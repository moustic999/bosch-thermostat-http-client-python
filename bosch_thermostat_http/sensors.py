""" Sensors of Bosch thermostat. """
from .const import (SENSOR_NAME, SENSORS,
                    SENSOR_TYPE, SENSOR_UNIT, SENSOR_VALUE, GET, PATH, ID,
                    NAME, VALUE, STATE)
from .helper import BoschSingleEntity, BoschEntities, check_sensor

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
            sensor_check_status = (check_sensor(sensor)
                                   if not restoring_data else True)
            if sensor_check_status:
                self.register_sensor(sensor[ID],
                                     sensor[ID], restoring_data)

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
        name = attr_id.split('/').pop()
        super().__init__(name, attr_id, restoring_data, path)
        self._type = "sensor"

    @property
    def json_scheme(self):
        return {
            NAME: self._main_data[NAME],
            ID: self._main_data[ID]
        }

    async def update(self):
        """ Update sensor data. """
        result = await self._requests[GET](self._main_data[PATH])
        self.process_results(result)
