"""Heating Circuits module of Bosch thermostat."""
import logging
from .const import (
    SUBMIT,
    HC, GET,
    AUTO_SETPOINT, AUTO, MANUAL,
    MANUAL_SETPOINT,
    OPERATION_MODE,
    AUTO_SETTEMP, STATUS, CURRENT_TEMP, PRESETS, OFF
)
from .circuit import Circuit
from .errors import ResponseError

_LOGGER = logging.getLogger(__name__)

UPDATE_KEYS = [
    OPERATION_MODE,
    STATUS,
    CURRENT_TEMP,
    AUTO_SETTEMP,
    MANUAL_SETPOINT,
    AUTO_SETPOINT,
]

MODE_TO_SETPOINT = "mode_to_setpoint"
READ = "read"
WRITE = "write"

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
        self._presets = self._db.get(PRESETS)
        self._mode_to_setpoint = self._db.get(MODE_TO_SETPOINT)

    @property
    def temp_read(self,):
        return self.temp_setpoint(READ)

    @property
    def temp_write(self):
        return self.temp_setpoint(WRITE)

    def temp_setpoint(self, key):
        """Check whith temp property. Use only for setting temp. Key READ or WRITE"""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(key)

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating HC %s", self.name)
        is_updated = False
        for key in self._data:
            if key in (AUTO, MANUAL) and self.operation_mode_type != key:
                continue
            try:
                result = await self._requests[GET](
                    self._circuits_path[key])
                if self.process_results(result, key):
                    is_updated = True
            except ResponseError:
                pass
        self._updated_initialized = True
        return is_updated

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        result = await self._requests[SUBMIT](self._circuits_path[self.temp_write],
                                              temperature)
        if result:
            _LOGGER.debug("TEMP SETPOINT %s", self.temp_setpoint)
            self._data[self.temp_read][self._str.val] = temperature
            return True
        return False

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        _LOGGER.debug(f"Target temp {AUTO_SETPOINT} is {self.get_value(self.temp_read)} in {self.get_value(OPERATION_MODE)}")
        return self.get_value(self.temp_read, 0)
    
    @property
    def operation_mode_type(self):
        if self.current_mode in self._presets.get(MANUAL):
            return MANUAL
        if self.current_mode in self._presets.get(AUTO):
            return AUTO

    @property
    def hvac_modes(self):
        return [key for key, value in self.hastates.items()
                if value in self.available_operation_modes]

    @property
    def hvac_mode(self):
        for _k, _v in self.hastates.items():
            if _v == self.current_mode:
                return _k
        return OFF

    async def set_hvac_mode(self, hvac_mode):
        """Helper to set operation mode."""
        c_temp_read = self.temp_read
        c_temp_write = self.temp_write
        old_mode = self.current_mode
        new_mode = await self.set_operation_mode(self.hastates.get(hvac_mode))
        if (self.temp_read != c_temp_read) or (self.temp_write != c_temp_write):
            return 2
        if new_mode != old_mode:
            return 1
        return 0

    #  def operation_list_converter(self, op_list):
    #     return [self._hastates_inv.get(value) for value in op_list]




        