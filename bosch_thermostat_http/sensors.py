from .const import SENSOR_NAME, SENSOR_TYPE, SENSOR_VALUE, SENSOR_UNIT


class Sensors:
    def __init__(self, get_request):
        self._get_request = get_request
        self._items = []

    async def update(self):
        for item in self._items:
            await item.update()

    def get_sensors(self):
        return self._items

    def register_sensor(self, name, path):
        self._items.append(Sensor(self._get_request, name, path))


class Sensor:
    def __init__(self, get_request, name, path):
        self._get_request = get_request
        self._data = {
            SENSOR_NAME: name,
            SENSOR_TYPE: None,
            SENSOR_VALUE: None,
            SENSOR_UNIT: None
        }
        self._path = path

    def get_property(self, property_name):
        if property_name in self._data:
            return self._data[property_name]
        return None

    async def update(self):
        data = await self._get_request(self._path)
        self._data[SENSOR_VALUE] = data['value']
        self._data[SENSOR_TYPE] = data['type']
        self._data[SENSOR_UNIT] = data['unitOfMeasure']
