import time
import random
import os
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.adapters import MTCAdapter

class Virtual_iVACToolPlus(MTCDevice):
    """
    Virtual adapter for iVAC Tool Plus, which detects current on any electrical powered device.
    """

    MIN_TOGGLE_TIME = float(os.environ.get("MIN_TOGGLE_TIME", 5))
    MAX_TOGGLE_TIME = float(os.environ.get("MAX_TOGGLE_TIME", 10))
    MAX_SPINDLE_SPEED = 25000.0
    MIN_SPINDLE_SPEED = 10000.0

    def __init__(self):
        self._spindle_speed = 0
        self._vacuum_status = ''

    def read_data(self) -> dict:
        """Read and toggle tool states with random delay"""
        time.sleep(round(random.uniform(self.MIN_TOGGLE_TIME, self.MAX_TOGGLE_TIME), 2))
        self.spindle_speed = random.randint(self.MIN_SPINDLE_SPEED, self.MAX_SPINDLE_SPEED)
        if self.actuator_state == 'ACTIVE':
            self.actuator_state = 'INACTIVE'
        else:
            self.actuator_state = 'ACTIVE'
        return {
            'SpindleSpeed': self.spindle_speed,
            'VacuumSystem': self.actuator_state
        }


class Virtual_iVACToolPlusAdapter(MTCAdapter):
    device_class = Virtual_iVACToolPlus
    adapter_port = int(os.environ.get("ADAPTER_PORT", 7878))

    def __init__(self):
        super().__init__()
        self.opcua_server = None
        self.device = self.device_class()

    def run(self):
        """Start both MTConnect server"""
        print("Starting MTConnect adapter...")
        super().run()


def main():
    adapter = Virtual_iVACToolPlusAdapter()
    adapter.run()


if __name__ == "__main__":
    main()
