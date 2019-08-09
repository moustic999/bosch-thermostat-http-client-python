"""Heating Circuits module of Bosch thermostat."""
import logging
from .const import (SUBMIT, HC, ROOMSETPOINT, MANUALROOMSETPOINT,
                    OPERATION_MODE, ROOMTEMP)
from .circuit import Circuit


_LOGGER = logging.getLogger(__name__)


class HeatingCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, db, str_obj):
        """
        Initialize heating circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, db, str_obj, HC)

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        operation_mode = self.get_value(OPERATION_MODE)
        if operation_mode:
            temp_property = (ROOMSETPOINT if operation_mode ==
                             self._str.auto else MANUALROOMSETPOINT)
            await self._requests[SUBMIT](
                self._circuits_path[temp_property],
                temperature)

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        _LOGGER.debug("Target temp is %s",
                      self._data.get(ROOMSETPOINT, {}).get(
                          self._str.val, None))
        return self._data.get(ROOMSETPOINT, {}).get(self._str.val, None)

    @property
    def current_temp(self):
        """Give current temperautre of Heating circuit."""
        _LOGGER.debug("Current temp is %s",
                      self.get_property(ROOMTEMP))
        return self.parse_float_value(self.get_property(ROOMTEMP))

    @property
    def temp_units(self):
        """Return units of temperaure."""
        return self.get_property(ROOMTEMP).get(self._str.units)
