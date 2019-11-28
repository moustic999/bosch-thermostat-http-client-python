"""Sensors of Bosch thermostat."""
from .const import ID, NAME, RESULT, URI, TYPE, REGULAR, SENSOR
from .helper import BoschSingleEntity, BoschEntities


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, requests, sensors=None, sensors_db=None, str_obj=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(requests)
        self._items = {}
        for sensor_id in sensors:
            sensor = sensors_db.get(sensor_id)
            if sensor and sensor_id not in self._items:
                self._items[sensor_id] = Sensor(
                    self._requests, sensor_id, sensor[NAME], sensor[ID], str_obj
                )

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    def __init__(self, requests, attr_id, name, path, str_obj):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        super().__init__(name, attr_id, str_obj, requests, SENSOR, path)
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: REGULAR}}

    def get_all_properties(self):
        """Retrieve all properties with value, min, max etc."""
        return self._data[self.attr_id].get(RESULT)
