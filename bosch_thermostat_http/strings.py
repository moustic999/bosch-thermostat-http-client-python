"""Module to control string from db json."""
# pylint: disable=invalid-name

import logging

from .const import (
    ALLOWED_VALUES,
    AUTO,
    MAX,
    MIN,
    OPEN,
    SHORT,
    STATE,
    UNITS,
    VALUE,
    INVALID,
)

_LOGGER = logging.getLogger(__name__)


class Strings:
    """String for Bosch."""

    def __init__(self, dictionary, _type=None):
        """Write dictionary to object."""
        self._dict = dictionary
        self.__init_shared()

    def __init_shared(self):
        """Initialize strings."""
        self.val = self._dict.get(VALUE, VALUE)
        self.min = self._dict.get(MIN, MIN)
        self.max = self._dict.get(MAX, MAX)
        self.allowed_values = self._dict.get(ALLOWED_VALUES, ALLOWED_VALUES)
        self.units = self._dict.get(UNITS, UNITS)
        self.state = self._dict.get(STATE, STATE)
        self.open = self._dict.get(OPEN, OPEN)
        self.short = self._dict.get(SHORT, SHORT)
        self.auto = self._dict.get(AUTO, AUTO)
        self.invalid = self._dict.get(INVALID, INVALID)

    def get(self, prop):
        """Get string from DB."""
        return getattr(self, prop, None)
