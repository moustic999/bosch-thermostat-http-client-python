""" Sensors of Bosch thermostat. """
from .const import (SENSOR_NAME, SENSORS,
                    SENSOR_TYPE, SENSOR_UNIT, SENSOR_VALUE, GET, PATH)
from .helper import BoschSingleEntity, BoschEntities

### ADD RESTORING_DATA

class Sensors(BoschEntities):
    """ Sensors object containing multiple Sensor objects. """
    def __init__(self, requests):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(requests)

    @property
    def sensors(self):
        """ Get sensor list. """
        return self.get_items()

    async def initialize(self, sensors=None):
        restoring_data = True
        if not sensors:
            sensors = await self.retrieve_from_module(2, SENSORS)
            restoring_data = False
        for sensor in sensors:
            if "id" in sensor:
                self.register_sensor(sensor["id"],
                                     sensor["id"], restoring_data)

    def register_sensor(self, attr_id, path, restoring_data):
        """ Register sensor for the module. """
        self._items.append(Sensor(self._requests, attr_id, path, restoring_data))


class Sensor(BoschSingleEntity):
    """ Single sensor object. """
    def __init__(self, requests, attr_id, path, restoring_data):
        """
        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        self._requests = requests
        self._data = {
            SENSOR_NAME: attr_id.split('/').pop(),
            SENSOR_TYPE: None,
            SENSOR_VALUE: None,
            SENSOR_UNIT: None
        }
        super().__init__(attr_id.split('/').pop(), attr_id, restoring_data,
                         self._data, path)

    async def update(self):
        """ Update sensor data. """
        data = await self._requests[GET](self._main_data[PATH])
        self._data[SENSOR_VALUE] = data['value']
        self._data[SENSOR_TYPE] = data['type']
        self._data[SENSOR_UNIT] = data['unitOfMeasure']
