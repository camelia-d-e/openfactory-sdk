from typing import Dict, List
import httpx
from ..interfaces.device_connection_strategy import IDeviceConnectionStrategy


class DeviceConnectionAPI(IDeviceConnectionStrategy):
    """Manages device info connection."""

    def __init__(self, api_base_url: str):
        self.api_base_url: str = api_base_url

    async def fetch_devices(self) -> List[Dict[str, any]]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices")
                resp.raise_for_status()
                devices = resp.json().get("devices", [])
                return devices
        except Exception as e:
            print(f"Error fetching devices: {str(e)}")
            return []

    async def fetch_device_dataitems(self, device_uuid: str) -> List[Dict[str, any]]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices/{device_uuid}/dataitems")
                resp.raise_for_status()
                return self.format_device_data(resp.json())
        except Exception as e:
            print(f"Error fetching dataitems for {device_uuid}: {str(e)}")
            return []

    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> Dict[str, any]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices/{device_uuid}/dataitems/{dataitem_id}")
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            print(f"Error fetching stats for {dataitem_id}: {str(e)}")
            return {}

    async def set_simulation_mode(self, simulation_mode: bool) -> Dict[str, any]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_base_url}/simulation-mode",
                    json={"name": "SimulationMode",
                          "args": simulation_mode}
                )
                resp.raise_for_status()
                return {"status": "success"}
        except Exception as e:
            print(f"Error setting simulation mode: {str(e)}")
            return {"status": "error", "message": str(e)}

    def format_device_data(self, device_data: dict) -> List[Dict[str, any]]:
        device_dataitems = []
        for id, value in device_data.get('data_items', {}).items():
            if 'Tool' in id:
                device_dataitems.append({'id': id, 'value': value, 'type': 'tool'})
            elif 'Gate' in id:
                device_dataitems.append({'id': id, 'value': value, 'type': 'gate'})
            else:
                device_dataitems.append({'id': id, 'value': value, 'type': 'condition'})
        return device_dataitems

    def supports_native_websocket(self) -> bool:
        """OpenFactory supports native WebSocket connections"""
        return True

    def get_websocket_url(self, device_uuid: str) -> str:
        """Return the OpenFactory WebSocket URL"""
        return f"ws://localhost:8000/devices/{device_uuid}/ws"

    async def start_realtime_updates(self, device_uuid: str):
        pass

    async def stop_realtime_updates(self, device_uuid: str):
        """Stop OpenFactory WebSocket connection"""
        pass
