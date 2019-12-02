"""Main circuit object."""
import logging
from .const import (
    GET,
    ID,
    CURRENT_TEMP,
    OPERATION_MODE,
    SUBMIT,
    REFS,
    HA_STATES,
    STATUS,
    TYPE,
    URI,
    REGULAR,
    RESULT,
    OFF,
    CIRCUIT_TYPES,
    ACTIVE_PROGRAM,
    READ,
    WRITE,
    MODE_TO_SETPOINT,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
)
from .helper import BoschSingleEntity
from .errors import ResponseError, RequestError
from .schedule import Schedule

_LOGGER = logging.getLogger(__name__)


class Circuit(BoschSingleEntity):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, requests, attr_id, db, str_obj, _type, current_date):
        """Initialize circuit with requests and id from gateway."""
        name = attr_id.split("/").pop()
        self._db = db[CIRCUIT_TYPES[_type]]
        self._mode_to_setpoint = self._db.get(MODE_TO_SETPOINT)
        super().__init__(name, attr_id, str_obj, requests, _type)
        self._schedule = Schedule(requests, _type, name, current_date)
        self._target_temp = 0
        for key, value in self._db[REFS].items():
            uri = value[ID].format(self.name)
            self._data[key] = {RESULT: {}, URI: uri, TYPE: value[TYPE]}

    @property
    def db_json(self):
        """Give simple json scheme of circuit."""
        return self._db

    @property
    def schedule(self):
        """Retrieve schedule of HC/DHW."""
        return self._schedule

    @property
    def _hastates(self):
        """Get dictionary which converts Bosch states to HA States."""
        return self._db.get(HA_STATES, None)

    @property
    def current_mode(self):
        """Retrieve current mode of Circuit."""
        return self.get_value(OPERATION_MODE)

    @property
    def temp_read(self):
        """Get temp read property."""
        return self._temp_setpoint(READ)

    @property
    def temp_write(self):
        """Get temp write property."""
        return self._temp_setpoint(WRITE)

    def _temp_setpoint(self, key):
        """Check which temp property to use. Key READ or WRITE"""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(key)

    @property
    def available_operation_modes(self):
        """Get Bosch operations modes."""
        return self.get_property(OPERATION_MODE).get(self.strings.allowed_values, {})

    @property
    def operation_mode_type(self):
        """Check if operation mode type is manual or auto."""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(TYPE)

    async def initialize(self):
        """Check each uri if return json with values."""
        await self.update_requested_key(STATUS)

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating HC %s", self.name)
        is_updated = False
        try:
            for key, item in self._data.items():
                if item[TYPE] in (REGULAR, ACTIVE_PROGRAM):
                    result = await self._requests[GET](item[URI])
                    if self.process_results(result, key):
                        is_updated = True
                if item[TYPE] == ACTIVE_PROGRAM:
                    active_program = self.get_activeswitchprogram(result)
                    await self._schedule.update_schedule(active_program)
            temp_read = self.temp_read
            if temp_read:
                result = await self._requests[GET](self._data[temp_read][URI])
                if self.process_results(result, temp_read):
                    is_updated = True
            self._state = True
        except (RequestError, ResponseError):
            self._state = False
        self._update_initialized = True
        return is_updated

    @property
    def setpoint(self):
        """
        Retrieve setpoint in which is currently Circuit.
        Might be equal to operation_mode, might me taken from schedule.
        """
        if self.operation_mode_type == OFF:
            return OFF
        if self.temp_read:
            return self.current_mode
        return self._schedule.get_setpoint_for_mode(self.current_mode, self.operation_mode_type)

    async def update_requested_key(self, key):
        """Update info about Circuit asynchronously."""
        if key in self._data:
            try:
                result = await self._requests[GET](self._data[key][URI])
                self.process_results(result, key)
                self._state = True
            except ResponseError:
                self._state = False

    async def set_operation_mode(self, new_mode):
        """Set operation_mode of Heating Circuit."""
        if self.current_mode == new_mode:
            _LOGGER.warning("Trying to set mode which is already set %s", new_mode)
            return None
        if new_mode in self.available_operation_modes:
            await self._requests[SUBMIT](self._data[OPERATION_MODE][URI], new_mode)
            self._data[OPERATION_MODE][RESULT][self._str.val] = new_mode
            return new_mode
        _LOGGER.warning(
            "You wanted to set %s, but it is not allowed %s",
            new_mode,
            self.available_operation_modes,
        )

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

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            return self.get_value(STATUS)

    @property
    def current_temp(self):
        """Give current temperature of circuit."""
        _LOGGER.debug("Current temp is %s", self.get_property(CURRENT_TEMP))
        temp = self.get_value(CURRENT_TEMP)
        if temp and temp > 0 and temp < 120:
            return temp

    @property
    def temp_units(self):
        """Return units of temperature."""
        return self.get_property(CURRENT_TEMP).get(self._str.units)

    @property
    def ha_modes(self):
        """Retrieve HA modes."""
        return [
            key
            for key, value in self._hastates.items()
            if value in self.available_operation_modes
        ]

    @property
    def ha_mode(self):
        """Retrieve current mode in HA terminology."""
        for _k, _v in self._hastates.items():
            if _v == self.current_mode:
                return _k
        return OFF

    def get_activeswitchprogram(self, result=None):
        """
        Retrieve active program from thermostat.
        If ActiveSwitch program is not present
        then take first one from the list from result.
        """
        active_program = self.get_value(ACTIVE_PROGRAM)
        if active_program:
            return active_program
        return result["references"][0][ID].split("/")[-1]

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        temp_read = self.temp_read
        if self.operation_mode_type == OFF:
            self._target_temp = 0
            return self._target_temp
        if temp_read:
            target_temp = self.get_value(self.temp_read, 0)
            if target_temp > 0:
                self._target_temp = target_temp
                return self._target_temp
        target_temp = self.schedule.get_temp_for_mode(
            self.current_mode, self.operation_mode_type
        )
        if target_temp > 0:
            self._target_temp = target_temp
        return self._target_temp

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        temp_read = self.temp_read
        if temp_read or self.operation_mode_type == OFF:
            return DEFAULT_MIN_TEMP
        else:
            return self.schedule.get_min_temp_for_mode(
                self.current_mode, self.operation_mode_type
            )

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        temp_read = self.temp_read
        if temp_read or self.operation_mode_type == OFF:
            return DEFAULT_MAX_TEMP
        else:
            return self.schedule.get_max_temp_for_mode(
                self.current_mode, self.operation_mode_type
            )

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        if (target_temp
                and self.min_temp < temperature < self.max_temp
                and target_temp != temperature
                and self.temp_write):
            result = await self._requests[SUBMIT](
                self._data[self.temp_write][URI], temperature
            )
            _LOGGER.debug("Set temperature for %s with result %s", self.name, result)
            if result:
                if self.temp_read:
                    self._data[self.temp_read][RESULT][self._str.val] = temperature
                else:
                    self.schedule.cache_temp_for_mode(
                        temperature,
                        self.operation_mode_type,
                        self.current_mode,
                    )
                return True
        return False
