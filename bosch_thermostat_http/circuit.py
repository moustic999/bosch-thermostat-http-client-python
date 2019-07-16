"""Main circuit object."""
import logging
from .const import GET, PATH, ID, VALUE, ALLOWED_VALUES, OPERATION_MODE, SUBMIT
from .helper import BoschSingleEntity, crawl

_LOGGER = logging.getLogger(__name__)


class Circuit(BoschSingleEntity):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, requests, attr_id, restoring_data):
        """Initialize circuit with requests and id from gateway."""
        self._circuits_path = {}
        self._references = None
        self._requests = requests
        self._restoring_data = restoring_data
        name = attr_id.split('/').pop()
        super().__init__(name, attr_id, restoring_data)
        self._updated_initialized = False

    @property
    def json_scheme(self):
        """Give simple json scheme of circuit."""
        return self._circuits_path

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
        keys_to_del = []
        keys_to_add = {}
        for key, value in self._circuits_path.items():
            result = await crawl(value, [], 1, self._requests[GET])
            if not result:
                keys_to_del.append(key)
            for res in result:
                if ID in res:
                    short_wanted = res[ID].replace(self._main_data[ID],
                                                   '').replace('/', '')
                    if key != short_wanted:
                        keys_to_add[short_wanted] = res[ID]
                        keys_to_del.append(key)
        for key in keys_to_add:
            self._circuits_path[key] = keys_to_add[key]
            self._data[key] = {}
        for key in keys_to_del:
            if key in self._data:
                del self._data[key]
            if key in self._circuits_path:
                del self._circuits_path[key]
        self._json_scheme_ready = True

    def add_data(self, path, references):
        """Add all URI which we taking values from."""
        self._main_data[PATH] = path
        for key in references:
            if self._restoring_data:
                short_id = key
                self._circuits_path[short_id] = references[key]
            else:
                short_id = key['id'].replace(self._main_data[ID],
                                             '').replace('/', '')
                self._circuits_path[short_id] = key["id"]
            self._data[short_id] = {}

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
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)
            self._updated_initialized = True

    async def set_operation_mode(self, new_mode):
        """Set operation_mode of Heating Circuit."""
        if (self._data[OPERATION_MODE][VALUE] == new_mode):
            _LOGGER.warning("Trying to set mode which is already set %s",
                            new_mode)
        elif (ALLOWED_VALUES in self._data[OPERATION_MODE] and
                new_mode in self._data[OPERATION_MODE][ALLOWED_VALUES]):
            await self._requests[SUBMIT](self._circuits_path[OPERATION_MODE],
                                         new_mode)
            return new_mode
        _LOGGER.warning("You wanted to set %s, but it is not allowed %s",
                        new_mode,
                        self._data[OPERATION_MODE][ALLOWED_VALUES])
        return None
