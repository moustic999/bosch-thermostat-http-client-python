"""Main circuit object."""
import logging
from .const import (GET, ID, HEATING_CIRCUITS, DHW_CIRCUITS, HC, CURRENT_TEMP,
                    OPERATION_MODE, SUBMIT, REFS)
from .helper import BoschSingleEntity, crawl

_LOGGER = logging.getLogger(__name__)


class Circuit(BoschSingleEntity):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, requests, attr_id, db, str_obj, _type):
        """Initialize circuit with requests and id from gateway."""
        self._circuits_path = {}
        self._references = None
        self._requests = requests
        name = attr_id.split('/').pop()
        self._type = _type
        if self._type == HC:
            self._db = db[HEATING_CIRCUITS]
        else:
            self._db = db[DHW_CIRCUITS]
        super().__init__(name, attr_id, str_obj)

    @property
    def db_json(self):
        """Give simple json scheme of circuit."""
        return self._db

    @property
    def get_schedule(self):
        """Prepare to retrieve schedule of HC/DHW."""
        return None

    async def initialize(self):
        """Check each uri if return json with values."""
        refs = self._db[REFS]
        for key, value in refs.items():
            uri = value[ID].format(self.name)
            result = await crawl(uri, [], 1, self._requests[GET])
            _LOGGER.debug("INITIALIZING uri %s with result %s", uri, result)
            if result:
                self._circuits_path[key] = uri
                self._data[key] = {}
        self._json_scheme_ready = True

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating circuit %s", self.name)
        for key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)
        self._updated_initialized = True

    async def update_requested_key(self, key):
        """Update info about Circuit asynchronously."""
        if key in self._data:
            result = await self._requests[GET](self._circuits_path[key])
            self.process_results(result, key)
            self._updated_initialized = True

    async def set_operation_mode(self, new_mode):
        """Set operation_mode of Heating Circuit."""
        op_mode = self.get_property(OPERATION_MODE)
        op_mode_value = op_mode.get(self._str.val)
        allowed_values = op_mode.get(self._str.allowed_values, {})
        if op_mode_value == new_mode:
            _LOGGER.warning("Trying to set mode which is already set %s",
                            new_mode)
            return None
        if new_mode in allowed_values:
            await self._requests[SUBMIT](self._circuits_path[OPERATION_MODE],
                                         new_mode)
            return new_mode
        _LOGGER.warning("You wanted to set %s, but it is not allowed %s",
                        new_mode, allowed_values)
        return None

    @property
    def current_temp(self):
        """Give current temperature of circuit."""
        _LOGGER.debug("Current temp is %s",
                      self.get_property(CURRENT_TEMP))
        return self.parse_float_value(
            self.get_property(CURRENT_TEMP))

    @property
    def temp_units(self):
        """Return units of temperature."""
        return self.get_property(CURRENT_TEMP).get(self._str.units)

    def parse_float_value(self, val, single_value=True, minmax_obliged=False):
        """Parse if value is between min and max."""
        state = val.get(self._str.state, {})
        value = val.get(self._str.val, False)
        _min = val.get(self._str.min, -1)
        _max = val.get(self._str.max, -1)
        if not value:
            return None
        for k in state:
            if ((self._str.open in k and k[self._str.open] == val) or
                    (self._str.short in k and k[self._str.short] == val)):
                return None
        if all(k in val for k in
               (self._str.val, self._str.min, self._str.max)):
            if _min <= value <= _max:
                return value if single_value else val
            return None
        if not minmax_obliged:
            return value if single_value else val
        return None
