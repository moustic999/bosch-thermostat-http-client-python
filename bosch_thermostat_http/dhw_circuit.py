"""Heating Circuits module of Bosch thermostat."""
from .const import (SUBMIT, VALUE, WATER_HIGH, WATER_SETPOINT, DHW,
                    HCPROGRAM, OWNPROGRAM, OPERATION_MODE)

from .circuit import Circuit


class DHWCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, db):
        """
        Initialize single circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, db, DHW)

    def __initialize_dict(self, dictionary):
        super().__initialize_dict()
        self._ownprogram = self._dict.get(OWNPROGRAM, OWNPROGRAM)
        self._hcprogram = self._dict.get(HCPROGRAM, HCPROGRAM)

    async def set_temperature(self, temp):
        """Set temperature of Circuit."""
        t_temp = self.target_temperature
        op_mode = self.get_value(OPERATION_MODE)
        if (t_temp[self._min_str] < temp < t_temp[self._max_str] and op_mode):
            if op_mode == self._ownprogram:
                target = WATER_SETPOINT
            elif op_mode == self._hcprogram:
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
            return (temp[VALUE], temp[self._min_str], temp[self._max_str])
        setpoint_temp = self.get_value(WATER_SETPOINT, -1)
        if all(k in temp_levels_high for k in (self._min_str, self._max_str)):
            return (setpoint_temp, temp[self._min_str], temp[self._max_str])
        return (setpoint_temp, 0, 99)
