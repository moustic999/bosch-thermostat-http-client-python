""" Constants used in Bosch thermostat. """

TYPE_INFO = "info"
TYPE_SENSOR = "sensor"
TYPE_HEATING = "heating"
BS = 16
MAGIC = bytearray.fromhex(
    "867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")

GET = "get"
SUBMIT = "submit"
NAME = "name"
PATH = "path"

""" Section of gateway info consts. """
GATEWAY = "/gateway/"
UUID = "uuid"

FIRMWARE_VERSION = "versionFirmware"
HARDWARE_VERSION = "versionHardware"

GATEWAY_PATH_LIST = {
    UUID: GATEWAY + UUID,
    FIRMWARE_VERSION: GATEWAY + FIRMWARE_VERSION,
    HARDWARE_VERSION: GATEWAY + HARDWARE_VERSION
}

HC = '/heatingCircuits'  # get all heating Circuits
"""
Get/set actual mode + get allowed modes
(manual, auto, 'Off', 'high', 'HCprogram', 'ownprogram').
"""
OPERATION_MODE = "operationMode"

DHW = '/dhwCircuits'
SENSORS = "/system/sensors"

""" Section of sensor friendly names. To be used in future. """
SENSOR_FRIENDLY_NAMES = {
    'outdoor_t1': 'outdoor Temp',
    'supply_t1_setpoint': 'supply Temp Setpoint',
    'supply_t1': 'supply Temp',
    'return': 'return Temp',
    'hotWater_t2': 'hotWater'
}
SENSOR_NAME = "sensor_name"
SENSOR_VALUE = "sensor_value"
SENSOR_TYPE = "sensor_type"
SENSOR_UNIT = "sensor_unit_of_measurment"

HTTP_HEADER = {
    'User-agent': 'TeleHeater/2.2.3',
    'Accept': 'application/json'
}

TIMEOUT = 10

""" VARS FOR HOME ASSISTANT. """
HC_CURRENT_ROOMSETPOINT = "currentRoomSetpoint"
HC_CURRENT_ROOMTEMPERATURE = "roomtemperature"
HC_HOLIDAY_MODE = "holidayMode"
HC_HEATING_STATUS = "status"
HC_SETPOINT_ROOMTEMPERATURE = "temperatureRoomSetpoint"
##### OLD
  # current Selected Temp
_HC_MANUAL_ROOMSETPOINT = "manualRoomSetpoint"  # set target Temp in manual mode
  # room current temperature
""" set target temp in auto mode. """


#
# _HEATING_CIRCUIT_LIST = {
#     _HC_CURRENT_ROOMSETPOINT: HC+'/{}/currentRoomSetpoint',
#     _HC_MANUAL_ROOMSETPOINT: HC+'/{}/manualRoomSetpoint',
#     OPERATION_MODE: HC+'/{}/operationMode',
#     _HC_SETPOINT_ROOMTEMPERATURE: HC+'/{}/temperatureRoomSetpoint',
#     _HC_CURRENT_ROOMTEMPERATURE: HC+'/{}/roomtemperature'
# }

DHW_CURRENT_WATERTEMP = "actualTemp"
DHW_CURRENT_SETPOINT = "currentSetpoint"
DHW_WATERFLOW = "waterFlow"
DHW_WORKINGTIME = "workingTime"

DHEATING_WATER_CIRCUIT_LIST = {
    DHW_CURRENT_WATERTEMP: DHW+'/dhw{}/actualTemp',
    DHW_CURRENT_SETPOINT: DHW+'/dhw{}/currentSetpoint',
    DHW_WATERFLOW: DHW+'/dhw{}/waterFlow',
    DHW_WORKINGTIME: DHW+'/dhw{}/workingTime',
}
