""" Circuits module of Bosch thermostat. """
from .const import (GET, SUBMIT, NAME, PATH, OPERATION_MODE)
from .helper import crawl, BoschEntities, BoschSingleEntity


class Circuits(BoschEntities):
    """
    Circuits main object containing multiple Circuit objects.
    """
    def __init__(self, requests, circuit_type):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        :param str circuit_type: is it HC or DHW
        """
        self._circuit_type = circuit_type
        super().__init__(requests)

    def get_circuits(self):
        """ Get circuits. """
        return self.get_items()

    async def initialize(self, circuits=None):
        """ Initialize HeatingCircuits asynchronously. """
        restoring_data = True
        if not circuits:
            circuits = await self.retrieve_from_module(1, self._circuit_type)
            restoring_data = False
        for circuit in circuits:
            if "references" in circuit:
                circuit_object = Circuit(
                    self._requests,
                    circuit['id'].split('/').pop()
                    )
                circuit_object.add_data(circuit['id'], circuit['references'])
                # if not restoring_data:
                    # await circuit_object.initialize()
                self._items.append(circuit_object)


class Circuit(BoschSingleEntity):
    """ Single Circuit object. """

    def __init__(self, requests, name):
        """
        :param dict requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of heating circuit.

        """
        self._requests = requests
        self._circuits_path = {}
        self._operation_list = []
        self._operation_address = None
        super().__init__(name, {})

    def add_data(self, path, references):
        self._main_data[PATH] = path
        for key in references:
            self._data[key['id'].split('/').pop()] = None
            self._circuits_path[key['id'].split('/').pop()] = key["id"]

    async def update(self):
        """ Update info about Circuit asynchronously. """
        for key in self._data:
            result = await self._requests[GET](
                self._circuits_path[key])
            self._data[key] = (result['value'] if 'value' in result
                               else self._data[key])
            if key == OPERATION_MODE:
                self._operation_list = result['allowedValues']
                self._operation_address = self._circuits_path[key]

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

    @property
    def allow_operations(self):
        return self._operation_list

    def set_mode(self, new_mode):
        """ Set mode of Circuit. """
        if self._operation_address and new_mode in self._operation_list:
            self._requests[SUBMIT](
                self._operation_address,
                new_mode)
