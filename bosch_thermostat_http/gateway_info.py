"""Gateway info module retrieving basic information from Bosch thermostat."""
from .const import (GATEWAY_PATH_LIST, GET)
from .helper import BoschSingleEntity


class GatewayInfo(BoschSingleEntity):
    """Gateway info gets UUID, FIRMWARE_VERSION and HARDWARE_VERSION. """
    def __init__(self, requests, name, restoring_data=None):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._data = {}
        for key in GATEWAY_PATH_LIST:
            self._data[key] = None
        super().__init__(name, restoring_data, self._data)
        self._requests = requests

    async def update(self):
        """ Update data of thermostat asynchronously. """
        for key in self._data:
            result = await self._requests[GET](GATEWAY_PATH_LIST[key])
            self._data[key] = result['value']
