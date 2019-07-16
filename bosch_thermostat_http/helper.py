"""Helper functions."""

from .const import (GET, NAME, PATH, ID, VALUE, MINVALUE, MAXVALUE, OPEN,
                    SHORT, ALLOWED_VALUES, UNITS, STATE)

from .errors import ResponseError, EncryptionError


def parse_float_value(value, single_value=True, min_max_obligatory=False):
    """Parse if value is between min and max."""
    if value:
        if STATE in value:
            for k in value[STATE]:
                if ((OPEN in k and k[OPEN] == value[VALUE]) or
                        (SHORT in k and k[SHORT] == value[VALUE])):
                    return None
        if all(k in value for k in (VALUE, MINVALUE, MAXVALUE)):
            if value[MINVALUE] <= value[VALUE] <= value[MAXVALUE]:
                return value[VALUE] if single_value else value
            return None
        if not min_max_obligatory:
            return value[VALUE] if single_value else value
    return None


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


async def deep_into(url, get, log=None):
    """Test for getting references. Used for raw scan."""
    if log:
        print(url)
    try:
        resp = await get(url)
        if log:
            print(resp)
        if "references" in resp:
            for uri in resp["references"]:
                await deep_into(uri["id"], get, log)
    except (EncryptionError, ResponseError):
        pass
        # print("error : {}". format(err))


def check_sensor(sensor):
    """Check if sensor is valid."""
    if ID in sensor and VALUE in sensor:
        if STATE in sensor:
            for item in sensor[STATE]:
                for key in item:
                    if sensor[VALUE] == item[key]:
                        return False
        return True
    return False


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

    def __init__(self, name, attr_id, restoring_data, path=None):
        """Initialize single entity."""
        self._main_data = {
            NAME: name,
            ID: attr_id,
            PATH: path
        }
        self._data = {}
        self._type = None
        self._json_scheme_ready = restoring_data

    def process_results(self, result, key=None):
        """Convert multi-level json object to one level object."""
        data = self._data if self._type == "sensor" else self._data[key]
        if result:
            for res_key in [VALUE, MINVALUE, MAXVALUE, ALLOWED_VALUES,
                            UNITS, STATE]:
                if res_key in result:
                    data[res_key] = result[res_key]

    def get_property(self, property_name):
        """Retrieve JSON with all properties: value, min, max, state etc."""
        return self._data[property_name]

    def get_value(self, property_name):
        """Retrieve only value from JSON."""
        ref = self.get_property(property_name)
        if ref:
            return ref.get(VALUE)
        return None

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
