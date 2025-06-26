import asyncio
from collections import defaultdict
import json
import threading
from typing import List, Dict, Set
from pydantic import BaseModel
import uvicorn
import time
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from queue import Queue
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset

class Command(BaseModel):
    name: str
    args:  str | bool | None


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.connection_device_map: Dict[WebSocket, str] = {}
        self.outgoing_queues: Dict[WebSocket, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, device_uuid: str):
        await websocket.accept()
        async with self._lock:
            self.active_connections[device_uuid].add(websocket)
            self.connection_device_map[websocket] = device_uuid
            self.outgoing_queues[websocket] = asyncio.Queue()
        print(f"Client connected to device {device_uuid}. Total connections: {len(self.active_connections[device_uuid])}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.connection_device_map:
                device_uuid = self.connection_device_map[websocket]
                self.active_connections[device_uuid].discard(websocket)
                del self.connection_device_map[websocket]
                if websocket in self.outgoing_queues:
                    del self.outgoing_queues[websocket]
                print(f"Client disconnected from device {device_uuid}. Remaining connections: {len(self.active_connections[device_uuid])}")

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
        self.asset_uuid = "IVAC"
        self.device_queues = defaultdict(Queue)
        self.devices_assets = {}
        self.ksqlClient = ksqlClient
        self.connection_manager = ConnectionManager()
        self.app = FastAPI(title="OpenFactory WebSocket API", version="2.0.0")
        self.router = APIRouter()
        self.setup_routes(ksqlClient, bootstrap_servers)
        self.app.include_router(self.router)
        self.running = True
        self.loop = None
        self.event_processing_task = None

    def setup_routes(self, ksqlClient, bootstrap_servers):
        @self.router.get("/")
        async def root():
            return {
                "message": "OpenFactory WebSocket API is running",
                "version": "2.0.0",
                "websocket_endpoint": "/devices/{device_uuid}/ws",
            }

        @self.router.get("/devices")
        async def list_devices():
            devices = self.get_all_devices()
            device_status = []
            for device_uuid in devices:
                device_status.append({
                    "device_uuid": device_uuid,
                    "connections": self.connection_manager.get_device_connection_count(device_uuid)
                })
            return {
                "devices": device_status,
                "total_devices": len(devices)
            }

        @self.router.get("/devices/{device_uuid}/dataitems")
        async def get_device_dataitems_endpoint(device_uuid: str):
            return {
                "device_uuid": device_uuid,
                "data_items": self.get_device_dataitems(device_uuid),
            }
        
        @self.router.post("/simulation-mode")
        async def set_simulation_mode(simulation_mode: Command):
            self.method(simulation_mode.name, str(simulation_mode.args).lower())
            print(f'Sent to CMD_STREAM: SimulationMode with value {str(simulation_mode.args).lower()}')

        @self.router.websocket("/devices/{device_uuid}/ws")
        async def websocket_device_stream(websocket: WebSocket, device_uuid: str):
            await self.connection_manager.connect(websocket, device_uuid)
            
            if device_uuid not in self.devices_assets:
                try:
                    self.devices_assets[device_uuid] = Asset(
                        device_uuid,
                        ksqlClient=ksqlClient,
                        bootstrap_servers=bootstrap_servers
                    )
                    self.devices_assets[device_uuid].subscribe_to_events(
                        self.on_event, 
                        f'api_events_group_{device_uuid}'
                    )
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
                await websocket.send_text(json.dumps(initial_data))

                async def sender():
                    """Handle outgoing messages to client"""
                    if websocket not in self.connection_manager.outgoing_queues:
                        return
                    
                    queue = self.connection_manager.outgoing_queues[websocket]
                    try:
                        while websocket.client_state == WebSocketState.CONNECTED:
                            try:
                                msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                                if websocket.client_state == WebSocketState.CONNECTED:
                                    await websocket.send_text(msg)
                            except asyncio.TimeoutError:
                                if websocket.client_state == WebSocketState.CONNECTED:
                                    ping_msg = {
                                        "event": "ping",
                                        "timestamp": time.time()
                                    }
                                    await websocket.send_text(json.dumps(ping_msg))
                            except Exception as e:
                                print(f"Error sending message: {e}")
                                break
                    except Exception as e:
                        print(f"Sender coroutine error: {e}")

                async def receiver():
                    """Handle incoming messages from client"""
                    try:
                        while websocket.client_state == WebSocketState.CONNECTED:
                            try:
                                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                                try:
                                    parsed_message = json.loads(message)
                                    await self.handle_client_message(device_uuid, parsed_message)
                                except json.JSONDecodeError as e:
                                    error_msg = {
                                        "event": "error",
                                        "message": f"Invalid JSON: {str(e)}"
                                    }
                                    if websocket.client_state == WebSocketState.CONNECTED:
                                        await websocket.send_text(json.dumps(error_msg))
                            except asyncio.TimeoutError:
                                if websocket.client_state != WebSocketState.CONNECTED:
                                    break
                            except WebSocketDisconnect:
                                print("WebSocket disconnected in receiver")
                                break
                            except Exception as e:
                                print(f"Error in receiver: {e}")
                                break
                    except Exception as e:
                        print(f"Receiver coroutine error: {e}")

                await asyncio.gather(
                    sender(),
                    receiver(),
                    return_exceptions=True
                )
                    
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
                                "event": "device_change",
                                "device_uuid": device_uuid,
                                "timestamp": time.time(),
                                "data": dict(change)
                            }
                            await self.connection_manager.send_to_device_connections(device_uuid, message)
                    
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error in background event processing: {e}")
                    await asyncio.sleep(1)
        
        self.event_processing_task = asyncio.create_task(process_device_events())

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
            query = f"SELECT ID, VALUE FROM assets WHERE ASSET_UUID = '{device_uuid}' AND TYPE IN ('Events', 'Condition') AND VALUE != 'UNAVAILABLE';"
            df = self.ksqlClient.query(query)
            return dict(zip(df.ID.tolist(), df.VALUE.tolist())) if 'ID' in df.columns and 'VALUE' in df.columns else {}
        except Exception as e:
            print(f"Error getting device dataitems for {device_uuid}: {e}")
            return {}

    async def handle_client_message(self, device_uuid: str, message: dict):
        """Handle messages received from WebSocket clients"""
        try:
            print(f"Received message from {device_uuid}: {message}")

            if message.get("type") == "pong":
                pass
        except Exception as e:
            print(f"Error handling client message: {e}")

    def on_event(self, msg_key: str, msg_value: dict) -> None:
        try:
            device_uuid = msg_key
            msg_value['device_uuid'] = device_uuid
            self.device_queues[device_uuid].put(msg_value)
        except Exception as e:
            print(f"Error processing device event: {e}")

    async def app_event_loop_stopped(self) -> None:
        print("Stopping API consumer thread...")
        self.running = False
        
        # Cancel background task
        if self.event_processing_task and not self.event_processing_task.done():
            self.event_processing_task.cancel()
            try:
                await self.event_processing_task
            except asyncio.CancelledError:
                pass
        
        # Stop asset subscriptions
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
                total_connections = sum(len(connections) for connections in self.connection_manager.active_connections.values())
                if total_connections > 0:
                    print(f"Active WebSocket connections: {total_connections} across {len(self.connection_manager.active_connections)} devices")
                time.sleep(30)
            except KeyboardInterrupt:
                print("Shutting down WebSocket API...")
                self.running = False
                break

