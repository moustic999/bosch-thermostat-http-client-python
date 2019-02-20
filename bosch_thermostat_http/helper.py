""" Helper functions. """

from .const import (GET, NAME, PATH, ID, VALUE, MINVALUE, MAXVALUE,
                    ALLOWED_VALUES, UNITS, STATE, DHW_OFFTEMP_LEVEL)


async def crawl(url, _list, deep, get):
    resp = await get(url)
    if (("references" not in resp or deep == 0) and "id" in resp):
        _list.append(resp)
    else:
        if "references" in resp:
            for uri in resp["references"]:
                if "id" in uri and deep > 0:
                    await crawl(uri["id"], _list, deep-1, get)
    return _list


async def deep_into(url, get, log=None):
    if log:
        print(url)
    resp = await get(url)
    if log:
        print(resp)
    if "references" in resp:
        for uri in resp["references"]:
            await deep_into(uri["id"], get, log)


def check_sensor(sensor):
    """ Check if sensor is valid. """
    if ID in sensor and VALUE in sensor:
        if STATE in sensor:
            for item in sensor[STATE]:
                for key in item:
                    if sensor[VALUE] == item[key]:
                        return False
        return True
    return False


class RequestError(Exception):
    """Raise request to Bosch thermostat error. """


class BoschEntities:
    """
    Main object to deriver sensors and circuits.
    """
    def __init__(self, requests):
        """
        :param dic requests: { GET: get function, SUBMIT: submit function}
        """
        self._items = []
        self._requests = requests

    async def retrieve_from_module(self, deep, path):
        return await crawl(path, [], deep, self._requests[GET])

    def get_items(self):
        """ Get items. """
        return self._items

    async def update_all(self):
        """ Update all heating circuits. """
        for item in self._items:
            await item.update()


class BoschSingleEntity:

    def __init__(self, name, attr_id, restoring_data, path=None):
        self._main_data = {
            NAME: name,
            ID: attr_id,
            PATH: path
        }
        self._data = {}
        self._type = None
        self._json_scheme_ready = restoring_data

    def process_results(self, result, key=None):
        data = self._data if self._type == "sensor" else self._data[key]
        if result:
            for res_key in [VALUE, MINVALUE, MAXVALUE, ALLOWED_VALUES,
                            UNITS, STATE]:
                if res_key in result:
                    data[res_key] = result[res_key]

    def get_property(self, property_name):
        """ Retrieve JSON with all properties: value, min, max, state etc."""
        if property_name == DHW_OFFTEMP_LEVEL:
            print("sprawdzawm")
            print(self._data)
        return self._data[property_name]

    def get_value(self, property_name):
        """ Retrieve only value from JSON. """
        ref = self.get_property(property_name)
        if ref:
            return ref.get(VALUE)
        print("no value")
        print(VALUE)
        return None


    @property
    def attr_id(self):
        return self._main_data[ID]

    def get_all_properties(self):
        return self._data

    @property
    def name(self):
        """ Name of Bosch entity. """
        return self._main_data[NAME]

    @property
    def json_scheme_ready(self):
        """ Is Bosch entity restored from scheme. """
        return self._json_scheme_ready

    @property
    def path(self):
        return self._main_data[PATH]
