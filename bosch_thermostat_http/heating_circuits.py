""" Heating Circuits module of Bosch thermostat. """
from .const import HC as HEATING_CIRCUITS
from .const import (GET, SUBMIT, NAME, PATH, OPERATION_MODE,
                    HC_SETPOINT_ROOMTEMPERATURE, HC_MANUAL_ROOMSETPOINT,
                    HC_TEMPORARY_TEMPERATURE, HC_CURRENT_ROOMSETPOINT, HC_CURRENT_ROOMTEMPERATURE,
                    HC_OPERATION_MODE, HC)
                    
from .helper import crawl, BoschSingleEntity, BoschEntities


class HeatingCircuits(BoschEntities):
    """
    Heating Circuits object containing multiple Heating Circuit objects.
    """
    def __init__(self, requests):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(requests)

    @property
    def heating_circuits(self):
        """ Get circuits. """
        return self.get_items()



    async def initialize(self, circuits=None):
        """ Initialize HeatingCircuits asynchronously. """
        restoring_data = True
        if not circuits:
            circuits = await self.retrieve_from_module(1, HC)
            restoring_data = False
        for circuit in circuits:
            if "references" in circuit:
                circuit_object = HeatingCircuit(
                    self._requests,
                    circuit['id'],
                    restoring_data
                    )
                circuit_object.add_data(circuit['id'], circuit['references'])
                if not restoring_data:
                    await circuit_object.initialize()
                    circuit['references'] = circuit_object.json_scheme
                self._items.append(circuit_object)


class HeatingCircuit(BoschSingleEntity):
    """ Single Heating Circuits object. """

    def __init__(self, requests, attr_id, restoring_data):
        """
        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        self._requests = requests
        self._circuits_path = {}
        self._references = None
        self._restoring_data = restoring_data
        self._data = {
            HC_CURRENT_ROOMSETPOINT: None,
            HC_CURRENT_ROOMTEMPERATURE: None,
            HC_OPERATION_MODE: None
        }
        self._operation_list = []

        super().__init__(attr_id.split('/').pop(), attr_id, restoring_data, {})

    @property
    def json_scheme(self):
        return self._circuits_path

    async def initialize(self):
        """ Check each uri if return json with values. """
        keys_to_del = []
        for key, value in self._circuits_path.items():
            result_id = await crawl(value, [], 1, self._requests[GET])
            if not result_id:
                keys_to_del.append(key)
        for key in keys_to_del:
            del self._data[key]
            del self._circuits_path[key]
        self._json_scheme_ready = True

    def add_data(self, path, references):
        self._main_data[PATH] = path
        for key in references:
            if self._restoring_data:
                short_id = key
                self._circuits_path[short_id] = references[key]
            else:
                short_id = key['id'].split('/').pop()
                self._circuits_path[short_id] = key["id"]
            self._data[short_id] = None

    async def set_operation_mode(self, new_mode):
        """ Set operation_mode of Heating Circuit. """
        if new_mode in self._operation_list:
            await self._requests[SUBMIT](
                self._circuits_path[OPERATION_MODE],
                new_mode)

    async def set_temperature(self, temperature):
        """ Set temperature of Circuit. """
        if(self._data[HC_OPERATION_MODE] is not None):
            if (self._data[HC_OPERATION_MODE] == 'auto'):
                temp_property = HC_TEMPORARY_TEMPERATURE
            else:
                temp_property = HC_MANUAL_ROOMSETPOINT

        await self._requests[SUBMIT](
            self._circuits_path[temp_property],
            temperature)

    async def update(self):
        """ Update info about Circuit asynchronously. """
        for key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self._data[key] = (result['value'] if 'value' in result
                               else self._data[key])
            if key == OPERATION_MODE:
                self._operation_list = result['allowedValues']

    async def update_requested_keys(self, key):
        """ Update info about Circuit asynchronously. """
        if key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self._data[key] = (result['value'] if 'value' in result
                               else self._data[key])
            if key == OPERATION_MODE:
                if 'allowedValues' not in result:
                    print("TODO: values not present!!")
                    print(result)
                self._operation_list = result['allowedValues']



#    async def update(self):
#        """ Update info about HeatingCircuit asynchronously. """
#        for key in self._data:
#            result = await self._get_request(
#                HEATING_CIRCUIT_LIST[key].format(self.name))
#            self._data[key] = result['value']
#            if key == HC_OPERATION_MODE:
#                self._operation_list = result['allowedValues']

    def set_mode(self, new_mode):
        """ Set mode of HeatingCircuit. """
        if new_mode in self._operation_list:
            await self._requests[SUBMIT](
                self._circuits_path[OPERATION_MODE],
                new_mode)
