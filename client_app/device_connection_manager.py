from typing import Dict, List
import websockets
import httpx
import json
from fastapi.websockets import WebSocket

class DeviceConnectionManager:
    """Manages device info connection."""

    def __init__(self, api_base_url: str):
        self.api_base_url: str = api_base_url
        self.devices: List[Dict[str, any]] = []
        self.device_dataitems: Dict[str, List[Dict[str, any]]] = {}

    async def fetch_devices(self) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_base_url}/devices")
            resp.raise_for_status()
            self.devices = resp.json().get("devices", [])

    async def fetch_device_dataitems(self, device_uuid: str) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_base_url}/devices/{device_uuid}/dataitems")
            resp.raise_for_status()
            self.device_dataitems[device_uuid] = self.format_device_data(resp.json())

    def format_device_data(self, device_data: dict) -> dict:
        device_dataitems = []
        for id, value in device_data.get('data_items', {}).items():
                if 'Tool' in id:
                    device_dataitems.append({'id': id, 'value': value, 'type': 'tool'})
                elif 'Gate' in id:
                    device_dataitems.append({'id': id, 'value': value, 'type': 'gate'})
                else:
                    device_dataitems.append({'id': id, 'value': value, 'type': 'condition'})
        return device_dataitems