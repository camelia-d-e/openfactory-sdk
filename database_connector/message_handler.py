from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DeviceMessage:
    """Represents a device update message"""
    asset_uuid: str
    dataitem_id: str
    value: Any
    timestamp: datetime

class MessageHandler:
    """
    Handles routing of WebSocket messages to appropriate database operations
    """
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.subscribed_devices: Dict[str, Dict] = {}
    
    def handle_message(self, raw_message: str):
        """
        Main message handler - routes incoming WebSocket messages to appropriate actions
        """
        try:
            message_data = json.loads(raw_message)

            if message_data.get('event', '') == "device_change":
                device_message = self.parse_device_message(message_data)
                print(f"Received update for device {device_message.asset_uuid} : ({device_message.dataitem_id}, {device_message.value})")
                variable_id = self.db_manager.fetch_variable_id(device_message.asset_uuid, device_message.dataitem_id)
                datatype = self.db_manager.fetch_type(variable_id)
                if datatype == "EquipmentMode" or datatype == "DoorStatus":
                    self.db_manager.insert_strvalue(variable_id, device_message.value, device_message.timestamp)

        except Exception as e:
            print(f"Error handling message: {e}")
    
    def parse_device_message(self, message_data: Dict) -> Optional[DeviceMessage]:
        """Parse raw message data into DeviceMessage object"""
        try:
            asset_uuid = message_data.get('asset_uuid')
            dataitem_id = message_data.get('data').get('id')
            value = message_data.get('data').get('value')
            timestamp_str = message_data.get('data').get('attributes').get('timestamp')
            
            timestamp = timestamp_str[:-1] if timestamp_str.endswith('Z') else timestamp_str
            
            return DeviceMessage(
                asset_uuid=asset_uuid,
                dataitem_id=dataitem_id,
                value=value,
                timestamp=timestamp,
            )
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None
    