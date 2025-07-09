from connection_strategy.interfaces.device_connection_strategy import IDeviceConnectionStrategy
from connection_strategy.strategies.device_connection_historian import DeviceConnectionHistorian
from connection_strategy.strategies.device_connection_api import DeviceConnectionAPI


class ConnectionStrategyFactory:
    """Factory class to create connection strategies based on type"""

    @staticmethod
    def create_strategy(strategy_type: str, config: dict) -> IDeviceConnectionStrategy:
        """Create a connection strategy based on the provided type"""
        if strategy_type == 'api':
            return DeviceConnectionAPI(api_base_url=config['api_base_url'])
        elif strategy_type == 'historian':
            return DeviceConnectionHistorian(
                connection_string=config['connection_string'],
                database=config['database']
            )
