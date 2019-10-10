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
HA_STATES = "hastates"

UUID = "uuid"
PATHS = "paths"
GATEWAY = "gateway"
HC = "hc"
DHW = "dhw"
SENSORS = "sensors"
DICT = "dict"
MAIN_URI = "mainUri"
MODELS = "models"
PRESETS = "presets"
TEMP = "temp"
DATE = "dateTime"

""" New refs scheme. """
OPERATION_MODE = "operation_mode"
STATUS = "status"
AUTO = "auto"
MANUAL = "manual"
OFF = "off"
ON = "on"
MAX = "max"
MIN = "min"
UNITS = "units"
VALUE = "value"
VALUES = "values"
ALLOWED_VALUES = "allowedValues"
STATE = "state"
OWNPROGRAM = "ownprogram"
HCPROGRAM = "hcprogram"
CURRENT_TEMP = "current_temp"
AUTO_SETPOINT = "auto_setpoint"
MANUAL_SETPOINT = "manual_setpoint"
AUTO_SETTEMP = "auto_set_temp"
WATER_SETPOINT = "water_setpoint"
WATER_OFF = "water_off"
WATER_HIGH = "water_high"
ACTIVE_PROGRAM = "activeProgram"
DAYOFWEEK = "dayOfWeek"
MODE = "mode"
START = "start"
STOP = "stop"
SETPOINT = "setpoint"
TIME = "time"
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
SYSTEM_INFO = "systemInfo"

HTTP_HEADER = {
    'User-agent': 'TeleHeater',
    'Connection': 'close'
}

TIMEOUT = 10

HEATING_CIRCUITS = "heatingCircuits"
DHW_CIRCUITS = "dhwCircuits"

RC300 = "RC300"

###SCHEDULE
SETPOINT_PROP = "setpointProperty"
SWITCH_POINTS = "switchPoints"
SWITCHPROGRAM = "/heatingCircuits/{}/switchPrograms/{}"
MIDNIGHT = 1440
DAYS_INT = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
DAYS = {
    "Mo": "monday",
    "Tu": "tuesday",
    "We": "wednesday",
    "Th": "thursday",
    "Fr": "friday",
    "Sa": "saturday",
    "Su": "sunday",
}