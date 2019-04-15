"""Heating Circuits module of Bosch thermostat."""
from .const import (SUBMIT, MINVALUE, MAXVALUE, VALUE, DHW_HIGHTTEMP_LEVEL,
                    DHW_CURRENT_SETPOINT, DHW_OWNPROGRAM, OPERATION_MODE)

from .circuit import Circuit
from .helper import parse_float_value


class DHWCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, restoring_data):
        """
        Initialize single circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, restoring_data)
        self._type = "dhw"

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        t_temp = self.target_temperature
        if (t_temp[MINVALUE] < temperature < t_temp[MAXVALUE] and
                self._data[OPERATION_MODE][VALUE]):
            if self._data[OPERATION_MODE] == DHW_OWNPROGRAM:
                target = DHW_CURRENT_SETPOINT
            elif self._data[OPERATION_MODE] == DHW_OWNPROGRAM:
                target = DHW_HIGHTTEMP_LEVEL
            if target:
                await self._requests[SUBMIT](
                    self._circuits_path[target], temperature)
                return True
        return False

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        temp_levels_high = self.get_property(DHW_HIGHTTEMP_LEVEL)
        temp = parse_float_value(temp_levels_high, False, True)
        if temp:
            return (temp[VALUE], temp[MINVALUE], temp[MAXVALUE])
        setpoint_temp = self._data[DHW_CURRENT_SETPOINT].get(VALUE)
        if setpoint_temp:
            if all(k in temp_levels_high for k in (MINVALUE, MAXVALUE)):
                return (setpoint_temp, temp[MINVALUE], temp[MAXVALUE])
            return (setpoint_temp, 0, 99)
        return (-1, 0, 99)
