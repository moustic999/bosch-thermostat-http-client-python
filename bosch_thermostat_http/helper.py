"""Helper functions."""

import re

from .const import (ALLOWED_VALUES, GET, ID, NAME, OPEN, PATH, SHORT, STATE,
                    UNITS, VALUE, MIN, MAX, AUTO)
from .errors import EncryptionError, ResponseError

regex = re.compile("http://\\d+\\.\\d+\\.\\d+\\.\\d+/", re.IGNORECASE)


async def crawl(url, _list, deep, get, exclude=()):
    """Crawl for Bosch API correct values."""
    try:
        resp = await get(url)
        if (("references" not in resp or deep == 0) and "id" in resp):
            if not resp['id'] in exclude:
                _list.append(resp)
        else:
            if "references" in resp:
                for uri in resp["references"]:
                    if "id" in uri and deep > 0:
                        await crawl(uri["id"], _list, deep-1, get, exclude)
        return _list
    except ResponseError:
        # print("error while retrieving url {} with error {}".format(url, err))
        return _list


async def deep_into(url, _list, get):
    """Test for getting references. Used for raw scan."""
    try:
        resp = await get(url)
        new_resp = resp
        if 'uri' in new_resp:
            new_resp['uri'] = remove_all_ip_occurs(resp['uri'])
        if 'id' in new_resp and new_resp['id'] == '/gateway/uuid':
            new_resp['value'] = -1
            new_resp['allowedValues'] = -1
        if ('setpointProperty' in new_resp and
                'uri' in new_resp['setpointProperty']):
            new_resp['setpointProperty']['uri'] = remove_all_ip_occurs(
                new_resp['setpointProperty']['uri'])
        _list.append(resp)
        if "references" in resp:
            for idx, val in enumerate(resp["references"]):
                val2 = val
                if 'uri' in val2:
                    val2['uri'] = remove_all_ip_occurs(val2['uri'])
                new_resp['references'][idx] = val2
                await deep_into(val["id"], _list, get)
    except (EncryptionError, ResponseError):
        pass
    return _list


def remove_all_ip_occurs(data):
    return regex.sub("http://THERMOSTAT/", data)


class BoschEntities:
    """Main object to deriver sensors and circuits."""

    def __init__(self, requests):
        """
        Initiazlie Bosch entities.

        :param dic requests: { GET: get function, SUBMIT: submit function}
        """
        self._items = []
        self._requests = requests

    async def retrieve_from_module(self, deep, path, exclude=()):
        """Retrieve all json objects with simple values."""
        return await crawl(path, [], deep, self._requests[GET], exclude)

    def get_items(self):
        """Get items."""
        return self._items

    async def update_all(self):
        """Update all heating circuits."""
        for item in self._items:
            await item.update()


class BoschSingleEntity:
    """Object for single sensor/circuit. Don't use it directly."""

    def __init__(self, name, attr_id, dict, path=None):
        """Initialize single entity."""
        self._main_data = {
            NAME: name,
            ID: attr_id,
            PATH: path
        }
        self._data = {}
        self._type = None
        self.__initialize_dict(dict)
        self._json_scheme_ready = False

    def __initialize_dict(self, dictionary):
        self._dict = dictionary
        self._val_str = self._dict.get(VALUE, VALUE)
        self._min_str = self._dict.get(MIN, MIN)
        self._max_str = self._dict.get(MAX, MAX)
        self._all_str = self._dict.get(ALLOWED_VALUES, ALLOWED_VALUES)
        self._units_str = self._dict.get(UNITS, UNITS)
        self._state_str = self._dict.get(STATE, STATE)
        self._open_str = self._dict.get(OPEN, OPEN)
        self._short_str = self._dict.get(SHORT, SHORT)
        self._auto_str = self._dict.get(AUTO, AUTO)

    def process_results(self, result, key=None):
        """Convert multi-level json object to one level object."""
        data = self._data if self._type == "sensor" else self._data[key]
        if result:
            for res_key in [self._val_str, self._min_str, self._max_str,
                            self._all_str, self._units_str, self._state_str]:
                if res_key in result:
                    data[res_key] = result[res_key]

    def get_property(self, property_name):
        """Retrieve JSON with all properties: value, min, max, state etc."""
        return self._data.get(property_name, {})

    def get_value(self, property_name, default_value=None):
        """Retrieve only value from JSON."""
        ref = self.get_property(property_name)
        return ref.get(self._val_str, default_value)

    @property
    def attr_id(self):
        """Get ID of the entity."""
        return self._main_data[ID]

    def get_all_properties(self):
        """Retrieve all properties with value, min, max etc."""
        return self._data

    @property
    def name(self):
        """Name of Bosch entity."""
        return self._main_data[NAME]

    @property
    def json_scheme_ready(self):
        """Is Bosch entity restored from scheme."""
        return self._json_scheme_ready

    @property
    def path(self):
        """Get path of Bosch API which entity is using for data."""
        return self._main_data[PATH]
