from .const import GET, PATH
from .helper import BoschSingleEntity, crawl

class Circuit(BoschSingleEntity):

    def __init__(self, requests, attr_id, restoring_data):
        self._circuits_path = {}
        self._references = None
        self._requests = requests
        self._restoring_data = restoring_data
        name = attr_id.split('/').pop()
        super().__init__(name, attr_id, restoring_data)

    @property
    def json_scheme(self):
        return self._circuits_path

    async def initialize(self):
        """ Check each uri if return json with values. """
        keys_to_del = []
        for key, value in self._circuits_path.items():
            result_id = await crawl(value, [], 1, self._requests[GET])
            if not result_id:
                keys_to_del.append(key)
        for key in keys_to_del:
            del self._data[key]
            del self._circuits_path[key]
        self._json_scheme_ready = True

    def add_data(self, path, references):
        self._main_data[PATH] = path
        for key in references:
            if self._restoring_data:
                short_id = key
                self._circuits_path[short_id] = references[key]
            else:
                short_id = key['id'].split('/').pop()
                self._circuits_path[short_id] = key["id"]
            self._data[short_id] = {}

    async def update(self):
        """ Update info about Circuit asynchronously. """
        for key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)

    async def update_requested_keys(self, key):
        """ Update info about Circuit asynchronously. """
        if key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self.process_results(result, key)
