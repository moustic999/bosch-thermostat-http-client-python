"""Circuits module of Bosch thermostat."""
from .const import ID, CIRCUIT_TYPES, HC, DHW, SC
from .helper import BoschEntities, BoschSingleEntity
from .circuit import Circuit, BasicCircuit


class Circuits(BoschEntities):
    """Circuits main object containing multiple Circuit objects."""

    def __init__(self, connector, circuit_type, bus_type):
        """
        Initialize circuits.

        :param obj get -> get function
        :param obj put -> put http function
        :param str circuit_type: is it HC or DHW
        """
        self._circuit_type = circuit_type if circuit_type in CIRCUIT_TYPES.keys() else None
        self._connector = connector
        self._bus_type = bus_type
        super().__init__(connector.get)

    @property
    def circuits(self):
        """Get circuits."""
        return self.get_items()

    async def initialize(self, database, str_obj, current_date):
        """Initialize HeatingCircuits asynchronously."""
        if not self._circuit_type:
            return None
        db_prefix = CIRCUIT_TYPES[self._circuit_type]
        if db_prefix not in database:
            return None
        circuits = await self.retrieve_from_module(1, f"/{db_prefix}")
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
        if self._circuit_type in (HC, DHW):
            return Circuit(self._connector, circuit[ID],
                           database, str_obj, self._circuit_type,
                           self._bus_type, current_date)
        elif self._circuit_type == SC:
            return BasicCircuit(self._connector, circuit[ID],
                                database, str_obj, self._circuit_type,
                                self._bus_type)
        return None
