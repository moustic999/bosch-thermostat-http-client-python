"""Sensors of Bosch thermostat."""
from .const import (GET, PATH, ID, NAME)
from .helper import BoschSingleEntity, BoschEntities
from .errors import ResponseError, Response404Error, SensorNoLongerAvailable


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, requests):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(requests)
        self._items = {}

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()

    async def initialize(self, sensors=None, str_obj=None):
        """
        Asynchronously initialize all sensors.

        :param sensors dict if declared then restore sensors from it.
                            If not download data from device.
        """
        for sensor in sensors:
            self.register_sensor(sensor[NAME],
                                 sensor[ID], str_obj)

    def register_sensor(self, name, path, str_obj):
        """Register sensor for the module."""
        attr_id = path.split('/').pop()
        if attr_id not in self._items:
            self._items[attr_id] = Sensor(self._requests, attr_id,
                                          name, path, str_obj)


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    def __init__(self, requests, attr_id, name, path, str_obj):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        self._requests = requests
        super().__init__(name, attr_id, str_obj, path)
        self._type = "sensor"

    @property
    def json_scheme(self):
        """Get json scheme of sensor."""
        return {
            NAME: self._main_data[NAME],
            ID: self._main_data[ID]
        }

    async def update(self):
        """Update sensor data."""
        try:
            result = await self._requests[GET](self._main_data[PATH])
            self.process_results(result)
            self._updated_initialized = True
        except Response404Error:
            raise SensorNoLongerAvailable("This sensor is no available.")
        except ResponseError:
            self._data = None
