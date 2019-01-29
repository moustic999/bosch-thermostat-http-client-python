from .const import (FIRMWARE_VERSION, HARDWARE_VERSION, UUID,
                    GATEWAY_PATH_LIST)


class GatewayInfo:

    def __init__(self, get_request):
        self._data = {
            UUID: None,
            FIRMWARE_VERSION: None,
            HARDWARE_VERSION: None
        }
        self._get_request = get_request

    def get_property(self, property_name):
        if property_name in self._data:
            return self._data[property_name]
        return None

    async def update(self):
        for key in self._data:
            result = await self._get_request(GATEWAY_PATH_LIST[key])
            self._data[key] = result['value']
