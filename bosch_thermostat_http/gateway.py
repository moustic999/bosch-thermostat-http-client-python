"""Gateway module connecting to Bosch thermostat."""
import json

import async_timeout
from aiohttp import client_exceptions

from .const import HTTP_HEADER, TIMEOUT, GET, SUBMIT, DHW, HC, GATEWAY, SENSORS
from .encryption import Encryption
from .gateway_info import GatewayInfo
from .circuits import Circuits
from .sensors import Sensors


class RequestError(Exception):
    """Raise request to Bosch thermostat error. """


class Gateway:
    """Gateway to Bosch thermostat."""

    def __init__(self, websession, host, access_key, password):
        """
        :param access_key:
        :param password:
        :param host:
        """
        self._host = host
        self._websession = websession
        self._encryption = Encryption(access_key, password)
        self._data = {
            GATEWAY: None,
            HC: None,
            DHW: None,
            SENSORS: None
        }
        self._serial_number = None
        self._requests = {
            GET: self.get,
            SUBMIT: self.set_value
        }

    def encrypt(self, data):
        """ Encrypt message to gateway. """
        return self._encryption.encrypt(data)

    def decrypt(self, data):
        """ Decrypt message from gateway. """
        return self._encryption.decrypt(data)

    def format_url(self, path):
        """ Format URL to make requests to gateway. """
        return 'http://{}{}'.format(self._host, path)

    def get_items(self, data_type):
        """ Get items on types like Sensors, Heating Circuits etc. """
        return self._data[data_type].get_items()

    @property
    def heating_circuits(self):
        """ Get circuit list. """
        return self._data[HC].circuits

    @property
    def sensors(self):
        """ Get sensors list. """
        return self._data[SENSORS].sensors

    def get_property(self, qtype, property_name):
        """ Get property of gateway info. """
        if qtype == 'info':
            return self._data[GATEWAY].get_property(property_name)
        return None

    def get_request(self):
        """ For testing purposes only. Delete it in final lib."""
        return self.get

    async def initialize_gatewayinfo(self, restored_data=None):
        self._data[GATEWAY] = GatewayInfo(self._requests, GATEWAY)
        await self._data[GATEWAY].update()

    async def initialize_hc_circuits(self, restored_data=None):
        self._data[HC] = Circuits(self._requests, HC)
        await self._data[HC].initialize(restored_data)
            # here can add circuits from memory
        # await self._data[HC].update()

    async def initialize_dhw_circuits(self, restored_data=None):
        self._data[HC] = Circuits(self._requests, DHW)
        await self._data[HC].initialize(restored_data)
            # here can add circuits from memory
        # await self._data[HC].update()

    async def initialize_sensors(self, restored_data=None):
        self._data[SENSORS] = Sensors(self._requests)
        await self._data[SENSORS].initialize(restored_data)
            # here can sensors from memory
        # await self._data[SENSORS].update()

    async def initialize(self):
        """ Initialize gateway asynchronously. """
        await self.initialize_gatewayinfo()
        await self.initialize_sensors()
        await self.initialize_hc_circuits(None)
        await self.initialize_dhw_circuits(None)

    async def request(self, path):
        """ Make a get request to the API. """
        try:
            with async_timeout.timeout(TIMEOUT):
                async with self._websession.get(
                        self.format_url(path),
                        headers=HTTP_HEADER) as res:
                    data = await res.text()
                    return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error getting data from {}, path: {}, message: {}'
                .format(self._host, path, err)
            )

    async def submit(self, path, data):
        """Make a put request to the API."""
        try:
            with async_timeout.timeout(TIMEOUT):
                async with self._websession.put(
                        self.format_url(path),
                        data=data,
                        headers=HTTP_HEADER) as req:
                    data = await req.text()
                    return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error putting data to {}, path: {}, message: {}'.
                format(self._host, path, err)
            )

    async def get(self, path):
        """ Get message from API with given path. """
        encrypted = await self.request(path)
        result = self._encryption.decrypt(encrypted)
        jsondata = json.loads(result)
        return jsondata

    async def set(self, path, data):
        """ Send message to API with given path. """
        encrypted = self._encryption.encrypt(data)
        result = await self.submit(path, encrypted)
        return result

    async def set_value(self, path, value):
        """ Set value for thermostat. """
        data = json.dumps({"value": value})
        result = await self.set(path, data)
        return result
