import asyncio
from collections import defaultdict
import json
import threading
import uvicorn
import time
from fastapi import APIRouter, FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from queue import Queue
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset, AssetAttribute

class OpenFactoryAPI(OpenFactoryApp):
    """OpenFactory API class to handle device changes streaming."""

    def __init__(self, app_uuid, ksqlClient, bootstrap_servers, loglevel='INFO'):
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        self.asset_uuid = "OFA-API"
        
        self.device_queues = defaultdict(Queue)
        
        self.app = FastAPI()
        self.router = APIRouter()
        self.setup_routes()
        self.app.include_router(self.router)
        
        self.ivac = Asset("IVAC",
                          ksqlClient=ksqlClient,
                          bootstrap_servers=bootstrap_servers)
        self.ivac.subscribe_to_events(self.on_event, 'api_events_group')
        self.running = True
        
    def setup_routes(self):
        """Setup FastAPI routes."""
        @self.router.get("/")
        async def root():
            return {"message": "OpenFactory API is running"}

        @self.router.get("/devices/{device_uuid}/stream")
        async def stream_devices_messages(request: Request, device_uuid: str):
            return EventSourceResponse(self.event_generator(request, device_uuid))
        
    async def event_generator(self, request: Request, device_uuid: str):
        """Generator function to yield events for a specific device."""
        queue = self.device_queues[device_uuid]
        while True:
            if await request.is_disconnected():
                break
            try:
                if not queue.empty():
                    change = queue.get()
                    yield {
                        "event": "device_change",
                        "data": json.dumps(dict(change))
                    }
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"Error in event generator: {e}")
                break

    def on_event(self, msg_key: str, msg_value: dict) -> None:
        """Handle device events."""
        try:
            device_uuid = msg_key
            msg_value['device_uuid'] = device_uuid
            self.device_queues[device_uuid].put(msg_value)
        except Exception as e:
            print(f"Error processing device event: {e}")

    def app_event_loop_stopped(self) -> None:
        """Called automatically when the main application event loop is stopped."""
        print("Stopping API consumer thread ...")
        self.running = False
        if hasattr(self, 'all_devices'):
            self.ivac.stop_events_subscription()

    def main_loop(self) -> None:
        """Main loop of the App."""
        print("Starting OpenFactory API main loop...")
        
        while self.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("Shutting down...")
                self.running = False
                break

def run_api():
    """Function to run the API server."""
    app_instance = OpenFactoryAPI(
        app_uuid='OFA-API',
        ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
        bootstrap_servers="broker:29092"
    )
    
    # Start the OpenFactory app in a separate thread
    def start_openfactory():
        try:
            app_instance.run()
        except Exception as e:
            print(f"Error in OpenFactory thread: {e}")
    
    openfactory_thread = threading.Thread(target=start_openfactory, daemon=True)
    openfactory_thread.start()
    
    time.sleep(2)
    
    print("Starting FastAPI server on 0.0.0.0:8000")
    
    # Run the FastAPI app
    try:
        uvicorn.run(app_instance.app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        app_instance.running = False

if __name__ == "__main__":
    run_api()