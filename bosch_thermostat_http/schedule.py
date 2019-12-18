"""Logic to converse schedule."""
import logging
from datetime import datetime

from .const import (
    GET,
    DAYOFWEEK,
    MODE,
    START,
    STOP,
    SETPOINT,
    TIME,
    VALUE,
    TEMP,
    AUTO,
    SETPOINT_PROP,
    SWITCH_POINTS,
    SWITCHPROGRAM,
    MIDNIGHT,
    DAYS, DAYS_INT,
    DAYS_INDEXES, DAYS_INV,
    CIRCUIT_TYPES, ID, MAX, MIN, MAX_VALUE, MIN_VALUE, MANUAL
)
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


def sort_switchpoints(dic):
    day = dic[DAYOFWEEK]
    return (DAYS_INT.index(day), dic[TIME])



class Schedule:
    """Scheduler logic."""

    def __init__(self, connector, circuit_type, circuit_name, current_time):
        """Initialize schedule handling of Bosch gateway."""
        self._connector = connector
        self._active_program = None
        self._circuit_type = CIRCUIT_TYPES[circuit_type]
        self._circuit_name = circuit_name
        self._setpoints_temp = {}
        self._switch_points = None
        self._active_setpoint = None
        self._active_program_uri = None
        self._time = None
        self._time_retrieve = current_time

    async def update_schedule(self, active_program):
        """Update schedule from Bosch gateway."""
        self._active_program = active_program
        self._active_program_uri = SWITCHPROGRAM.format(
            self._circuit_type, self._circuit_name, active_program
        )
        try:
            self._time = await self._time_retrieve()
            result = await self._connector.get(self._active_program_uri)
            await self._parse_schedule(
                result.get(SWITCH_POINTS), result.get(SETPOINT_PROP)
            )
        except DeviceException:
            pass

    async def update_schedule_test(self, result, time):
        """Test function to do. Update schedule from Bosch gateway."""
        self._time = time
        self._switch_points = result.get(SWITCH_POINTS)

    @property
    def setpoints(self):
        """Retrieve json setpoints."""
        return self._setpoints_temp
    
    def schedule_test(self):
        try:
            switch_points = self._switch_points.copy()
            added = {'dayOfWeek': 'We', 'setpoint': 'night', 'time': 120}
            bosch_date = datetime.strptime(self._time, "%Y-%m-%dT%H:%M:%S")
            day_of_week = DAYS_INT[bosch_date.weekday()]
            mins = self._get_minutes_since_midnight(bosch_date)
            print(day_of_week)
            added = {'dayOfWeek': day_of_week, 'setpoint': '', 'time': mins}
            switch_points.append(added)
            switch_points.sort(key=sort_switchpoints)
            i = switch_points.index(added)
            _prev = switch_points[i - 1]
            _next = switch_points[i + 1]

            def calcMinsInWeek(_setpoint):
                # print(DAYS_INT[_setpoint[DAYOFWEEK]])
                return (DAYS_INT.index(_setpoint[DAYOFWEEK]) + 1) * _setpoint[TIME]
            _mins_current = calcMinsInWeek(added)
            _mins_prev = calcMinsInWeek(_prev)
            _mins_next = calcMinsInWeek(_next)
            print(added)
            print(_prev)
            print(_mins_prev)
            print(_next)
            print(_mins_next)
            print("_mins_curr", _mins_current)
            print("_mins", (_mins_current - _mins_prev))
            print("self", self._switch_points)
            if _mins_current >= _mins_next:
                return _next
            print(_prev, "prev")
            return _prev
        except DeviceException:
            pass

    @property
    def time(self):
        """Get current time of Gateway."""
        return self._time

    @property
    def active_program(self):
        """Get active program."""
        return self._active_program

    def cache_temp_for_mode(self, temp, mode_type, active_setpoint=None):
        """Save active program for cache."""
        if mode_type == AUTO:
            active_setpoint = self.get_temp_in_schedule()[MODE]
        if active_setpoint in self._setpoints_temp:
            self._setpoints_temp[active_setpoint][VALUE] = temp

    async def _get_setpoint_temp(self, setpoint_property, setpoint):
        """Download temp for setpoint."""
        try:
            result = await self._connector.get(f'{setpoint_property[ID]}/{setpoint}')
        except DeviceException as err:
            _LOGGER.debug("Bug %s", err)
            pass
        return {
            MODE: setpoint,
            VALUE: result.get(VALUE, 0),
            MAX: result.get(MAX_VALUE, 0),
            MIN: result.get(MIN_VALUE, 0)
        }

    async def _parse_schedule(self, switch_points, setpoint_property):
        """Convert Bosch schedule to dict format."""
        for switch in switch_points:
            setpoint = switch[SETPOINT]
            if setpoint not in self._setpoints_temp:
                self._setpoints_temp[setpoint] = await self._get_setpoint_temp(
                    setpoint_property, setpoint
                )
        self._switch_points = switch_points

    def get_temp_for_mode(self, mode, mode_type):
        """This is working only in manual for RC35 where op_mode == setpoint."""
        cache = {}
        if mode_type == MANUAL:
            return self._setpoints_temp.get(mode, {}).get(VALUE, -1)
        if self.time:
            cache = self.get_temp_in_schedule()
        return cache.get(TEMP, 0)

    def get_max_temp_for_mode(self, mode, mode_type):
        """Get max temp for mode in schedule."""
        cache = {}
        if mode_type == MANUAL:
            return self._setpoints_temp.get(mode, {}).get(MAX, -1)
        if self.time:
            cache = self.get_temp_in_schedule()
        return cache.get(MAX, 0)

    def get_min_temp_for_mode(self, mode, mode_type):
        """Get min temp for mode in schedule."""
        cache = {}
        if mode_type == MANUAL:
            return self._setpoints_temp.get(mode, {}).get(MIN, -1)
        if self.time:
            cache = self.get_temp_in_schedule()
        return cache.get(MIN, 0)

    def get_setpoint_for_mode(self, mode, mode_type):
        """Get setpoints for mode."""
        cache = {}
        if mode_type == MANUAL:
            return self._setpoints_temp.get(mode, {}).get(MODE, -1)
        if self.time:
            cache = self.get_temp_in_schedule()
        return cache.get(MODE)

    def get_temp_in_schedule(self):
        """Find temp in schedule for current date."""
        if self._time:
            bosch_date = datetime.strptime(self._time, "%Y-%m-%dT%H:%M:%S")
            day_of_week = DAYS_INT[bosch_date.weekday()]
            if self._switch_points:
                switch_points = self._switch_points.copy()
                current_setpoint = {
                    DAYOFWEEK: day_of_week,
                    SETPOINT: '',
                    TIME: self._get_minutes_since_midnight(bosch_date)
                }
                switch_points.append(current_setpoint)
                switch_points.sort(key=sort_switchpoints)
                _prev_setpoint = switch_points[switch_points.index(current_setpoint) - 1][SETPOINT]
                return {
                    MODE: _prev_setpoint,
                    TEMP: self._setpoints_temp[_prev_setpoint][VALUE],
                    MAX: self._setpoints_temp[_prev_setpoint][MAX],
                    MIN: self._setpoints_temp[_prev_setpoint][MIN]
                }

    def _get_minutes_since_midnight(self, date):
        """Retrieve minutes since midnight."""
        return int((
            date - date.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds() / 60.0)
