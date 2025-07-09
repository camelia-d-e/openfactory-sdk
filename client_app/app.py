import os
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from connection_strategy.context.device_connection_manager import DeviceConnectionManager
from connection_strategy_factory import ConnectionStrategyFactory
from typing import Dict, Any

CONNECTION_TYPE = os.getenv("CONNECTION_TYPE", "api")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

templates = Jinja2Templates(directory="templates")


def get_connection_config():
    """Get connection configuration based on environment variables"""
    if CONNECTION_TYPE == "api":
        return {'api_base_url': API_BASE_URL}
    elif CONNECTION_TYPE == "historian":
        return {
            'server_url': os.getenv("HISTORIAN_SERVER_URL", "http://historian.company.com"),
            'username': os.getenv("HISTORIAN_USERNAME", ""),
            'password': os.getenv("HISTORIAN_PASSWORD", ""),
            'connection_string': os.getenv("HISTORIAN_CONNECTION_STRING", ""),
            'database': os.getenv("HISTORIAN_DATABASE", "production")
        }
    else:
        return {'api_base_url': API_BASE_URL}


class OpenFactoryClientApp:
    """Client app for openfactory API with strategy pattern support"""

    def __init__(self, strategy_type: str = 'api', config: Dict[str, Any] = None):
        if config is None:
            config = {'api_base_url': API_BASE_URL}

        strategy = ConnectionStrategyFactory.create_strategy(strategy_type, config)
        self.device_manager = DeviceConnectionManager(strategy)
        self.config = config

    async def startup_event(self):
        await self.device_manager.fetch_devices()
        for device in self.device_manager.devices:
            uuid = device['device_uuid']
            await self.device_manager.fetch_device_dataitems(uuid)

        for device in self.device_manager.devices:
            for device_uuid, dataitems in self.device_manager.device_dataitems.items():
                for dataitem in dataitems:
                    await self.device_manager.fetch_dataitem_stats(device_uuid, dataitem['id'])

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


config = get_connection_config()
ofc_app = OpenFactoryClientApp(CONNECTION_TYPE, config)


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
