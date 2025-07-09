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
        _ = device_uuid
        pass

    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> None:
        _ = device_uuid
        _ = dataitem_id
        pass

    async def set_simulation_mode(self, simulation_mode: bool) -> None:
        _ = simulation_mode
        pass

    def format_device_data(self, device_data: dict) -> List[Dict[str, any]]:
        _ = device_data
        pass

    def supports_native_websocket(self) -> bool:
        return False
