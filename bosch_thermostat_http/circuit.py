"""Main circuit object."""
import logging
from .const import (
    ID,
    CURRENT_TEMP,
    OPERATION_MODE,
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
    MODE_TO_SETPOINT,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    SETPOINT,
    MANUAL,
    AUTO
)
from .helper import BoschSingleEntity
from .exceptions import DeviceException
from .schedule import Schedule

_LOGGER = logging.getLogger(__name__)


class BasicCircuit(BoschSingleEntity):

    def __init__(self, connector, attr_id, db, str_obj, _type, bus_type):
        """Basic circuit init."""
        name = attr_id.split("/").pop()
        self._db = db[CIRCUIT_TYPES[_type]]
        self._bus_type = bus_type
        super().__init__(name, connector, attr_id, _type, str_obj)
        self._main_uri = f"/{CIRCUIT_TYPES[_type]}/{self.name}"
        for key, value in self._db[REFS].items():
            uri = f"{self._main_uri}/{value[ID]}"
            self._data[key] = {RESULT: {}, URI: uri, TYPE: value[TYPE]}

    @property
    def db_json(self):
        """Give simple json scheme of circuit."""
        return self._db

    async def update_requested_key(self, key):
        """Update info about Circuit asynchronously."""
        if key in self._data:
            try:
                result = await self._connector.get(self._data[key][URI])
                self.process_results(result, key)
                self._state = True
            except DeviceException:
                self._state = False

    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            return self.get_value(STATUS)

    async def initialize(self):
        """Check each uri if return json with values."""
        await self.update_requested_key(STATUS)


class Circuit(BasicCircuit):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, connector, attr_id, db, str_obj, _type, bus_type, current_date):
        """Initialize circuit with get, put and id from gateway."""
        super().__init__(connector, attr_id, db, str_obj, _type, bus_type)
        self._mode_to_setpoint = self._db.get(MODE_TO_SETPOINT)
        self._schedule = Schedule(connector, _type, self.name, current_date, str_obj, bus_type)
        self._target_temp = 0

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
    def _temp_setpoint(self):
        """Check which temp property to use. Key READ or WRITE"""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(SETPOINT)

    @property
    def available_operation_modes(self):
        """Get Bosch operations modes."""
        return self.get_property(OPERATION_MODE).get(self.strings.allowed_values, {})

    @property
    def operation_mode_type(self):
        """Check if operation mode type is manual or auto."""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(TYPE)

    @property
    def setpoint(self):
        """
        Retrieve setpoint in which is currently Circuit.
        Might be equal to operation_mode, might me taken from schedule.
        """
        if self.operation_mode_type == OFF:
            return OFF
        if self.operation_mode_type == MANUAL:
            return self.current_mode
        return self._schedule.get_setpoint_for_mode(self.current_mode, self.operation_mode_type)

    async def set_operation_mode(self, new_mode):
        """Set operation_mode of Heating Circuit."""
        if self.current_mode == new_mode:
            _LOGGER.warning("Trying to set mode which is already set %s", new_mode)
            return None
        if new_mode in self.available_operation_modes:
            await self._connector.put(self._data[OPERATION_MODE][URI], new_mode)
            self._data[OPERATION_MODE][RESULT][self._str.val] = new_mode
            return new_mode
        _LOGGER.warning(
            "You wanted to set %s, but it is not allowed %s",
            new_mode,
            self.available_operation_modes,
        )

    async def set_ha_mode(self, ha_mode):
        """Helper to set operation mode."""
        old_setpoint = self._temp_setpoint
        old_mode = self.current_mode
        new_mode = await self.set_operation_mode(self._hastates.get(ha_mode))
        different_mode = new_mode != old_mode
        try:
            if (different_mode
                    and old_setpoint != self._temp_setpoint
                    and self.operation_mode_type == MANUAL):
                temp = self.get_value(self._temp_setpoint, 0)
                if temp == 0:
                    result = await self._connector.get(self._data[self._temp_setpoint][URI])
                    self.process_results(result, self._temp_setpoint)
        except DeviceException as err:
            _LOGGER.debug(f"Can't update data for mode {new_mode}. Error: {err}")
            pass
        if different_mode:
            return 1
        return 0


    @property
    def current_temp(self):
        """Give current temperature of circuit."""
        _LOGGER.debug("Current temp of %s is %s", self.name, self.get_property(CURRENT_TEMP))
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
        try:
            return result["references"][0][ID].split("/")[-1]
        except IndexError:
            return None

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        if self.operation_mode_type == OFF:
            self._target_temp = 0
            return self._target_temp
        if self._temp_setpoint:
            target_temp = self.get_value(self._temp_setpoint, 0)
            if target_temp > 0:
                self._target_temp = target_temp
                return self._target_temp
        target_temp = self.schedule.get_temp_for_mode(
            self.current_mode, self.operation_mode_type
        )
        if target_temp >= 0:
            self._target_temp = target_temp
        return self._target_temp

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        if self.operation_mode_type == OFF:
            return DEFAULT_MIN_TEMP
        else:
            return self.schedule.get_min_temp_for_mode(
                self.current_mode, self.operation_mode_type
            )

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        if self.operation_mode_type == OFF:
            return DEFAULT_MAX_TEMP
        else:
            return self.schedule.get_max_temp_for_mode(
                self.current_mode, self.operation_mode_type
            )

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        if self.operation_mode_type == OFF:
            _LOGGER.debug("Not setting temp. Mode is off")
            return False
        if (
            self.min_temp < temperature < self.max_temp
            and target_temp != temperature
        ):
            if self._temp_setpoint:
                target_uri = self._data[self._temp_setpoint][URI]
            elif self.operation_mode_type == AUTO:
                target_uri = self.schedule.get_uri_setpoint_for_mode(self.current_mode, self.operation_mode_type)
            else:
                _LOGGER.debug("Not setting temp. Don't know how")
                return False
            result = await self._connector.put(
                target_uri, temperature
            )
            _LOGGER.debug("Set temperature for %s with result %s", self.name, result)
            if result:
                if self._temp_setpoint:
                    self._data[self._temp_setpoint][RESULT][self._str.val] = temperature
                else:
                    self.schedule.cache_temp_for_mode(
                        temperature,
                        self.operation_mode_type,
                        self.current_mode,
                    )
                return True
        _LOGGER.debug("Setting temperature not allowed in this mode.")
        return False

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating circuit %s", self.name)
        try:
            for key, item in self._data.items():
                if item[TYPE] in (REGULAR, ACTIVE_PROGRAM):
                    result = await self._connector.get(item[URI])
                    self.process_results(result, key)
                if item[TYPE] == ACTIVE_PROGRAM:
                    active_program = self.get_activeswitchprogram(result)
                    if active_program:
                        await self._schedule.update_schedule(active_program)
            if self._temp_setpoint:
                result = await self._connector.get(self._data[self._temp_setpoint][URI])
                self.process_results(result, self._temp_setpoint)
            self._state = True
        except DeviceException as err:
            self._state = False
            self._extra_message = f"Can't update data. Error: {err}"
