"""Heating Circuits module of Bosch thermostat."""
import logging
from .const import (SUBMIT, HC_MANUAL_ROOMSETPOINT,
                    HC_TEMPORARY_TEMPERATURE, HC_CURRENT_ROOMSETPOINT,
                    OPERATION_MODE, HC_MODE_AUTO, VALUE,
                    MINVALUE, MAXVALUE, HC_ROOMTEMPERATURE, UNITS)
from .circuit import Circuit

from .helper import parse_float_value

_LOGGER = logging.getLogger(__name__)


class HeatingCircuit(Circuit):
    """Single Heating Circuits object."""

    def __init__(self, requests, attr_id, restoring_data):
        """
        Initialize heating circuit.

        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """
        super().__init__(requests, attr_id, restoring_data)
        self._type = "hc"

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        if self._data[OPERATION_MODE][VALUE]:
            temp_property = (HC_TEMPORARY_TEMPERATURE if
                             self._data[OPERATION_MODE][VALUE] ==
                             HC_MODE_AUTO else HC_MANUAL_ROOMSETPOINT)
            await self._requests[SUBMIT](
                self._circuits_path[temp_property],
                temperature)

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        # temp = self.get_property(HC_TEMPORARY_TEMPERATURE)
        # temp_val = temp.get(VALUE, -1)
        # if temp.get(MINVALUE, 5) < temp_val < temp.get(MAXVALUE, 30):
        #    return temp_val
        _LOGGER.debug("Target temp is %s",
                      self._data[HC_CURRENT_ROOMSETPOINT].get(VALUE))
        return self._data[HC_CURRENT_ROOMSETPOINT].get(VALUE)

    @property
    def current_temp(self):
        """Give current temperautre of Heating circuit."""
        _LOGGER.debug("Current temp is %s",
                      self.get_property(HC_ROOMTEMPERATURE))
        return parse_float_value(self.get_property(HC_ROOMTEMPERATURE))

    @property
    def temp_units(self):
        """Return units of temperaure."""
        return self.get_property(HC_ROOMTEMPERATURE).get(UNITS)
