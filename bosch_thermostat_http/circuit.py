from .const import GET, PATH, ID, VALUE
from .helper import BoschSingleEntity, crawl

class Circuit(BoschSingleEntity):

    def __init__(self, requests, attr_id, restoring_data):
        self._circuits_path = {}
        self._references = None
        self._requests = requests
        self._restoring_data = restoring_data
        name = attr_id.split('/').pop()
        super().__init__(name, attr_id, restoring_data)
        self._updated_initialized = False

    @property
    def json_scheme(self):
        return self._circuits_path

    @property
    def update_initialized(self):
        return self._updated_initialized


    async def initialize(self):
        """ Check each uri if return json with values. """
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
        """ Update info about Circuit asynchronously. """
        for key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)
        self._updated_initialized = True

    async def update_requested_key(self, key):
        """ Update info about Circuit asynchronously. """
        if key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)
            self._updated_initialized = True
