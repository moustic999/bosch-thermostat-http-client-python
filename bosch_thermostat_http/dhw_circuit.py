"""Heating Circuits module of Bosch thermostat."""
from .const import (SUBMIT, VALUE, WATER_HIGH, WATER_SETPOINT, DHW,
                    OPERATION_MODE)

from .circuit import Circuit


class DHWCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, db, str_obj):
        """
        Initialize single circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, db, str_obj, DHW)

    async def set_temperature(self, temp):
        """Set temperature of Circuit."""
        t_temp = self.target_temperature
        op_mode = self.get_value(OPERATION_MODE)
        if (t_temp[self._str.min] < temp < t_temp[self._str.max] and op_mode):
            if op_mode == self._str.ownprogram:
                target = WATER_SETPOINT
            elif op_mode == self._str.hcprogram:
                target = WATER_HIGH
            if target:
                await self._requests[SUBMIT](
                    self._circuits_path[target], temp)
                return True
        return False

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        temp_levels_high = self.get_property(WATER_HIGH)
        temp = self.parse_float_value(temp_levels_high, False, True)
        if temp:
            return (temp[VALUE], temp[self._str.min], temp[self._str.max])
        setpoint_temp = self.get_value(WATER_SETPOINT, -1)
        if all(k in temp_levels_high for k in (self._str.min, self._str.max)):
            return (setpoint_temp, temp[self._str.min], temp[self._str.max])
        return (setpoint_temp, 0, 99)
