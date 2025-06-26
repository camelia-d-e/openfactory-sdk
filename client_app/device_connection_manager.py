from typing import Dict, List
import httpx


class DeviceConnectionManager:
    """Manages device info connection."""

    def __init__(self, api_base_url: str):
        self.api_base_url: str = api_base_url
        self.devices: List[Dict[str, any]] = []
        self.device_dataitems: Dict[str, List[Dict[str, any]]] = {}
        self.device_dataitems_stats: Dict[str, any] = {}

    async def fetch_devices(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices")
                resp.raise_for_status()
                self.devices = resp.json().get("devices", [])
        except Exception as e:
            print(f"Error fetching devices: {str(e)}")
            self.devices = []
    
    async def fetch_device_dataitems(self, device_uuid: str) -> None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices/{device_uuid}/dataitems")
                resp.raise_for_status()
                self.device_dataitems[device_uuid] = self.format_device_data(resp.json())

        except Exception as e:
            print(f"Error fetching dataitems for {device_uuid}: {str(e)}")
            self.device_dataitems[device_uuid] = []
    
    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.api_base_url}/devices/{device_uuid}/dataitems/{dataitem_id}")
                resp.raise_for_status()
                self.device_dataitems_stats[dataitem_id] = resp.json()

        except Exception as e:
            print(f"Error fetching stats for {dataitem_id}: {str(e)}")

    async def set_simulation_mode(self, simulation_mode: bool) -> None:
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
                elif '':
                    device_dataitems.append({'id': id, 'value': value, 'type': 'condition'})
        return device_dataitems