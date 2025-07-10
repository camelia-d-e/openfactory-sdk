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
        async with websockets.connect(f"{self.base_url}/ws/devices") as ws:
            message = await ws.recv()
            data = json.loads(message)
            
            if data.get("event") == "devices_list":
                for device in data.get("devices", []):
                    self.devices[device["device_uuid"]] = {
                        "device_uuid": device["device_uuid"],
                        "dataitems": self.format_device_data(device.get("dataitems", {})),
                        "stats": device.get("durations", {})
                    }
                print(f"Got initial device list: {len(self.devices)} device(s)")
            return self.devices
    
    def format_device_data(self, device_data: dict) -> List[Dict[str, any]]:
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
    
    async def stream_device_updates(self, device_uuid: str):
        """Stream updates to frontend"""
        async with websockets.connect(f"{API_BASE_URL}/ws/devices/{device_uuid}") as ws:
            while True:
                try:
                    data = await ws.recv()
                    yield f"data: {data}\n\n"
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed, reconnecting...")
                    await asyncio.sleep(1)
                    break
    
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

@app.get("/updates/{device_uuid}")
async def stream_updates(device_uuid: str):
    """SSE endpoint for real-time updates"""
    return StreamingResponse(
        ofc_app.stream_device_updates(device_uuid),
        media_type="text/event-stream",
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)