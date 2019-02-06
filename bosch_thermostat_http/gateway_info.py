"""Gateway info module retrieving basic information from Bosch thermostat."""
from .const import (FIRMWARE_VERSION, GATEWAY_PATH_LIST, HARDWARE_VERSION,
                    UUID, GET)
from .helper import BoschSingleEntity


class GatewayInfo(BoschSingleEntity):
    """Gateway info gets UUID, FIRMWARE_VERSION and HARDWARE_VERSION. """
    def __init__(self, requests, name, restoring_data=None):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._data = {
            UUID: None,
            FIRMWARE_VERSION: None,
            HARDWARE_VERSION: None
        }
        super().__init__(name, restoring_data, self._data)
        self._requests = requests

    async def update(self):
        """ Update data of thermostat asynchronously. """
        for key in self._data:
            result = await self._requests[GET](GATEWAY_PATH_LIST[key])
            self._data[key] = result['value']