async def startup_event(app_instance):
    """Initialize async components when the FastAPI app starts"""
    app_instance.loop = asyncio.get_event_loop()
    await app_instance.setup_background_tasks()

def run_websocket_api():
    app_instance = OpenFactoryAPI(
        app_uuid='OFA-API',
        ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
        bootstrap_servers="broker:29092"
    )
    
    @app_instance.app.on_event("startup")
    async def startup():
        await startup_event(app_instance)
    
    @app_instance.app.on_event("shutdown")
    async def shutdown():
        await app_instance.app_event_loop_stopped()
    
    def start_openfactory():
        try:
            app_instance.run()
        except Exception as e:
            print(f"Error in OpenFactory thread: {e}")
    
    openfactory_thread = threading.Thread(target=start_openfactory, daemon=True)
    openfactory_thread.start()
    time.sleep(3)
    
    print("Starting WebSocket API server on 0.0.0.0:8000")
    print("WebSocket endpoint: ws://localhost:8000/devices/{device_uuid}/ws")
    
    try:
        uvicorn.run(
            app_instance.app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            ws_ping_interval=30,
            ws_ping_timeout=10
        )
    except Exception as e:
        print(f"Error starting WebSocket API server: {e}")
        app_instance.running = False

if __name__ == "__main__":
    run_websocket_api()