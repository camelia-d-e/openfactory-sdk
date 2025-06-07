import time
import random
import os
from mtcadapter.mtcdevices import MTCDevice
from mtcadapter.adapters import MTCAdapter


class Virtual_iVACToolPlus(MTCDevice):
    """
    Virtual adapter for iVAC Tool Plus, which detects current on any electrical powered device.
    """

    MIN_TOGGLE_TIME = float(os.environ.get("MIN_TOGGLE_TIME", 1))
    MAX_TOGGLE_TIME = float(os.environ.get("MAX_TOGGLE_TIME", 5))

    __state__ = 'ON'

    def read_data(self):
        time.sleep(round(random.uniform(self.MIN_TOGGLE_TIME, self.MAX_TOGGLE_TIME), 2))
        if self.__state__ == 'ON':
            self.__state__ = 'OFF'
        else:
            self.__state__ = 'ON'
        data = {'A1ToolPlus': self.__state__}
        return data


class Virtual_iVACToolPlusAdapter(MTCAdapter):
    device_class = Virtual_iVACToolPlus
    adapter_port = int(os.environ.get("ADAPTER_PORT", 7878))


def main():
    adapter = Virtual_iVACToolPlusAdapter()
    adapter.run()


if __name__ == "__main__":
    main()
