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
    RESULT,
    OFF,
    CIRCUIT_TYPES,
    ACTIVE_PROGRAM,
    MODE_TO_SETPOINT,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    SETPOINT,
    MANUAL,
    AUTO,
    CURRENT_SETPOINT,
    CAN,
    MAX_REF,
    MIN_REF,
    HA_NAME,
    BOSCH_NAME,
    MIN_VALUE,
    MAX_VALUE,
    VALUE,
)
from .helper import BoschSingleEntity
from .exceptions import DeviceException
from .schedule import Schedule

_LOGGER = logging.getLogger(__name__)


class OperationModeHelper:
    def __init__(self, name, mode_to_setpoint, str_obj):
        self.name = name
        self._str = str_obj
        self._operation_mode = {}
        self._uri = False
        self._mode_to_setpoint = mode_to_setpoint

    def init_op_mode(self, operation_mode, uri):
        self._operation_mode = operation_mode
        self._uri = uri

    def set_new_operation_mode(self, value):
        self._operation_mode[self._str.val] = value

    @property
    def uri(self):
        return self._uri

    @property
    def is_set(self):
        return self._uri

    @property
    def available_modes(self):
        """Get Bosch operations modes."""
        return self._operation_mode.get(self._str.allowed_values, {})

    def find_in_available_modes(self, modes):
        for mode in modes:
            if mode in self.available_modes:
                return mode

    @property
    def current_mode(self):
        """Retrieve current mode of Circuit."""
        return self._operation_mode.get(self._str.val, None)

    def temp_setpoint(self, mode=None):
        """Check which temp property to use. Key READ or WRITE"""
        mode = self.current_mode if not mode else mode
        return self._mode_to_setpoint.get(mode, {}).get(SETPOINT)

    @property
    def mode_type(self):
        """Check if operation mode type is manual or auto."""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(TYPE)

    @property
    def is_off(self):
        return self.mode_type == OFF

    @property
    def is_manual(self):
        return self.mode_type == MANUAL

    @property
    def is_auto(self):
        return self.mode_type == AUTO


class BasicCircuit(BoschSingleEntity):
    def __init__(self, connector, attr_id, db, str_obj, _type, bus_type):
        """Basic circuit init."""
        name = attr_id.split("/").pop()
        self._db = db[CIRCUIT_TYPES[_type]]
        self._bus_type = bus_type
        super().__init__(name, connector, attr_id, _type, str_obj)
        self._main_uri = f"/{CIRCUIT_TYPES[_type]}/{self.name}"
        self._operation_mode = {}
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
            state = self.get_value(STATUS)
            if state:
                return state
            if self._bus_type == CAN:
                if self.get_value(CURRENT_SETPOINT):
                    return True

    async def initialize(self):
        """Check each uri if return json with values."""
        await self.update_requested_key(STATUS)


