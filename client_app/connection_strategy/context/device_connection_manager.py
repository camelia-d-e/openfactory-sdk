from typing import Dict, List, Any, Optional
from ..interfaces.device_connection_strategy import IDeviceConnectionStrategy

class DeviceConnectionManager:
    """
    Context class that manages device operations using the current connection strategy.
    Implements the main interface while delegating the actual work to the strategy.
    """
    
    def __init__(self, strategy: IDeviceConnectionStrategy):
        self._strategy = strategy
        self.devices: List[Dict[str, Any]] = []
        self.device_dataitems: Dict[str, List[Dict[str, Any]]] = {}
        self.dataitem_stats: Dict[str, Dict[str, Any]] = {}

    async def fetch_devices(self) -> List[Dict[str, Any]]:
        """Fetch and store devices using current strategy"""
        self.devices = await self._strategy.fetch_devices()
        return self.devices

    async def fetch_device_dataitems(self, device_uuid: str) -> List[Dict[str, Any]]:
        """Fetch and store data items for a device"""
        items = await self._strategy.fetch_device_dataitems(device_uuid)
        self.device_dataitems[device_uuid] = items
        return items
    
    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> Dict[str, Any]:
        """Fetch statistics for specific data item"""
        stats = await self._strategy.fetch_dataitem_stats(device_uuid, dataitem_id)
        if device_uuid not in self.dataitem_stats:
            self.dataitem_stats[device_uuid] = {}
        self.dataitem_stats[device_uuid][dataitem_id] = stats
        return stats
    
    async def set_simulation_mode(self, enabled: bool) -> Dict[str, Any]:
        """Enable/disable simulation mode"""
        return await self._strategy.set_simulation_mode(enabled)
    
    async def start_realtime_updates(self, device_uuid: str) -> None:
        """Start receiving realtime updates for a device"""
        if hasattr(self._strategy, 'start_realtime_updates'):
            await self._strategy.start_realtime_updates(device_uuid)
    
    async def stop_realtime_updates(self, device_uuid: str) -> None:
        """Stop receiving realtime updates for a device"""
        if hasattr(self._strategy, 'stop_realtime_updates'):
            await self._strategy.stop_realtime_updates(device_uuid)
    
    def get_websocket_url(self, device_uuid: str) -> Optional[str]:
        """Get websocket URL if strategy supports it"""
        if hasattr(self._strategy, 'get_websocket_url'):
            return self._strategy.get_websocket_url(device_uuid)
        return None
    
    def set_strategy(self, strategy: IDeviceConnectionStrategy) -> None:
        """Change the connection strategy at runtime"""
        self._strategy = strategy
        self.devices = []
        self.device_dataitems = {}
        self.dataitem_stats = {}
    
    @property
    def current_strategy_type(self) -> str:
        """Get the name of the current strategy"""
        return self._strategy.__class__.__name__