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
ID = "id"

VALUE = "value"
MINVALUE = "minValue"
MAXVALUE = "maxValue"
ALLOWED_VALUES = "allowedValues"
UNITS = "unitOfMeasure"
STATE = "state"

""" Section of gateway info consts. """
GATEWAY = "/gateway"
SYSTEM = '/system'
DHW = '/dhwCircuits'
HC = '/heatingCircuits'
HEATSOURCES = '/heatSources'
NOTIFICATIONS = "/notifications"

ROOT_PATHS = [DHW,GATEWAY,HC,HEATSOURCES,NOTIFICATIONS,SYSTEM]



SENSORS = "/system/sensors"
UUID = "uuid"

FIRMWARE_VERSION = "versionFirmware"
HARDWARE_VERSION = "versionHardware"
SYSTEM_BRAND = "brand"
SYSTEM_TYPE = "systemType"

GATEWAY_PATH_LIST = {
    UUID: GATEWAY +'/' +UUID,
    FIRMWARE_VERSION: GATEWAY +'/'+ FIRMWARE_VERSION,
    HARDWARE_VERSION: GATEWAY +'/'+ HARDWARE_VERSION,
    SYSTEM_BRAND: SYSTEM +'/'+ SYSTEM_BRAND,
    SYSTEM_TYPE: SYSTEM +'/'+ SYSTEM_TYPE
}


"""
Get/set actual mode + get allowed modes
(manual, auto, 'Off', 'high', 'HCprogram', 'ownprogram').
"""
OPERATION_MODE = "operationMode"




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
HC_TEMPORARY_TEMPERATURE = "temporaryRoomSetpoint"
HC_ECO = "temperatureLevels/eco"
##### OLD
HC_OPERATION_MODE = "operationMode"
HC_MODE_AUTO = 'auto'
HC_MODE_MANUAL = 'manual'

  # current Selected Temp
HC_MANUAL_ROOMSETPOINT = "manualRoomSetpoint"  # set target Temp in manual mode
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

HC_CAPABILITY = 'heatingCircuit'
DHW_CAPABILITY = 'hotWater'
SOLAR_CAPACITY = 'solar'
SENSOR_CAPACITY = 'sensor'

SYTEM_CAPABILITIES = {
   HC_CAPABILITY : ['/heatingCircuits'],
   DHW_CAPABILITY : ['/dhwCircuits'],
#   SOLAR_CAPACITY : ['/solarCircuits'],
   SENSOR_CAPACITY : ['/system/sensors/temperatures','/heatSources']
}

DETAILED_CAPABILITIES = {
    HC_CAPABILITY :  ['/heatingCircuits/{}/currentRoomSetpoint',
                          '/heatingCircuits/{}/operationMode',
                          '/heatingCircuits/{}/roomtemperature'],
    DHW_CAPABILITY : ['/dhwCircuits/{}/currentSetpoint',
              '/dhwCircuits/{}/operationMode',
              '/dhwCircuits/{}/actualTemp'],
    SOLAR_CAPACITY :[]
    }

SENSORS_CAPABILITIES = [
    '/system/sensors/temperatures/outdoor_t1',
    '/system/sensors/temperatures/supply_t1_setpoint',
    '/system/sensors/temperatures/supply_t1',
    '/system/sensors/temperatures/hotWater_t2',
    '/system/sensors/temperatures/return',
    '/heatSources/actualPower',
    '/heatSources/actualModulation',
    '/heatSources/burnerModulationSetpoint',
    '/heatSources/burnerPowerSetpoint',
    '/heatSources/flameStatus',
    '/heatSources/CHpumpModulation',
    '/heatSources/systemPressure',
    '/heatSources/flameCurrent',
    '/heatSources/workingTime',
    '/heatSources/numberOfStarts'
]
