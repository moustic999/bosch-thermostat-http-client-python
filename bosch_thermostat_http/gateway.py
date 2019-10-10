"""Gateway module connecting to Bosch thermostat."""
import asyncio
import json
import logging

from .circuits import Circuits
from .const import (DHW, DICT, GATEWAY, GET, HC, ROOT_PATHS, SENSORS, SUBMIT,
                    UUID, VALUE, MODELS, VALUES, SYSTEM_INFO, NAME, DATE)
from .encryption import Encryption
from .errors import RequestError, Response404Error, ResponseError
from .helper import deep_into
from .sensors import Sensors
from .strings import Strings

_LOGGER = logging.getLogger(__name__)


class Gateway:
    """Gateway to Bosch thermostat."""

    def __init__(self, session, host, access_key, password=None):
        """
        Initialize gateway.

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
        self._firmware_version = None
        self._device = None
        self._db = None
        self._str = None

    async def initialize(self, database=None):
        """Initialize gateway asynchronously."""
        from .db import get_firmware_uri, get_db_of_firmware, get_initial_db
        self._firmware_version = await self.get(get_firmware_uri())
        initial_db = get_initial_db()
        if not database:
            self._device = await self.get_device_type(initial_db)
            self._db = get_db_of_firmware(self._device[VALUE],
                                          self._firmware_version[VALUE])
        else:
            from .db import check_db
            if check_db(self._firmware_version, database):
                self._db = database
            else:
                return False
        if not self._device:
            self._device = await self.get_device_type(initial_db)
        if self._db and self._device:
            if initial_db:
                initial_db.pop(MODELS, None)
                self._db.update(initial_db)
            self._str = Strings(self._db[DICT])
            if not self._data[GATEWAY]:
                await self._update_info()

    async def get_device_type(self, _db):
        """Find device model."""
        system_info = await self.get(_db[GATEWAY][SYSTEM_INFO])
        model_scheme = _db[MODELS]
        for info in system_info.get(VALUES, []):
            model = model_scheme.get(info.get('Id', -1))
            if model:
                return model

    @property
    def device_name(self):
        """Device friendly name based on model."""
        return self._device[NAME]

    def get_items(self, data_type):
        """Get items on types like Sensors, Heating Circuits etc."""
        return self._data[data_type].get_items()

    async def current_date(self):
        """Find current datetime of gateway."""
        response = await self.get(self._db[GATEWAY].get(DATE))
        if VALUE in response:
            self._data[GATEWAY][DATE] = response[VALUE]
            return response[VALUE]

    @property
    def database(self):
        """Retrieve db scheme."""
        return self._db

    def set_timeout(self, timeout):
        """Set timeout for API calls."""
        self._connector.set_timeout(timeout)

    @property
    def access_key(self):
        """Return key to store in config entry."""
        return self._encryption.key

    @property
    def heating_circuits(self):
        """Get circuit list."""
        return self._data[HC].circuits

    def get_circuits(self, ctype):
        """Get circuit list."""
        return self._data[ctype].circuits if ctype in self._data else None

    @property
    def dhw_circuits(self):
        """Get circuit list."""
        return self._data[DHW].circuits

    @property
    def sensors(self):
        """Get sensors list."""
        return self._data[SENSORS].sensors

    @property
    def firmware(self):
        """Get firmware."""
        return self._firmware_version.get(self._str.val)

    def get_info(self, key):
        """Get gateway info given key."""
        if key in self._data[GATEWAY]:
            return self._data[GATEWAY][key]
        return None

    async def _update_info(self):
        """Update gateway info from Bosch device."""
        for name, uri in self._db[GATEWAY].items():
            response = await self.get(uri)
            if VALUE in response:
                self._data[GATEWAY][name] = response[VALUE]

    async def initialize_circuits(self, circ_type):
        """Initialize circuits objects of given type (dhw/hcs)."""
        self._data[circ_type] = Circuits(self._requests, circ_type)
        await self._data[circ_type].initialize(self._db, self._str, self.current_date)
        return self.get_circuits(circ_type)

    async def initialize_sensors(self):
        """Initialize sensors objects."""
        self._data[SENSORS] = Sensors(self._requests)
        await self._data[SENSORS].initialize(self._db[SENSORS], self._str)
        return self.sensors

    async def rawscan(self):
        """Print out all info from gateway."""
        rawlist = []
        for root in ROOT_PATHS:
            rawlist.append(await deep_into(root, [], self.get))
        return rawlist

    async def smallscan(self):
        """Print out all info from gateway from HC2 only for now."""
        rawlist = []
        paths = [
            "/heatingCircuits/hc2/roomtemperature",
            "/heatingCircuits/hc2/operationMode",
            "/heatingCircuits/hc2/currentRoomSetpoint",
            "/heatingCircuits/hc2/manualRoomSetpoint",
            "/heatingCircuits/hc2/temperatureRoomSetpoint",
            "/heatingCircuits/hc2/status",
            "/heatingCircuits/hc2/activeSwitchProgram",
            "/heatingCircuits/hc2/temperatureLevels/day",
            "/heatingCircuits/hc2/temperatureLevels/night"
        ]
        for root in paths:
            rawlist.append(await deep_into(root, [], self.get))
        return rawlist

    async def check_connection(self, database=None):
        """Check if we are able to connect to Bosch device and return UUID."""
        try:
            await self.initialize(database)
            return self.get_info(UUID)
        except RequestError:
            return False

    async def get(self, path):
        """Get message from API with given path."""
        async with self._lock:
            try:
                encrypted = await self._connector.request(path)
                result = self._encryption.decrypt(encrypted)
                jsondata = json.loads(result)
                _LOGGER.debug("Retrieved data for path %s from gateway: %s", path, result)
                return jsondata
            except json.JSONDecodeError as err:
                raise ResponseError(f"Unable to decode Json response : {err}")
            except Response404Error:
                raise ResponseError(f"Path does not exist : {path}")

    async def _set(self, path, data):
        """Send message to API with given path."""
        async with self._lock:
            encrypted = self._encryption.encrypt(data)
            result = await self._connector.submit(path, encrypted)
            return result

    async def set_value(self, path, value):
        """Set value for thermostat."""
        data = json.dumps({"value": value})
        result = await self._set(path, data)
        return result
