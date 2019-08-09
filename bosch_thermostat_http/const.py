"""Constants used in Bosch thermostat."""

BS = 16
MAGIC = bytearray.fromhex(
    "867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")

GET = "get"
SUBMIT = "submit"
NAME = "name"
PATH = "path"
ID = "id"
REFS = "refs"

UUID = "uuid"
PATHS = "paths"
GATEWAY = "gateway"
HC = "hc"
DHW = "dhw"
SENSORS = "sensors"
DICT = "dict"
MAIN_URI = "mainUri"


""" New refs scheme. """
OPERATION_MODE = "operation_mode"
STATUS = "status"
ROOMSETPOINT = "room_setpoint"
MANUALROOMSETPOINT = "manual_room_setpoint"
TEMPORARY_TEMP = "temporary_temp"
ROOMTEMP = "room_temp"
AUTO = "auto"
MANUAL = "manual"
MAX = "max"
MIN = "min"
UNITS = "units"
VALUE = "value"
ALLOWED_VALUES = "allowedValues"
STATE = "state"
OWNPROGRAM = "ownprogram"
HCPROGRAM = "hcprogram"
WATER_TEMP = "water_temp"
WATER_SETPOINT = "water_setpoint"
WATER_OFF = "water_off"
WATER_HIGH = "water_high"
OPEN = "open"
SHORT = "short"

INVALID = "invalid"

ROOT_PATHS = ["/dhwCircuits", "/gateway", "/heatingCircuits",
              "/heatSources", "/notifications", "/system"]

""" Section of gateway info consts. """

FIRMWARE_VERSION = "versionFirmware"
HARDWARE_VERSION = "versionHardware"
SYSTEM_BRAND = "brand"
SYSTEM_TYPE = "systemType"


"""
Get/set actual mode + get allowed modes
(manual, auto, 'Off', 'high', 'HCprogram', 'ownprogram').
"""

HTTP_HEADER = {
    'User-agent': 'TeleHeater',
    'Connection': 'close'
}

TIMEOUT = 10

HEATING_CIRCUITS = "heatingCircuits"
DHW_CIRCUITS = "dhwCircuits"
