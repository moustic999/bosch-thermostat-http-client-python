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
# PATHS = "paths"
GATEWAY = "gateway"
HC = "hc"
DHW = "dhw"
SENSORS = "sensors"
SENSOR = "sensor"
DICT = "dict"
MAIN_URI = "mainUri"
MODELS = "models"
# PRESETS = "presets"
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
MAX_VALUE = "maxValue"
MIN_VALUE = "minValue"
UNITS = "units"
VALUE = "value"
VALUES = "values"
ALLOWED_VALUES = "allowedValues"
STATE = "state"
CURRENT_TEMP = "current_temp"
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
TYPE = "type"
URI = "uri"
REGULAR = "regular"
RESULT = "result"  # to not mismarch with value
SYSTEM_BRAND = "brand"
SYSTEM_TYPE = "systemType"
SYSTEM_INFO = "systemInfo"

USER_AGENT = "User-agent"
CONNECTION = "Connection"
TELEHEATER = "TeleHeater"
KEEP_ALIVE = "keep-alive"

HTTP_HEADER = {
    USER_AGENT: TELEHEATER,
    CONNECTION: KEEP_ALIVE,
    "Content-Type": "application/json"
}

TIMEOUT = 10

HEATING_CIRCUITS = "heatingCircuits"
DHW_CIRCUITS = "dhwCircuits"
CIRCUIT_TYPES = {
    HC: HEATING_CIRCUITS,
    DHW: DHW_CIRCUITS
}

MODE_TO_SETPOINT = "mode_to_setpoint"
READ = "read"
WRITE = "write"

RC300 = "RC300"

# SCHEDULE
SETPOINT_PROP = "setpointProperty"
SWITCH_POINTS = "switchPoints"
SWITCHPROGRAM = "/{}/{}/switchPrograms/{}"
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

SENSORS_LIST = ["outdoor_t1", "hotWater_t2", "supply_t1_setpoint", "supply_t1",
                "return", "healthStatus", "actualPower", "actualModulation",
                "CHpumpModulation"]

DEFAULT_MIN_TEMP = 0
DEFAULT_MAX_TEMP = 100
