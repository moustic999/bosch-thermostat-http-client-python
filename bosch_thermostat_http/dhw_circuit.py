"""Heating Circuits module of Bosch thermostat."""
from .const import (
    SUBMIT,
    VALUE,
    WATER_HIGH,
    AUTO_SETPOINT,
    DHW,
    OPERATION_MODE,
    URI,
    RESULT, ACTIVE_PROGRAM, ID, MANUAL, OFF, TEMP
)

from .circuit import Circuit


class DHWCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, db, str_obj, current_date):
        """
        Initialize single circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, db, str_obj, DHW, current_date)

    async def set_temperature(self, temp):
        """Set temperature of Circuit."""
        (t_temp, min_temp, max_temp) = self.target_temperature
        op_mode = self.get_value(OPERATION_MODE)
        if min_temp < temp < max_temp and op_mode and t_temp != temp:
            await self._requests[SUBMIT](self._data[WATER_HIGH][URI], temp)
            self._data[WATER_HIGH][RESULT][self._str.val] = temp
            return True
        return False

        