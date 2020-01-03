"""Gateway module connecting to Bosch thermostat."""

import logging
from .http_connector import HttpConnector
from .db import get_db_of_firmware, get_initial_db, get_custom_db
from .circuits import Circuits
from .const import (
    DHW,
    DICT,
    GATEWAY,
    HC,
    SC,
    ROOT_PATHS,
    SENSORS,
    UUID,
    VALUE,
    MODELS,
    VALUES,
    SYSTEM_INFO,
    NAME,
    DATE,
    FIRMWARE_VERSION,
    REFS,
    ID,
    HEATING_CIRCUITS,
    DHW_CIRCUITS,
    SYSTEM_BUS,
    CAN,
    EMS,
    CIRCUITS,
    CIRCUIT_TYPES
)
from .encryption import Encryption
from .exceptions import DeviceException
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
        self._host = host
        if password:
            access_token = access_key.replace("-", "")
            _encryption = Encryption(access_token, password)
        else:
            _encryption = Encryption(access_key)
        if type(session).__name__ == "ClientSession":
            self._connector = HttpConnector(host, session, _encryption)
        else:
            return
        self._data = {GATEWAY: {}, HC: None, DHW: None, SENSORS: None}
        self._firmware_version = None
        self._device = None
        self._db = None
        self._str = None
        self._initialized = None
        self._bus_type = None

    async def initialize(self):
        """Initialize gateway asynchronously."""
        initial_db = get_initial_db()
        self._str = Strings(initial_db[DICT])
        await self._update_info(initial_db.get(GATEWAY))
        self._firmware_version = self._data[GATEWAY].get(FIRMWARE_VERSION)
        self._device = await self.get_device_type(initial_db)
        if self._device and VALUE in self._device:
            self._db = get_db_of_firmware(self._device[VALUE], self._firmware_version)
            if self._db:
                initial_db.pop(MODELS, None)
                self._db.update(initial_db)
                self._initialized = True

    def custom_initialize(self, extra_db):
        "Custom initialization of component"
        if self._firmware_version:
            self._db = get_custom_db(self._firmware_version, extra_db)
            initial_db = get_initial_db()
            initial_db.pop(MODELS, None)
            self._db.update(initial_db)
            self._initialized = True

    async def get_device_type(self, _db):
        """Find device model."""
        system_bus = self._data[GATEWAY].get(SYSTEM_BUS)
        model_scheme = _db[MODELS]
        if system_bus == CAN:
            self._bus_type = CAN
            return model_scheme.get(CAN)
        self._bus_type = EMS
        system_info = self._data[GATEWAY].get(SYSTEM_INFO)
        if system_info:
            for info in system_info:
                model = model_scheme.get(info.get("Id", -1))
                if model:
                    return model

    async def _update_info(self, initial_db):
        """Update gateway info from Bosch device."""
        for name, uri in initial_db.items():
            try:
                response = await self._connector.get(uri)
                if self._str.val in response:
                    self._data[GATEWAY][name] = response[self._str.val]
                elif name == SYSTEM_INFO:
                    self._data[GATEWAY][SYSTEM_INFO] = response.get(VALUES, [])
            except DeviceException as err:
                _LOGGER.debug("Can't fetch data for update_info %s", err)
                pass

    @property
    def host(self):
        """Return host of Bosch gateway. Either IP or hostname."""
        return self._host

    @property
    def device_name(self):
        """Device friendly name based on model."""
        if self._device:
            return self._device.get(NAME)

    def get_items(self, data_type):
        """Get items on types like Sensors, Heating Circuits etc."""
        return self._data[data_type].get_items()

    async def current_date(self):
        """Find current datetime of gateway."""
        response = await self._connector.get(self._db[GATEWAY].get(DATE))
        val = response.get(self._str.val)
        self._data[GATEWAY][DATE] = val
        return val

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
        return self._connector.encryption_key

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
    def solar_circuits(self):
        """Get solar circuits."""
        return self._data[SC].circuits

    @property
    def sensors(self):
        """Get sensors list."""
        return self._data[SENSORS].sensors

    @property
    def firmware(self):
        """Get firmware."""
        return self._firmware_version

    @property
    def uuid(self):
        return self.get_info(UUID)

    def get_info(self, key):
        """Get gateway info given key."""
        if key in self._data[GATEWAY]:
            return self._data[GATEWAY][key]
        return None

    async def get_capabilities(self):
        supported = []
        for circuit in CIRCUIT_TYPES.keys():
            try:
                circuit_object = await self.initialize_circuits(circuit)
                if circuit_object:
                    supported.append(circuit)
            except DeviceException as err:
                _LOGGER.debug("Circuit %s not found. Skipping it. %s", circuit, err)
                pass
        return supported

    async def initialize_circuits(self, circ_type):
        """Initialize circuits objects of given type (dhw/hcs)."""
        self._data[circ_type] = Circuits(self._connector, circ_type, self._bus_type)
        await self._data[circ_type].initialize(self._db, self._str, self.current_date)
        return self.get_circuits(circ_type)

    def initialize_sensors(self, choosed_sensors=None):
        """Initialize sensors objects."""
        if not choosed_sensors:
            choosed_sensors = self._db.get(SENSORS)
        self._data[SENSORS] = Sensors(
            self._connector, choosed_sensors, self._db[SENSORS], self._str
        )
        return self.sensors

    async def rawscan(self):
        """Print out all info from gateway."""
        rawlist = []
        for root in ROOT_PATHS:
            rawlist.append(await deep_into(root, [], self._connector.get))
        return rawlist

    async def smallscan(self, _type=HC):
        """Print out all info from gateway from HC1 or DHW1 only for now."""
        if _type == HC:
            refs = self._db.get(HEATING_CIRCUITS).get(REFS)
            format_string = "hc1"
        elif _type == DHW:
            refs = self._db.get(DHW_CIRCUITS).get(REFS)
            format_string = "dhw1"
        else:
            refs = self._db.get(SENSORS)
            format_string = ""
        rawlist = []
        for item in refs.values():
            uri = item[ID].format(format_string)
            rawlist.append(await deep_into(uri, [], self._connector.get))
        return rawlist

    async def check_connection(self):
        """Check if we are able to connect to Bosch device and return UUID."""
        try:
            if not self._initialized:
                await self.initialize()
            else:
                response = await self._connector.get(self._db[GATEWAY][UUID])
                if self._str.val in response:
                    self._data[GATEWAY][UUID] = response[self._str.val]
        except DeviceException as err:
            _LOGGER.debug("Failed to check_connection: %s", err)
        uuid = self.get_info(UUID)
        return uuid

