
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class IDeviceConnectionStrategy(ABC):
    """Abstract base class for different data connection strategies"""
    
    @abstractmethod
    async def fetch_devices(self) -> List[Dict[str, Any]]:
        """Fetch all available devices"""
        pass
    
    @abstractmethod
    async def fetch_device_dataitems(self, device_uuid: str) -> List[Dict[str, Any]]:
        """Fetch data items for a specific device"""
        pass
    
    @abstractmethod
    async def fetch_dataitem_stats(self, device_uuid: str, dataitem_id: str) -> Dict[str, Any]:
        """Fetch statistics for a specific data item"""
        pass
    
    @abstractmethod
    async def set_simulation_mode(self, simulation_mode: bool) -> Dict[str, Any]:
        """Set simulation mode"""
        pass

    @abstractmethod
    async def start_realtime_updates(self, device_uuid: str):
        """Start real-time updates for a specific device"""
        pass
    
    @abstractmethod
    async def stop_realtime_updates(self, device_uuid: str):
        """Stop real-time updates for a specific device"""
        pass
    
    @abstractmethod
    def supports_native_websocket(self) -> bool:
        """Return True if this strategy supports native WebSocket connections"""
        return False
    
    def get_websocket_url(self, device_uuid: str) -> str:
        """Return WebSocket URL for strategies that support native WebSocket"""
        return None
    
    async def start_realtime_updates(self, device_uuid: str):
        """Start real-time updates for strategies that need server-side polling"""
        pass
    
    async def stop_realtime_updates(self, device_uuid: str):
        """Stop real-time updates for strategies that need server-side polling"""
        pass