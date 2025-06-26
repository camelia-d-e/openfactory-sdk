import os
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from device_connection_manager import DeviceConnectionManager

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class OpenFactoryClientApp:
    """Client app for openfactory API"""

    def __init__(self, api_base_url):
        self.device_manager = DeviceConnectionManager(api_base_url)
        self.api_base_url = api_base_url

    async def startup_event(self):
        await self.device_manager.fetch_devices()
        for device in self.device_manager.devices:
            uuid = device['device_uuid']
            await self.device_manager.fetch_device_dataitems(uuid)
        for device in self.device_manager.devices:
            for dataitem in self.device_manager.device_dataitems:
                await self.device_manager.fetch_dataitem_stats(uuid, dataitem)

    async def index(self, request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": self.device_manager.devices,
                "device": self.device_manager.device_dataitems
            }
        )

    async def device_detail(self, request: Request, device_uuid: str):
        dataitems = self.device_manager.device_dataitems.get(device_uuid, {})
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "devices": self.device_manager.devices,
                "device_uuid": device_uuid,
                "device_dataitems": dataitems
            }
        )
    
    async def set_simulation_mode(self, simulation_mode: bool):
        return await self.device_manager.set_simulation_mode(simulation_mode)
   
templates = Jinja2Templates(directory="templates")
ofc_app = OpenFactoryClientApp(API_BASE_URL)

@asynccontextmanager
async def lifespan(app):
    await ofc_app.startup_event()
    yield

app = FastAPI(title="OpenFactory Client App", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return await ofc_app.index(request)

@app.get("/devices/{device_uuid}", response_class=HTMLResponse)
async def device_detail(request: Request, device_uuid: str):
    return await ofc_app.device_detail(request, device_uuid)

@app.post("/simulation-mode")
async def set_simulation_mode(request: Request):
    data = await request.json()
    simulation_mode = data.get("enabled", False)
    
    return await ofc_app.set_simulation_mode(simulation_mode)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3000,
        reload=True
        )