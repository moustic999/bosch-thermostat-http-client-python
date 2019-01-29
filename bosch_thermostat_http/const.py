""" Constants used in Bosch thermostat. """

TYPE_INFO = "info"
TYPE_SENSOR = "sensor"
TYPE_HEATING = "heating"
BS = 16
MAGIC = bytearray.fromhex(
    "867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")


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
HC_CURRENT_ROOMSETPOINT = "currentRoomSetpoint"  # current Selected Temp
HC_MANUAL_ROOMSETPOINT = "manualRoomSetpoint"  # set target Temp in manual mode
HC_CURRENT_ROOMTEMPERATURE = "roomtemperature"  # room current temperature
""" set target temp in auto mode. """
HC_SETPOINT_ROOMTEMPERATURE = "temperatureRoomSetpoint"

""" get/set actual mode + get allowed modes (manual, auto). """
HC_OPERATION_MODE = "operationMode"
HEATING_CIRCUIT_LIST = {
    HC_CURRENT_ROOMSETPOINT: HC+'/{}/currentRoomSetpoint',
    HC_MANUAL_ROOMSETPOINT: HC+'/{}/manualRoomSetpoint',
    HC_OPERATION_MODE: HC+'/{}/operationMode',
    HC_SETPOINT_ROOMTEMPERATURE: HC+'/{}/temperatureRoomSetpoint',
    HC_CURRENT_ROOMTEMPERATURE: HC+'/{}/roomtemperature'
}
HEATING_CIRCUIT_OPERATION_MODE = '/heatingCircuits/{}/operationMode'

""" Section of sensor consts. """
SENSOR_LIST = {
    'outdoor Temp': '/system/sensors/temperatures/outdoor_t1',
    'supply Temp Setpoint': '/system/sensors/temperatures/supply_t1_setpoint',
    'supply Temp': '/system/sensors/temperatures/supply_t1',
    'return Temp': '/system/sensors/temperatures/return'
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
