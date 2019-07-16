"""Constants used in Bosch thermostat."""

BS = 16
MAGIC = bytearray.fromhex(
    "867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")
# MAGIC = bytearray.fromhex(
#     "75735458393830414a6a5651566b3635516b76574f4c615038452b795249504f")

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
OPEN = "open"
SHORT = "short"
INVALID = "invalid"

""" Section of gateway info consts. """
GATEWAY = "/gateway"
SYSTEM = '/system'
DHW = '/dhwCircuits'
HC = '/heatingCircuits'
HEATSOURCES = '/heatSources'
NOTIFICATIONS = "/notifications"
APPLIANCES = SYSTEM + '/appliance'

ROOT_PATHS = [DHW, GATEWAY, HC, HEATSOURCES, NOTIFICATIONS, SYSTEM]

SENSORS = "/system/sensors"
UUID = "uuid"

FIRMWARE_VERSION = "versionFirmware"
HARDWARE_VERSION = "versionHardware"
SYSTEM_BRAND = "brand"
SYSTEM_TYPE = "systemType"

GATEWAY_PATH_LIST = {
    UUID: '{}/{}'.format(GATEWAY, UUID),
    FIRMWARE_VERSION: '{}/{}'.format(GATEWAY, FIRMWARE_VERSION),
    HARDWARE_VERSION: '{}/{}'.format(GATEWAY, HARDWARE_VERSION),
    SYSTEM_BRAND: '{}/{}'.format(SYSTEM, SYSTEM_BRAND),
    SYSTEM_TYPE: '{}/{}'.format(SYSTEM, SYSTEM_TYPE)
}

"""
Get/set actual mode + get allowed modes
(manual, auto, 'Off', 'high', 'HCprogram', 'ownprogram').
"""
OPERATION_MODE = "operationMode"

HTTP_HEADER = {
    'User-agent': 'TeleHeater',
    'Connection': 'close'
}

TIMEOUT = 10

""" VARS FOR HOME ASSISTANT. """
HC_CURRENT_ROOMSETPOINT = "currentRoomSetpoint"
HC_ROOMTEMPERATURE = "roomtemperature"
HC_HOLIDAY_MODE = "holidayModeactivated"
HC_HEATING_STATUS = "status"
HC_SETPOINT_ROOMTEMPERATURE = "temperatureRoomSetpoint"
HC_TEMPORARY_TEMPERATURE = "temporaryRoomSetpoint"
HC_ECO = "temperatureLevels/eco"
HC_MODE_AUTO = 'auto'
HC_MODE_MANUAL = 'manual'
HC_MANUAL_ROOMSETPOINT = "manualRoomSetpoint"  # set target Temp in manual mode
# room current temperature
""" set target temp in auto mode. """

DHW_CURRENT_WATERTEMP = "actualTemp"
DHW_CURRENT_SETPOINT = "currentSetpoint"
DHW_HIGHTTEMP_LEVEL = "temperatureLevelshigh"
DHW_OFFTEMP_LEVEL = "temperatureLevelsoff"
DHW_OFF = "Off"
DHW_HIGH = "high"
DHW_HCPROGRAM = "HCprogram"
DHW_OWNPROGRAM = "ownprogram"

SENSORS_EXLUDE = ()
HEATSOURCES_EXLUDE = ('/system/appliance/workingTime/secondBurner')
APPLIANCES_EXLUDE = ()


HC_CAPABILITY = 'heatingCircuit'
DHW_CAPABILITY = 'hotWater'
SOLAR_CAPACITY = 'solar'
SENSOR_CAPACITY = 'sensor'

SYSTEM_CAPABILITIES = {
    HC_CAPABILITY: [HC],
    DHW_CAPABILITY: [DHW],
    #   SOLAR_CAPACITY : ['/solarCircuits'],
    SENSOR_CAPACITY: ['/system/sensors/temperatures', HEATSOURCES]
}

DETAILED_CAPABILITIES = {
    HC_CAPABILITY: [
        '/heatingCircuits/{}/currentRoomSetpoint',
        '/heatingCircuits/{}/operationMode',
        '/heatingCircuits/{}/roomtemperature'
    ],
    DHW_CAPABILITY: [
        '/dhwCircuits/{}/currentSetpoint',
        '/dhwCircuits/{}/operationMode',
        '/dhwCircuits/{}/actualTemp'
    ],
    SOLAR_CAPACITY: []
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
