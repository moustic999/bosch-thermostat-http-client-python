""" Sensors of Bosch thermostat. """
from .const import (SENSOR_NAME, SENSORS,
                    SENSOR_TYPE, SENSOR_UNIT, SENSOR_VALUE, GET, PATH)
from .helper import BoschSingleEntity, BoschEntities


class Sensors(BoschEntities):
    """ Sensors object containing multiple Sensor objects. """
    def __init__(self, requests):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(self, requests)

    def get_sensors(self):
        """ Get sensor list. """
        return self.get_items()

    async def initialize(self, sensors=None):
        if not sensors:
            sensors = await self.retrieve_from_module(2, SENSORS)
        for sensor in sensors:
            if "id" in sensor:
                self.register_sensor(sensor["id"].split('/').pop(),
                                     sensor["id"])

    def register_sensor(self, name, path):
        """ Register sensor for the module. """
        self._items.append(Sensor(self._requests, name, path))


class Sensor(BoschSingleEntity):
    """ Single sensor object. """
    def __init__(self, requests, name, path):
        """
        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        self._requests = requests
        self._data = {
            SENSOR_NAME: name,
            SENSOR_TYPE: None,
            SENSOR_VALUE: None,
            SENSOR_UNIT: None
        }
        super().__init__(name, self._data, path)

    async def update(self):
        """ Update sensor data. """
        data = await self._requests[GET](self._main_data[PATH])
        self._data[SENSOR_VALUE] = data['value']
        self._data[SENSOR_TYPE] = data['type']
        self._data[SENSOR_UNIT] = data['unitOfMeasure']
