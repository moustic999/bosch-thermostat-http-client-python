"""Heating Circuits module of Bosch thermostat."""
import logging
from .const import SUBMIT, HC, OPERATION_MODE, URI, RESULT
from .circuit import Circuit

_LOGGER = logging.getLogger(__name__)


class HeatingCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, db, str_obj, current_date):
        """
        Initialize heating circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, db, str_obj, HC, current_date)

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        if target_temp and temperature != target_temp:
            result = await self._requests[SUBMIT](
                self._data[self.temp_write][URI], temperature
            )
            _LOGGER.debug("Set temperature for HC %s with result %s", self.name, result)
            if result:
                if self.temp_read:
                    self._data[self.temp_read][RESULT][self._str.val] = temperature
                else:
                    self.schedule.cache_temp_for_mode(
                        temperature,
                        self.operation_mode_type,
                        self.get_value(OPERATION_MODE),
                    )
                return True
        return False

    async def set_ha_mode(self, ha_mode):
        """Helper to set operation mode."""
        c_temp_read = self.temp_read
        c_temp_write = self.temp_write
        old_mode = self.current_mode
        new_mode = await self.set_operation_mode(self._hastates.get(ha_mode))
        if (self.temp_read != c_temp_read) or (self.temp_write != c_temp_write):
            return 2
        if new_mode != old_mode:
            return 1
        return 0
