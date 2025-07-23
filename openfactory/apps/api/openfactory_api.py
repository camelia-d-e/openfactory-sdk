import asyncio
import json
import time
import threading
from collections import defaultdict
from queue import Queue
from typing import List, Dict, Set
import threading
import json
from typing import Dict

import websockets
from websockets.exceptions import ConnectionClosed

from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset

from topic_subscription import TopicSubscriber

class Command:
    def __init__(self, name: str, args):
        self.name = name
        self.args = args

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = defaultdict(set)
        self.connection_device_map: Dict[websockets.WebSocketServerProtocol, str] = {}
        self.outgoing_queues: Dict[websockets.WebSocketServerProtocol, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket, device_uuid: str):
        async with self._lock:
            self.active_connections[device_uuid].add(websocket)
            self.connection_device_map[websocket] = device_uuid
            self.outgoing_queues[websocket] = asyncio.Queue()

    async def disconnect(self, websocket):
        async with self._lock:
            if websocket in self.connection_device_map:
                device_uuid = self.connection_device_map[websocket]
                self.active_connections[device_uuid].discard(websocket)
                del self.connection_device_map[websocket]
                if websocket in self.outgoing_queues:
                    del self.outgoing_queues[websocket]

    async def send_to_device_connections(self, device_uuid: str, message: dict):
        if device_uuid in self.active_connections:
            connections_copy = self.active_connections[device_uuid].copy()
            for connection in connections_copy:
                if connection in self.outgoing_queues:
                    queue = self.outgoing_queues[connection]
                    try:
                        await queue.put(json.dumps(message))
                    except Exception as e:
                        print(f"Error queuing message for connection: {e}")
                        await self.disconnect(connection)

    def get_device_connection_count(self, device_uuid: str) -> int:
        return len(self.active_connections[device_uuid])

