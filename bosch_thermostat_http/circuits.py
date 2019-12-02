"""Circuits module of Bosch thermostat."""
from .const import MAIN_URI, ID, CIRCUIT_TYPES
from .helper import BoschEntities
from .circuit import Circuit


class Circuits(BoschEntities):
    """Circuits main object containing multiple Circuit objects."""

    def __init__(self, requests, circuit_type):
        """
        Initialize circuits.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        :param str circuit_type: is it HC or DHW
        """
        self._circuit_type = circuit_type if circuit_type in CIRCUIT_TYPES.keys() else None
        super().__init__(requests)

    @property
    def circuits(self):
        """Get circuits."""
        return self.get_items()

    async def initialize(self, database, str_obj, current_date):
        """Initialize HeatingCircuits asynchronously."""
        if not self._circuit_type:
            return None
        db_prefix = CIRCUIT_TYPES[self._circuit_type]
        uri = database[db_prefix][MAIN_URI]
        circuits = await self.retrieve_from_module(1, uri)
        for circuit in circuits:
            if "references" in circuit:
                circuit_object = self.create_circuit(
                    circuit, database, str_obj, current_date
                )
                if circuit_object:
                    await circuit_object.initialize()
                    if circuit_object.state:
                        self._items.append(circuit_object)

    def create_circuit(self, circuit, database, str_obj, current_date):
        """Create single circuit of given type."""
        if self._circuit_type:
            return Circuit(self._requests, circuit[ID],
                           database, str_obj, self._circuit_type, current_date)
        return None