class Circuit(BasicCircuit):
    """Parent object for circuit of type HC or DHW."""

    def __init__(self, connector, attr_id, db, str_obj, _type, bus_type, current_date):
        """Initialize circuit with get, put and id from gateway."""
        super().__init__(connector, attr_id, db, str_obj, _type, bus_type)
        self._op_mode = OperationModeHelper(
            self.name, self._db.get(MODE_TO_SETPOINT), str_obj
        )
        self._schedule = Schedule(
            connector,
            _type,
            self.name,
            current_date,
            str_obj,
            bus_type,
            self._db,
            self._op_mode,
        )
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
    def setpoint(self):
        """
        Retrieve setpoint in which is currently Circuit.
        Might be equal to operation_mode, might me taken from schedule.
        """
        if self._op_mode.is_off:
            return OFF
        if self._op_mode.is_manual:
            return self._op_mode.current_mode
        found_setpoint = self._schedule.get_setpoint_for_current_mode()
        if found_setpoint == ACTIVE_PROGRAM:
            found_setpoint = self.schedule.active_program
        return found_setpoint

    async def set_service_call(self, uri, value):
        """WARNING! It doesn't check if value you send is good!."""
        _LOGGER.info(f"Sending service call {uri} with {value}")
        uri = f"{self._main_uri}/{uri}"
        val = await self._connector.put(uri, value)
        return val

    async def set_operation_mode(self, new_mode):
        """Set operation_mode of Heating Circuit."""
        if self._op_mode.current_mode == new_mode:
            _LOGGER.warning("Trying to set mode which is already set %s", new_mode)
            return None
        if new_mode in self._op_mode.available_modes:
            await self._connector.put(self._op_mode.uri, new_mode)
            self._op_mode.set_new_operation_mode(new_mode)
            return new_mode
        _LOGGER.warning(
            "You wanted to set %s, but it is not allowed %s",
            new_mode,
            self._op_mode.available_modes,
        )

    def _find_ha_mode(self, ha_mode):
        for v in self._hastates:
            if v[HA_NAME] == ha_mode:
                return v[BOSCH_NAME]

    @property
    def _temp_setpoint(self):
        return self._op_mode.temp_setpoint()

    async def set_ha_mode(self, ha_mode):
        """Helper to set operation mode."""
        old_setpoint = self._temp_setpoint
        old_mode = self._op_mode.current_mode
        bosch_mode = self._op_mode.find_in_available_modes(self._find_ha_mode(ha_mode))
        new_mode = await self.set_operation_mode(bosch_mode)
        different_mode = new_mode != old_mode
        try:
            if (
                different_mode
                and old_setpoint != self._temp_setpoint
                and self._op_mode.is_manual
            ):
                temp = self.get_value(self._temp_setpoint, 0)
                if temp == 0:
                    result = await self._connector.get(
                        self._data[self._temp_setpoint][URI]
                    )
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
        _LOGGER.debug(
            "Current temp of %s is %s",
            self.name.upper(),
            self.get_property(CURRENT_TEMP),
        )
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
            v[HA_NAME]
            for v in self._hastates
            if any(x in self._op_mode.available_modes for x in v[BOSCH_NAME])
        ]

    @property
    def ha_mode(self):
        """Retrieve current mode in HA terminology."""
        for v in self._hastates:
            for x in v[BOSCH_NAME]:
                if x == self._op_mode.current_mode:
                    return v[HA_NAME]
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
        if self._op_mode.is_off:
            self._target_temp = 0
            return self._target_temp
        if self._temp_setpoint:
            target_temp = self.get_value(self._temp_setpoint, 0)
            if target_temp > 0:
                self._target_temp = target_temp
                return self._target_temp
        target_temp = self.schedule.get_temp_for_current_mode()
        if target_temp == ACTIVE_PROGRAM:
            target_temp = self.get_value_from_active_setpoint(VALUE)
        if target_temp >= 0:
            self._target_temp = target_temp
        return self._target_temp

    @property
    def active_program_setpoint(self):
        return self._op_mode.temp_setpoint(self.schedule.active_program)

    def get_value_from_active_setpoint(self, prop_name):
        activeSetpointValue = self.get_property(self.active_program_setpoint)
        default = 0
        if prop_name == MIN_VALUE:
            default = DEFAULT_MIN_TEMP
        elif prop_name == MAX_VALUE:
            default = DEFAULT_MAX_TEMP
        return activeSetpointValue.get(prop_name, default)

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MIN_TEMP
        else:
            setpoint_min = self.get_property(self._temp_setpoint).get(
                MIN_VALUE, self.get_value(self._db[MIN_REF], False)
            )
            min_temp = self.schedule.get_min_temp_for_mode(setpoint_min)
            if min_temp == ACTIVE_PROGRAM:
                min_temp = self.get_value_from_active_setpoint(MIN_VALUE)
            return min_temp

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MAX_TEMP
        else:
            setpoint_max = self.get_property(self._temp_setpoint).get(
                MAX_VALUE, self.get_value(self._db[MAX_REF], False)
            )
            max_temp = self.schedule.get_max_temp_for_mode(setpoint_max)
            if max_temp == ACTIVE_PROGRAM:
                max_temp = self.get_value_from_active_setpoint(MAX_VALUE)
            return max_temp

    async def set_temperature(self, temperature):
        """Set temperature of Circuit."""
        target_temp = self.target_temperature
        active_program_not_in_schedule = False
        if self._op_mode.is_off:
            return False
        if self.min_temp < temperature < self.max_temp and target_temp != temperature:
            if self._temp_setpoint:
                target_uri = self._data[self._temp_setpoint][URI]
            elif self._op_mode.is_auto:
                target_uri = self.schedule.get_uri_setpoint_for_current_mode()
                if target_uri == ACTIVE_PROGRAM:
                    active_program_not_in_schedule = True
                    target_uri = self._data[self.active_program_setpoint][URI]
            if not target_uri:
                _LOGGER.debug("Not setting temp. Don't know how")
                return False
            result = await self._connector.put(target_uri, temperature)
            _LOGGER.debug("Set temperature for %s with result %s", self.name, result)
            if result:
                if self._temp_setpoint:
                    self._data[self._temp_setpoint][RESULT][self._str.val] = temperature
                elif not active_program_not_in_schedule:
                    self.schedule.cache_temp_for_mode(temperature)
                return True
        _LOGGER.error(
            "Setting temperature not allowed in this mode. Temperature is probably out of range MIN-MAX!"
        )
        return False

    async def update(self):
        """Update info about Circuit asynchronously."""
        _LOGGER.debug("Updating circuit %s", self.name)
        last_item = list(self._data.keys())[-1]
        for key, item in self._data.items():
            is_operation_type = item[TYPE] == OPERATION_MODE
            try:
                result = await self._connector.get(item[URI])
                self.process_results(result, key)
            except DeviceException:
                continue
            if item[TYPE] == ACTIVE_PROGRAM:
                active_program = self.get_activeswitchprogram(result)
                if active_program:
                    await self._schedule.update_schedule(active_program)
            if not self._op_mode.is_set and is_operation_type and result:
                self._op_mode.init_op_mode(
                    self.process_results(result, key, True), item[URI]
                )
            if key == last_item:
                self._state = True
