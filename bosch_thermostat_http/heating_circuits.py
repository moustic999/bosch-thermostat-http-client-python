""" Heating Circuits module of Bosch thermostat. """
from .const import HC as HEATING_CIRCUITS
from .const import (HC_CURRENT_ROOMSETPOINT, HC_CURRENT_ROOMTEMPERATURE,
                    HC_OPERATION_MODE, HEATING_CIRCUIT_LIST,
                    HEATING_CIRCUIT_OPERATION_MODE)


class HeatingCircuits:
    """
    Heating Circuits object containing multiple Heating Circuit objects.
    """
    def __init__(self, get_request, submit_request):
        """
        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        """
        self._items = []
        self._get_request = get_request
        self._submit_request = submit_request

    async def initialize(self):
        """ Initialize HeatingCircuits asynchronously. """
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
        """ Update all heating circuits. """
        for item in self._items:
            await item.update()


class HeatingCircuit:
    """ Single Heating Circuits object. """

    def __init__(self, get_request, _submit_request, hc_name):
        """
        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        self._get_request = get_request
        self._submit_request = _submit_request
        self.name = hc_name
        self._data = {
            HC_CURRENT_ROOMSETPOINT: None,
            HC_CURRENT_ROOMTEMPERATURE: None,
            HC_OPERATION_MODE: None
        }
        self._operation_list = []

    async def update(self):
        """ Update info about HeatingCircuit asynchronously. """
        for key in self._data:
            result = await self._get_request(
                HEATING_CIRCUIT_LIST[key].format(self.name))
            self._data[key] = result['value']
            if key == HC_OPERATION_MODE:
                self._operation_list = result['allowedValues']

    def set_mode(self, new_mode):
        """ Set mode of HeatingCircuit. """
        if new_mode in self._operation_list:
            self._submit_request(
                HEATING_CIRCUIT_OPERATION_MODE.format(self.name),
                new_mode)