class OpenFactoryAPI(OpenFactoryApp):
    def __init__(self, app_uuid, ksqlClient, bootstrap_servers, loglevel='INFO'):
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        object.__setattr__(self, 'ASSET_ID', 'IVAC')
        self.device_queues = defaultdict(Queue)
        self.devices_assets = {}
        self.device_topics = {}
        self.ksqlClient = ksqlClient
        self.connection_manager = ConnectionManager()
        self.topic_subscriber = TopicSubscriber()
        self.running = True
        self.loop = None
        self.event_processing_task = None

    async def websocket_handler(self, websocket):
        """Handle incoming WebSocket connections."""
        path = websocket.request.path

        if path == "/ws/devices":
            await self.handle_devices_list_connection(websocket)
            return
        
        if not path.startswith("/ws/devices/"):
            await websocket.send(json.dumps({"event": "error", "message": "Invalid endpoint"}))
            await websocket.close()
            return
        
        device_uuid = path.split("/")[3]
        print(f"New WebSocket connection for device: {device_uuid}")

        await self.connection_manager.connect(websocket, device_uuid)

        if device_uuid not in self.devices_assets:
            try:
                self.devices_assets[device_uuid] = Asset(
                    device_uuid,
                    ksqlClient=self.ksqlClient,
                    bootstrap_servers="broker:29092"
                )

                device_stream_topic = self.create_device_stream(device_uuid)

                self.topic_subscriber.subscribe_to_kafka_topic(
                        topic=device_stream_topic,
                        kafka_group_id=f'api_device_stream_group_{device_uuid}',
                        on_message=self.on_message,
                        message_filter=lambda key: key == device_uuid
                    )
                self.device_topics[device_uuid] = device_stream_topic

                print(f"Initialized asset subscription for device: {device_uuid}")
            except Exception as e:
                print(f"Error initializing asset for {device_uuid}: {e}")

        try:
            initial_data = {
                "event": "connection_established",
                "device_uuid": device_uuid,
                "timestamp": time.time(),
                "data_items": self.get_device_dataitems(device_uuid),
                "connection_count": self.connection_manager.get_device_connection_count(device_uuid)
            }
            await websocket.send(json.dumps(initial_data))

            async def sender():
                """Handle outgoing messages to client"""
                if websocket not in self.connection_manager.outgoing_queues:
                    return
                
                queue = self.connection_manager.outgoing_queues[websocket]
                try:
                    while True:
                        try:
                            msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                            await websocket.send(msg)
                        except asyncio.TimeoutError:
                            ping_msg = {
                                "event": "ping",
                                "timestamp": time.time()
                            }
                            await websocket.send(json.dumps(ping_msg))
                        except ConnectionClosed:
                            break
                        except Exception as e:
                            print(f"Error sending message: {e}")
                            break
                except ConnectionClosed:
                    pass
                except Exception as e:
                    print(f"Sender coroutine error: {e}")

            async def receiver():
                """Handle incoming messages from client"""
                try:
                    while True:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                            try:
                                parsed_message = json.loads(message)
                                await self.handle_client_message(device_uuid, parsed_message, websocket)
                            except json.JSONDecodeError as e:
                                error_msg = {
                                    "event": "error",
                                    "message": f"Invalid JSON: {str(e)}"
                                }
                                await websocket.send(json.dumps(error_msg))
                        except asyncio.TimeoutError:
                            continue
                        except ConnectionClosed:
                            print("WebSocket disconnected in receiver")
                            break
                        except Exception as e:
                            print(f"Error in receiver: {e}")
                            break
                except Exception as e:
                    print(f"Receiver coroutine error: {e}")

            await asyncio.gather(sender(), receiver(), return_exceptions=True)
        except Exception as e:
            print(f"WebSocket handler error: {e}")
        finally:
            await self.connection_manager.disconnect(websocket)

    async def setup_background_tasks(self):
        """Setup background task for processing device events"""
        async def process_device_events():
            while self.running:
                try:
                    for device_uuid, queue in self.device_queues.items():
                        if not queue.empty():
                            change = queue.get()
                            message = {
                                "asset_uuid": device_uuid,
                                "data": dict(change)
                            }

                            await self.connection_manager.send_to_device_connections(device_uuid, message)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error in background event processing: {e}")
                    await asyncio.sleep(1)
        
        self.event_processing_task = asyncio.create_task(process_device_events())

    def create_device_stream(self, device_uuid: str) -> str:
        """Create a stream for the device to receive updates"""
        try:
            query = (
                f"CREATE STREAM IF NOT EXISTS device_stream_{device_uuid} "
                f"WITH (KAFKA_TOPIC='{device_uuid}_monitoring', PARTITIONS=1) AS "
                f"SELECT ASSET_UUID AS KEY, ID, VALUE, TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP "
                f"FROM ASSETS_STREAM WHERE ASSET_UUID = '{device_uuid}' "
                f"AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' "
                f"EMIT CHANGES;"
            )
            self.ksqlClient.statement_query(query)
            return f'{device_uuid}_monitoring'
        except Exception as e:
            print(f"Error creating stream for {device_uuid}: {e}")

    def drop_stream(self, device_uuid: str) -> None:
        """Drop stream associated to a specific device."""
        try:
            query = "DROP STREAM IF EXISTS device_stream_{device_uuid};"
            self.ksqlClient.statement_query(query)
        except Exception as e:
            print(f"Error dropping stream for {device_uuid}: {e}")

    def get_all_devices(self) -> List[str]:
        try:
            query = "SELECT ASSET_UUID FROM assets_type WHERE TYPE = 'Device';"
            df = self.ksqlClient.query(query)
            return df.ASSET_UUID.tolist() if 'ASSET_UUID' in df.columns else []
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def get_device_dataitems(self, device_uuid: str) -> dict:
        try:
            query = (
                f"SELECT ID, VALUE FROM assets WHERE ASSET_UUID = '{device_uuid}' "
                f"AND TYPE IN ('Events', 'Condition') AND VALUE != 'UNAVAILABLE';"
            )
            df = self.ksqlClient.query(query)
            return dict(zip(df.ID.tolist(), df.VALUE.tolist())) if 'ID' in df.columns and 'VALUE' in df.columns else {}
        except Exception as e:
            print(f"Error getting device dataitems for {device_uuid}: {e}")
            return {}

    def get_dataitem_stats(self, dataitem_id) -> dict:
        try:
            query = (
                f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC FROM IVAC_POWER_STATE_TOTALS "
                f"WHERE IVAC_POWER_KEY LIKE '{dataitem_id}%';"
            )
            df = self.ksqlClient.query(query)
            return dict(zip(df.IVAC_POWER_KEY.str[11:].tolist(), df.TOTAL_DURATION_SEC.tolist())) if 'IVAC_POWER_KEY' in df.columns and 'TOTAL_DURATION_SEC' in df.columns else {}
        except Exception:
            print("Error getting dataitems stats")
            return {}

    async def handle_client_message(self, device_uuid: str, message: dict, websocket):
        """Handle incoming messages from clients."""
        try:
            print(f"Received message from {device_uuid}: {message}")
            
            if message.get("method") == "simulation_mode":
                params = message.get("params", {})
                name = params.get("name")
                args = params.get("args")
                
                self.method(name, str(args).lower())
                print(f'Sent to CMD_STREAM: SimulationMode with value {str(args).lower()}')
                
                await websocket.send(json.dumps({
                    "event": "simulation_mode_updated",
                    "success": True,
                    "value": args
                }))
            elif message.get("action") == "drop":
                device_uuid = message.get("asset_uuid")
                self.drop_stream(device_uuid)

                await websocket.send(json.dumps({
                    "event": "stream_dropped",
                    "success": True
                }))
            else:
                await websocket.send(json.dumps({"error": "Unknown method"}))
        
        except Exception as e:
            print(f"Error handling client message: {e}")
            await websocket.send(json.dumps({
                "event": "simulation_mode_updated",
                "success": False,
                "error": str(e)
            }))

    async def handle_devices_list_connection(self, websocket):
        """Handle connections to the /ws/devices endpoint"""
        try:
            devices = self.get_all_devices()
            device_list = []
            for device in devices:
                device_list.append({
                    "device_uuid": device,
                    "dataitems": self.get_device_dataitems(device),
                    "durations": self.get_dataitem_stats(device),
                    "connections": self.connection_manager.get_device_connection_count(device)
                })
            
            initial_data = {
                "event": "devices_list",
                "timestamp": time.time(),
                "devices": device_list
            }
            await websocket.send(json.dumps(initial_data))
            
            while True:
                try:
                    await asyncio.sleep(30)
                    ping_msg = {
                        "event": "ping",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(ping_msg))
                except ConnectionClosed:
                    break
                    
        except Exception as e:
            print(f"Error in devices list connection: {e}")
        finally:
            await websocket.close()

    def on_message(self, msg_key: str, msg_value: dict) -> None:
        try:
            device_uuid = msg_key
            if(device_uuid == 'IVAC'):
                self.add_duration_updates(msg_value)
            self.device_queues[device_uuid].put(msg_value)
        except Exception as e:
            print(f"Error processing device event: {e}")

    def add_duration_updates(self, msg_value):
        query = (
            f"SELECT IVAC_POWER_KEY, TOTAL_DURATION_SEC FROM IVAC_POWER_STATE_TOTALS "
            f"WHERE IVAC_POWER_KEY LIKE '{msg_value['ID']}%';"
        )
        df = self.ksqlClient.query(query)
        msg_value['durations'] = dict(zip(df.IVAC_POWER_KEY.str[11:].tolist(), df.TOTAL_DURATION_SEC.tolist())) if 'IVAC_POWER_KEY' in df.columns and 'TOTAL_DURATION_SEC' in df.columns else {}

    async def app_event_loop_stopped(self) -> None:
        print("Stopping API consumer thread...")
        self.running = False
        
        if self.event_processing_task and not self.event_processing_task.done():
            self.event_processing_task.cancel()
            try:
                await self.event_processing_task
            except asyncio.CancelledError:
                pass
        
        for device_uuid, asset in self.devices_assets.items():
            try:
                asset.stop_events_subscription()
                print(f"Stopped subscription for device: {device_uuid}")
            except Exception as e:
                print(f"Error stopping subscription for {device_uuid}: {e}")

    def main_loop(self) -> None:
        print("Starting OpenFactory WebSocket API main loop...")
        while self.running:
            try:
                total_connections = sum(
                    len(connections) for connections in self.connection_manager.active_connections.values()
                )
                if total_connections > 0:
                    print(
                        f"Active WebSocket connections: {total_connections} "
                        f"across {len(self.connection_manager.active_connections)} devices"
                    )
                time.sleep(30)
            except KeyboardInterrupt:
                print("Shutting down WebSocket API...")
                self.running = False
                break

def run_websocket_api():
    """Main function to run the WebSocket API"""
    app_instance = OpenFactoryAPI(
        app_uuid='OFA-API',
        ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
        bootstrap_servers="broker:29092"
    )

    def start_openfactory():
        try:
            app_instance.run()
        except Exception as e:
            print(f"Error in OpenFactory thread: {e}")

    openfactory_thread = threading.Thread(target=start_openfactory, daemon=True)
    openfactory_thread.start()
    time.sleep(3)

    print("Starting WebSocket API server on 0.0.0.0:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")

    async def main():
        await app_instance.setup_background_tasks()
        
        try:
            async with websockets.serve(
                app_instance.websocket_handler, 
                "0.0.0.0", 
                8000,
                ping_interval=30,
                ping_timeout=10
            ):
                await asyncio.Future()
        except Exception as e:
            print(f"Error starting WebSocket server: {e}")
            app_instance.running = False
        finally:
            await app_instance.app_event_loop_stopped()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down WebSocket API...")
        app_instance.running = False

if __name__ == "__main__":
    run_websocket_api()