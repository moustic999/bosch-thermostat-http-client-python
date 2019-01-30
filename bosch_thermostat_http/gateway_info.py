"""Gateway info module retrieving basic information from Bosch thermostat."""
from .const import FIRMWARE_VERSION, GATEWAY_PATH_LIST, HARDWARE_VERSION, UUID


class GatewayInfo:
    """Gateway info gets UUID, FIRMWARE_VERSION and HARDWARE_VERSION. """
    def __init__(self, get_request):
        """
        :param obj get_request:    Pass get_request function to retrieve data.
        """
        self._data = {
            UUID: None,
            FIRMWARE_VERSION: None,
            HARDWARE_VERSION: None
        }
        self._get_request = get_request

    def get_property(self, property_name):
        """ Return property to parent module. """
        if property_name in self._data:
            return self._data[property_name]
        return None

    async def update(self):
        """ Update data of thermostat asynchronously. """
        for key in self._data:
            result = await self._get_request(GATEWAY_PATH_LIST[key])
            self._data[key] = result['value']
