import json

import async_timeout
from aiohttp import client_exceptions

from .const import HTTP_HEADER, TIMEOUT, SENSOR_LIST
from .encryption import Encryption
from .gateway_info import GatewayInfo
from .sensors import Sensors
from .heating_circuits import HeatingCircuits


class RequestError(Exception):
    """Raise request to Bosch thermostat error. """


class Gateway:

    def __init__(self, websession, host, access_key, password):
        """
        :param access_key:
        :param password:
        :param host:
        """
        self._host = host
        self._websession = websession
        self._encryption = Encryption(access_key, password)
        self._sensors = None
        self._info = None
        self._heatingcirctuits = None
        self._serial_number = None

    def encrypt(self, data):
        return self._encryption.encrypt(data)

    def decrypt(self, data):
        return self._encryption.decrypt(data)

    def format_url(self, path):
        return 'http://{}{}'.format(self._host, path)

    def get_sensors(self):
        return self._sensors.get_sensors()

    def get_property(self, qtype, property_name):
        if qtype == 'info':
            return self._info.get_property(property_name)
        return None

    async def initialize(self):
        self._info = GatewayInfo(self.get)
        await self._info.update()

        self._sensors = Sensors(self.get)
        for sensor_name, sensor_address in SENSOR_LIST.items():
            self._sensors.register_sensor(sensor_name, sensor_address)
        await self._sensors.update()

        self._heatingcirctuits = HeatingCircuits(self.get, self.set)
        await self._heatingcirctuits.initialize()
        await self._heatingcirctuits.update()

    async def request(self, path):
        """ Make a request to the API. """
        try:
            with async_timeout.timeout(TIMEOUT):
                async with self._websession.get(
                        self.format_url(path),
                        headers=HTTP_HEADER) as res:
                    data = await res.text()
                    return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self._host, err)
            )

    async def submit(self, path, data):
        """Make a request to the API."""
        try:
            with async_timeout.timeout(TIMEOUT):
                async with self._websession.put(
                        self.format_url(path),
                        data=data,
                        headers=HTTP_HEADER) as req:
                    await req.text()
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error putting data to {}: {}'.format(self._host, err)
            )

    async def get(self, path):
        encrypted = await self.request(path)
        result = self._encryption.decrypt(encrypted)
        jsondata = json.loads(result)
        return jsondata

    async def set(self, path, data):
        encrypted = self._encryption.encrypt(data)
        result = await self.submit(path, encrypted)
        return result

    async def set_value(self, path, value):
        data = json.dumps({"value": value})
        result = await self.set(path, data)
        return result
