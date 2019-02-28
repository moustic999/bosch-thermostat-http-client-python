"""Gateway module connecting to Bosch thermostat."""
import json
import asyncio
from aiohttp import client_exceptions

from .const import (HTTP_HEADER, GET, UUID, SUBMIT, DHW, HC, GATEWAY,
                    SENSORS, ROOT_PATHS, GATEWAY_PATH_LIST,
                    SYTEM_CAPABILITIES, DETAILED_CAPABILITIES,
                    SENSORS_CAPABILITIES, VALUE, ID)
from .encryption import Encryption
from .sensors import Sensors
from .circuits import Circuits

from .errors import RequestError, ResponseError, EncryptionError
from .helper import deep_into


class Gateway:
    """Gateway to Bosch thermostat."""

    def __init__(self, websession, host, access_key, password=None):
        """
        :param access_key:
        :param password:
        :param host:
        """
        self._host = host
        self._websession = websession
        self._encryption = None
        self._lock = asyncio.Lock()
        self._request_timeout = 10

        if password:
            access_token = access_key.replace('-', '')
            self._encryption = Encryption(access_token, password)
        else:
            self._encryption = Encryption(access_key)
        self._data = {
            GATEWAY: {},
            HC: None,
            DHW: None,
            SENSORS: None
        }
        self._requests = {
            GET: self.get,
            SUBMIT: self.set_value
        }

    async def initialize(self):
        """ Initialize gateway asynchronously. """
        if not self._data[GATEWAY]:
            await self._update_info()

    def format_url(self, path):
        """ Format URL to make requests to gateway. """
        return 'http://{}{}'.format(self._host, path)

    def get_items(self, data_type):
        """ Get items on types like Sensors, Heating Circuits etc. """
        return self._data[data_type].get_items()

    def set_timeout(self, timeout):
        self._request_timeout = timeout

    @property
    def access_key(self):
        """ Return key to store in config entry."""
        return self._encryption.key

    @property
    def heating_circuits(self):
        """ Get circuit list. """
        return self._data[HC].circuits

    @property
    def dhw_circuits(self):
        """ Get circuit list. """
        return self._data[DHW].circuits

    @property
    def sensors(self):
        """ Get sensors list. """
        return self._data[SENSORS].sensors

    def get_request(self):
        """ For testing purposes only. Delete it in final lib."""
        return self.get

    def get_info(self, key):
        if key in self._data[GATEWAY]:
            return self._data[GATEWAY][key]
        return None

    async def _update_info(self):
        for key in GATEWAY_PATH_LIST:
            response = await self.get(GATEWAY_PATH_LIST[key])
            if VALUE in response:
                name = response[ID].split('/').pop()
                self._data[GATEWAY][name] = response[VALUE]

    async def get_capabilities(self):
        capabilities = []
        for key, values in SYTEM_CAPABILITIES.items():
            for value in values:
                response = await self.get(value)
                if response['type'] == 'refEnum':
                    for ref in response['references']:
                        if (key in DETAILED_CAPABILITIES or
                                ref['id'] in SENSORS_CAPABILITIES):
                            capabilities.append({
                                'name': ref[ID].split('/').pop(),
                                'type': key,
                            })
        return capabilities

    async def initialize_circuits(self, circ_type, restored_data=None):
        self._data[circ_type] = Circuits(self._requests, circ_type)
        await self._data[circ_type].initialize(restored_data)

    async def initialize_sensors(self, restored_data=None):
        self._data[SENSORS] = Sensors(self._requests)
        await self._data[SENSORS].initialize(restored_data)

    async def rawscan(self):
        """ print out all info from gateway """
        for root in ROOT_PATHS:
            await deep_into(root, self.get, True)

    async def check_connection(self):
        try:
            await self.initialize()
            return self.get_info(UUID)
        except RequestError:
            return False

    async def _request(self, path):
        """ Make a get request to the API. """
        try:
            async with self._websession.get(
                    self.format_url(path),
                    headers=HTTP_HEADER, timeout=self._request_timeout) as res:
                if res.status == 200:
                    if res.content_type != 'application/json':
                        raise ResponseError('Invalid content type: {}'.
                                            format(res.content_type))
                    else:
                        data = await res.text()
                        return data
                else:
                    raise ResponseError('Invalid response code: {}'.
                                        format(res.status))

        except (client_exceptions.ClientError,
                client_exceptions.ClientConnectorError,
                TimeoutError) as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self._host, err)
            )

    async def _submit(self, path, data):
        """Make a put request to the API."""
        try:
            async with self._websession.put(
                    self.format_url(path),
                    data=data,
                    headers=HTTP_HEADER,
                    timeout=self._request_timeout) as req:
                data = await req.text()
                return data
        except (client_exceptions.ClientError, TimeoutError) as err:
            raise RequestError(
                'Error putting data to {}, path: {}, message: {}'.
                format(self._host, path, err)
            )

    async def get(self, path):
        """ Get message from API with given path. """
        async with self._lock:
            try:
                encrypted = await self._request(path)
                result = self._encryption.decrypt(encrypted)
                jsondata = json.loads(result)
                return jsondata
            except json.JSONDecodeError as err:
                raise ResponseError("Unable to decode Json response : {}".
                                    format(err))

    async def _set(self, path, data):
        """ Send message to API with given path. """
        async with self._lock:
            encrypted = self._encryption.encrypt(data)
            result = await self._submit(path, encrypted)
            return result

    async def set_value(self, path, value):
        """ Set value for thermostat. """
        data = json.dumps({"value": value})
        result = await self._set(path, data)
        return result
