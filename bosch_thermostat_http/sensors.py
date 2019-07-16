"""Sensors of Bosch thermostat."""
from .const import (SENSORS, APPLIANCES, GET, PATH, ID,
                    NAME, SENSORS_EXLUDE, HEATSOURCES_EXLUDE,
                    APPLIANCES_EXLUDE, HEATSOURCES)
from .helper import BoschSingleEntity, BoschEntities, check_sensor
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

    async def initialize(self, sensors=None):
        """
        Asynchronously initialize all sensors.

        :param sensors dict if declared then restore sensors from it.
                            If not download data from device.
        """
        restoring_data = True
        if not sensors:
            sensors = (await self.retrieve_from_module(2, SENSORS,
                                                       SENSORS_EXLUDE) +
                       await self.retrieve_from_module(2, APPLIANCES,
                                                       APPLIANCES_EXLUDE) +
                       await self.retrieve_from_module(2, HEATSOURCES,
                                                       HEATSOURCES_EXLUDE))
            restoring_data = False
        for sensor in sensors:
            sensor_check_status = (check_sensor(sensor)
                                   if not restoring_data else True)
            if sensor_check_status:
                self.register_sensor(sensor[NAME],
                                     sensor[ID], restoring_data)

    def register_sensor(self, name, path, restoring_data):
        """Register sensor for the module."""
        attr_id = path.split('/').pop()
        if attr_id not in self._items:
            self._items[attr_id] = Sensor(self._requests, attr_id,
                                          name, path, restoring_data)


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    def __init__(self, requests, attr_id, name, path, restoring_data):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        self._requests = requests
        super().__init__(name, attr_id, restoring_data, path)
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
        except Response404Error:
            raise SensorNoLongerAvailable("This sensor is no available.")
        except ResponseError:
            self._data = None
