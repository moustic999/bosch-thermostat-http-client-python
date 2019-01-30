""" Sensors of Bosch thermostat. """
from .const import SENSOR_NAME, SENSOR_TYPE, SENSOR_UNIT, SENSOR_VALUE


class Sensors:
    """ Sensors object containing multiple Sensor objects. """
    def __init__(self, get_request):
        """
        :param obj get_request: function to retrieve data from thermostat.
        """
        self._get_request = get_request
        self._items = []

    async def update(self):
        """ Update all sensors state asynchronously. """
        for item in self._items:
            await item.update()

    def get_sensors(self):
        """ Get sensor list. """
        return self._items

    def register_sensor(self, name, path):
        """ Register sensor for the module. """
        self._items.append(Sensor(self._get_request, name, path))


class Sensor:
    """ Single sensor object. """
    def __init__(self, get_request, name, path):
        """
        :param obj get_request: function to retrieve data from thermostat.
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        self._get_request = get_request
        self._data = {
            SENSOR_NAME: name,
            SENSOR_TYPE: None,
            SENSOR_VALUE: None,
            SENSOR_UNIT: None
        }
        self._path = path

    def get_property(self, property_name):
        """
        Get sensor data.
        :param str property_name: use on of values from const.py
            SENSOR_NAME, SENSOR_VALUE, SENSOR_TYPE, SENSOR_UNIT
        """
        if property_name in self._data:
            return self._data[property_name]
        return None

    async def update(self):
        """ Update sensor data. """
        data = await self._get_request(self._path)
        self._data[SENSOR_VALUE] = data['value']
        self._data[SENSOR_TYPE] = data['type']
        self._data[SENSOR_UNIT] = data['unitOfMeasure']
