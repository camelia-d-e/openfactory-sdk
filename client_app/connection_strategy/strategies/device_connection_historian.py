from typing import Dict, List

from ..interfaces.device_connection_strategy import IDeviceConnectionStrategy

class DeviceConnectionHistorian(IDeviceConnectionStrategy):
    """Manages device connection using a historian database."""

    def __init__(self, connection_string: str, database: str):
        self.connection_string = connection_string
        self.database = database

    async def fetch_devices(self) -> None:
        pass

    async def fetch_device_dataitems(self, device_uuid: str) -> None:
        pass
    
    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> None:
        pass
    
    async def set_simulation_mode(self, simulation_mode: bool) -> None:
        pass

    def format_device_data(self, device_data: dict) -> List[Dict[str, any]]:
        pass

    def supports_native_websocket(self) -> bool:
        return False

