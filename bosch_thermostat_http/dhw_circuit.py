""" Heating Circuits module of Bosch thermostat. """
from .const import DHW
from .const import (SUBMIT, NAME, OPERATION_MODE,
                    DHW_CURRENT_SETPOINT, HC_MANUAL_ROOMSETPOINT,
                    HC_TEMPORARY_TEMPERATURE,
                    HC_OPERATION_MODE, HC_MODE_AUTO, VALUE,
                    MINVALUE, MAXVALUE, ALLOWED_VALUES, UNITS)

from .circuit import Circuit


class DHWCircuit(Circuit):
    """ Single Heating Circuits object. """

    def __init__(self, requests, attr_id, restoring_data):
        """
        :param obj get_request:    function to retrieve data from thermostat.
        :param obj submit_request: function to send data to thermostat.
        :param str hc_name: name of heating circuit.
        """

        super().__init__(requests, attr_id, restoring_data)
        self._type = "dhw"

    async def set_operation_mode(self, new_mode):
        """ Set operation_mode of Heating Circuit. """
        if (self._data[OPERATION_MODE][VALUE] != new_mode and
                ALLOWED_VALUES in self._data[OPERATION_MODE] and
                new_mode in self._data[OPERATION_MODE][ALLOWED_VALUES]):
            await self._requests[SUBMIT](
                self._circuits_path[OPERATION_MODE],
                new_mode)

    async def set_temperature(self, temperature):
        """ Set temperature of Circuit. """
        if self._data[HC_OPERATION_MODE][VALUE]:
            temp_property = (HC_TEMPORARY_TEMPERATURE if
                             self._data[HC_OPERATION_MODE] == HC_MODE_AUTO
                             else HC_MANUAL_ROOMSETPOINT)
            await self._requests[SUBMIT](
                self._circuits_path[temp_property],
                temperature)

    def get_target_temperature(self):
        """ Get target temperature of Circtuit. Temporary or Room set point."""
        return self._data[DHW_CURRENT_SETPOINT].get(VALUE)

#    async def update(self):
#        """ Update info about HeatingCircuit asynchronously. """
#        for key in self._data:
#            result = await self._get_request(
#                HEATING_CIRCUIT_LIST[key].format(self.name))
#            self._data[key] = result['value']
#            if key == HC_OPERATION_MODE:
#                self._operation_list = result['allowedValues']
