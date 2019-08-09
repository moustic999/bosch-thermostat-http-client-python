"""Main circuit object."""
import logging
from .const import (GET, PATH, ID, VALUE, ALLOWED_VALUES, HEATING_CIRCUITS,
                    DHW_CIRCUITS, HC,
                    OPERATION_MODE, SUBMIT, DICT, REFS)
from .helper import BoschSingleEntity, crawl

_LOGGER = logging.getLogger(__name__)


class Circuit(BoschSingleEntity):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, requests, attr_id, db, type):
        """Initialize circuit with requests and id from gateway."""
        self._circuits_path = {}
        self._references = None
        self._requests = requests
        name = attr_id.split('/').pop()
        self._type = type
        self._db = db[HEATING_CIRCUITS if type == HC else DHW_CIRCUITS]
        super().__init__(name, attr_id, db[DICT])
        self._updated_initialized = False
    
    def __initialize_dict(self, dictionary):
        pass

    @property
    def db_json(self):
        """Give simple json scheme of circuit."""
        return self._db

    @property
    def update_initialized(self):
        """Inform if we successfully invoked update at least one time."""
        return self._updated_initialized

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
            if result:
                self._circuits_path[key] = uri
                self._data[key] = {}
        self._json_scheme_ready = True

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating circuit %s", self.name)
        print(self._dict)
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
        op_mode_value = op_mode.get(self._val_str)
        allowed_values = op_mode.get(ALLOWED_VALUES, {})
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

    def parse_float_value(self, value, single_value=True, minmax_obliged=False):
        """Parse if value is between min and max."""
        val = value.get(self._val_str, None)
        for k in val:
            if ((self._open_str in k and k[self._open_str] == val) or
                    (self._short_str in k and k[self._short_str] == val)):
                return None
            if all(k in val for k in
                   (self._val_str, self._min_str, self._max_str)):
                if value[self._min_str] <= val <= value[self._max_str]:
                    return val if single_value else val
                return None
            if not minmax_obliged:
                return val[self._val_str] if single_value else value
        return None
