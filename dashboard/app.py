import os
import json
import uvicorn
import websockets
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Any
import asyncio

API_BASE_URL = os.getenv("API_BASE_URL", "ws://ofa-api:8000")
templates = Jinja2Templates(directory="templates")

class OpenFactoryWebSocketClient:
    def __init__(self, base_url: str = "ws://ofa-api:8000"):
        self.base_url = base_url
        self.devices: Dict[str, Dict[str, Any]] = {}

    async def connect_to_devices_list(self):
        """Connect to the main devices list endpoint"""
        try:
            async with websockets.connect(f"{self.base_url}/ws/devices") as ws:
                message = await ws.recv()
                data = json.loads(message)
                print(data)
                
                if data.get("event", "") == "devices_list":
                    for device in data.get("devices", []):
                        self.devices[device["device_uuid"]] = {
                            "device_uuid": device["device_uuid"],
                            "dataitems": self.format_device_data(device.get("dataitems", {})),
                            "stats": device.get("durations", {})
                        }
                    print(f"Got initial device list: {len(self.devices)} device(s)")
                return self.devices
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
            raise HTTPException(status_code=500, detail="WebSocket connection error")
    
    def format_device_data(self, device_data: dict) -> List[Dict[str, Any]]:
        device_dataitems = []
        for id, value in device_data.items():
            if 'Tool' in id:
                device_dataitems.append({'id': id, 'value': value, 'type': 'tool'})
            elif 'Gate' in id:
                device_dataitems.append({'id': id, 'value': value, 'type': 'gate'})
            else:
                device_dataitems.append({'id': id, 'value': value, 'type': 'condition'})
        return device_dataitems

class OpenFactoryClientApp:
    def __init__(self, websocket_base_url: str = "ws://ofa-api:8000"):
        self.client = OpenFactoryWebSocketClient(websocket_base_url)
        self._startup_complete = False
        self.active_connections = {}
        self.output_queue = asyncio.Queue()
        self.device_queues: Dict[str, asyncio.Queue] = {}
    
    async def startup_event(self):
        """Initialize the app by fetching devices and their data"""
        if self._startup_complete:
            return
            
        print("Starting OpenFactory client initialization...")
        try:
            await self.client.connect_to_devices_list()
            self._startup_complete = True
            print("OpenFactory client initialization complete!")
        except Exception as e:
            print(f"Error during startup: {e}")
            raise

    async def device_listener(self, device_uuid: str):
                """Listen to a specific device and put updates in the output queue"""
                retry_count = 0
                max_retries = 5
                
                while retry_count < max_retries:
                    try:
                        async with websockets.connect(f"{API_BASE_URL}/ws/devices/{device_uuid}") as ws:
                            retry_count = 0
                            while True:
                                try:
                                    data = await ws.recv()
                                    parsed_data = json.loads(data)
                                    parsed_data["device_uuid"] = device_uuid
                                    print(parsed_data)
                                    await self.output_queue.put(parsed_data)
                                except websockets.exceptions.ConnectionClosed:
                                    print(f"Connection closed for device {device_uuid}, reconnecting...")
                                    break
                                except json.JSONDecodeError as e:
                                    print(f"JSON decode error for device {device_uuid}: {e}")
                                    continue
                    except Exception as e:
                        retry_count += 1
                        print(f"Error in device listener for {device_uuid} (attempt {retry_count}): {e}")
                        if retry_count < max_retries:
                            await asyncio.sleep(min(2 ** retry_count, 30))
                        else:
                            print(f"Max retries reached for device {device_uuid}, giving up")
                            break
    
    async def stream_all_device_updates(self):
        """Stream updates for all devices"""
        try:
            if not self._startup_complete:
                await self.startup_event()
            
            if not self.client.devices:
                while True:
                    yield f"data: {json.dumps({'event': 'ping'})}\n\n"
                    await asyncio.sleep(30)
            
            device_tasks = []

            for device_uuid in self.client.devices.keys():
                task = asyncio.create_task(self.device_listener(device_uuid))
                device_tasks.append(task)
            
            last_ping = asyncio.get_event_loop().time()
            while True:
                try:
                    try:
                        data = await asyncio.wait_for(self.output_queue.get(), timeout=1.0)
                        yield f"data: {json.dumps(data)}\n\n"
                    except asyncio.TimeoutError:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_ping > 30:
                            yield f"data: {json.dumps({'event': 'ping'})}\n\n"
                            last_ping = current_time
                    
                except Exception as e:
                    print(f"Error in main update loop: {e}")
                    yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"Fatal error in stream_all_device_updates: {e}")
            yield f"data: {json.dumps({'event': 'error', 'message': f'Fatal error: {str(e)}'})}\n\n"
        
        for device_uuid in self.client.devices.keys():
            queue = asyncio.Queue()
            if device_uuid not in self.device_queues:
                self.device_queues[device_uuid] = queue
                asyncio.create_task(self.device_listener(device_uuid))
            
        while True:
            try:
                for device_uuid, queue in self.device_queues.items():
                    try:
                        data = queue.get_nowait()
                        yield f"data: {json.dumps(data)}\n\n"
                    except asyncio.QueueEmpty:
                        continue
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error in main update loop: {e}")
                await asyncio.sleep(1)
    
    async def device_detail(self, request: Request, device_uuid: str):
        """Render device detail page with SSE endpoint"""
        if not self._startup_complete:
            await self.startup_event()
        
        if device_uuid not in self.client.devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": list(self.client.devices.keys()),
                "device_uuid": device_uuid,
                "device_dataitems": self.client.devices[device_uuid].get("dataitems", []),
                "dataitems_stats": self.client.devices[device_uuid].get("stats", []),
            }
        )

ofc_app = OpenFactoryClientApp(API_BASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await ofc_app.startup_event()
    yield

app = FastAPI(title="OpenFactory Client App", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if not ofc_app._startup_complete:
        await ofc_app.startup_event()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": list(ofc_app.client.devices.keys()),
            "device": {}
        }
    )

@app.get("/devices/{device_uuid}", response_class=HTMLResponse)
async def device_detail(request: Request, device_uuid: str):
    return await ofc_app.device_detail(request, device_uuid)

@app.get("/updates/all")
async def stream_updates():
    """SSE endpoint for real-time updates"""
    return StreamingResponse(
        ofc_app.stream_all_device_updates(),
        media_type="text/event-stream",
    )


@app.post("/simulation-mode/{device_uuid}")
async def set_simulation_mode(device_uuid: str, request: Request):
    try:
        data = await request.json()
        simulation_mode = data.get("enabled", False)
        
        async with websockets.connect(f"{API_BASE_URL}/ws/devices/{device_uuid}") as ws:
            await ws.send(json.dumps({
                "method": "simulation_mode",
                "params": {
                    "name": "SimulationMode",
                    "args": simulation_mode
                }
            }))
            response = await ws.recv()
            return json.loads(response)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)