from .const import (HC as HEATING_CIRCUITS, HEATING_CIRCUIT_LIST,
                    HEATING_CIRCUIT_OPERATION_MODE,
                    HC_CURRENT_ROOMSETPOINT, HC_CURRENT_ROOMTEMPERATURE,
                    HC_OPERATION_MODE)


class HeatingCircuits:
    def __init__(self, get_request, submit_request):
        self._items = []
        self._get_request = get_request
        self._submit_request = submit_request

    async def initialize(self):
        circuits_json = await self._get_request(HEATING_CIRCUITS)
        print(circuits_json)
        circuits = circuits_json['references']
        for circuit_id in circuits:
            name = circuit_id['id'].split('/').pop()
            heating_circuit = HeatingCircuit(
                self._get_request,
                self._submit_request,
                name)
            self._items.append(heating_circuit)

    async def update(self):
        for item in self._items:
            await item.update()


class HeatingCircuit:

    def __init__(self, request, submit, hc_name):
        self._request = request
        self._submit = submit
        self.name = hc_name
        self._data = {
            HC_CURRENT_ROOMSETPOINT: None,
            HC_CURRENT_ROOMTEMPERATURE: None,
            HC_OPERATION_MODE: None
        }
        self._operation_list = []

    async def update(self):
        for key in self._data:
            result = await self._request(
                HEATING_CIRCUIT_LIST[key].format(self.name))
            self._data[key] = result['value']
            if key == HC_OPERATION_MODE:
                self._operation_list = result['allowedValues']

    def set_mode(self, new_mode):
        if new_mode in self._operation_list:
            self._submit(
                HEATING_CIRCUIT_OPERATION_MODE.format(self.name),
                new_mode)
