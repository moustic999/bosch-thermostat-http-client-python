"""Circuits module of Bosch thermostat."""
from .const import DHW, HC
from .helper import BoschEntities


class Circuits(BoschEntities):
    """Circuits main object containing multiple Circuit objects."""

    def __init__(self, requests, circuit_type):
        """
        Initialize circuits.
        :param dict requests: { GET: get function, SUBMIT: submit function}
        :param str circuit_type: is it HC or DHW
        """
        self._circuit_type = circuit_type
        super().__init__(requests)

    @property
    def circuits(self):
        """Get circuits."""
        return self.get_items()

    async def initialize(self, circuits=None):
        """Initialize HeatingCircuits asynchronously."""
        restoring_data = True
        if not circuits:
            circuits = await self.retrieve_from_module(1,
                                                       self._circuit_type)
            restoring_data = False
        for circuit in circuits:
            if "references" in circuit:
                circuit_object = self.create_circuit(circuit, restoring_data)
                if circuit_object:
                    circuit_object.add_data(circuit['id'],
                                            circuit['references'])
                    if not restoring_data:
                        await circuit_object.initialize()
                        circuit['references'] = circuit_object.json_scheme
                    self._items.append(circuit_object)

    def create_circuit(self, circuit, restoring_data):
        """Create single circuit of given type."""
        if self._circuit_type == DHW:
            from .dhw_circuit import DHWCircuit
            return DHWCircuit(
                self._requests,
                circuit['id'],
                restoring_data
            )
        if self._circuit_type == HC:
            from .heating_circuit import HeatingCircuit
            return HeatingCircuit(
                self._requests,
                circuit['id'],
                restoring_data
            )
        return None
