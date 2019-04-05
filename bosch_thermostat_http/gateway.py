"""Gateway module connecting to Bosch thermostat."""
import json
import asyncio


from .const import (GET, UUID, SUBMIT, DHW, HC, GATEWAY,
                    SENSORS, ROOT_PATHS, GATEWAY_PATH_LIST,
                    SYSTEM_CAPABILITIES, DETAILED_CAPABILITIES,
                    SENSORS_CAPABILITIES, VALUE, ID)
from .encryption import Encryption
from .sensors import Sensors
from .circuits import Circuits

from .errors import RequestError, ResponseError
from .helper import deep_into


class Gateway:
    """Gateway to Bosch thermostat."""

    def __init__(self, session, host, access_key, password=None):
        """
        :param access_key:
        :param password:
        :param host:
        """
        if type(session).__name__ == 'ClientSession':
            from .http_connector import HttpConnector
            self._connector = HttpConnector(host, session)
        else:
            return
        self._encryption = None
        self._lock = asyncio.Lock()
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

    def get_items(self, data_type):
        """ Get items on types like Sensors, Heating Circuits etc. """
        return self._data[data_type].get_items()

    def set_timeout(self, timeout):
        """ Set timeout for API calls. """
        self._connector.set_timeout(timeout)

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
        """ Get gateway info given key. """
        if key in self._data[GATEWAY]:
            return self._data[GATEWAY][key]
        return None

    async def _update_info(self):
        """ Update gateway info from Bosch device. """
        for key in GATEWAY_PATH_LIST:
            response = await self.get(GATEWAY_PATH_LIST[key])
            if VALUE in response:
                name = response[ID].split('/').pop()
                self._data[GATEWAY][name] = response[VALUE]

    async def get_capabilities(self):
        """ Get capabilities of gateway. """
        capabilities = []
        for key, values in SYSTEM_CAPABILITIES.items():
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
        """ Initialize circuits objects of given type (dhw/hcs). """
        self._data[circ_type] = Circuits(self._requests, circ_type)
        await self._data[circ_type].initialize(restored_data)

    async def initialize_sensors(self, restored_data=None):
        """ Initialize sensors objects. """
        self._data[SENSORS] = Sensors(self._requests)
        await self._data[SENSORS].initialize(restored_data)

    async def rawscan(self):
        """ Print out all info from gateway. """
        for root in ROOT_PATHS:
            await deep_into(root, self.get, True)

    async def check_connection(self):
        """Check if we are able to connect to Bosch device and return UUID."""
        try:
            await self.initialize()
            return self.get_info(UUID)
        except RequestError:
            return False

    async def get(self, path):
        """ Get message from API with given path. """
        async with self._lock:
            try:
                encrypted = await self._connector.request(path)
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
            result = await self._connector.submit(path, encrypted)
            return result

    async def set_value(self, path, value):
        """ Set value for thermostat. """
        data = json.dumps({"value": value})
        result = await self._set(path, data)
        return result
