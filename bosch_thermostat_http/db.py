"""Retrieve standard data."""
import json
import os

from .const import (PATHS, GATEWAY, DICT, GATEWAY, HEATING_CIRCUITS,
                    DHW_CIRCUITS, MANUAL, AUTO, MAX, MIN, UNITS, STATE,
                    INVALID, VALUE, ALLOWED_VALUES, OWNPROGRAM, HCPROGRAM,
                    OPEN, SHORT, UUID, FIRMWARE_VERSION, HARDWARE_VERSION,
                    SYSTEM_BRAND, SYSTEM_TYPE, MAIN_URI, REFS, RC300)

MAINPATH = os.path.join(os.path.dirname(__file__), 'db')
FILENAME = os.path.join(MAINPATH, 'db.json')

DATA = "data"
FIRMWARE_URI = "versionFirmwarePath"
SYSTEM_INFO_URI = "systemInfo"
SENSORS = "sensors"


def open_json(file):
    """Open json file."""
    with open(file, 'r') as f:
        datastore = json.load(f)
        return datastore
    return None


def get_firmware_uri():
    datastore = open_json(FILENAME)
    if FIRMWARE_URI in datastore:
        return datastore[FIRMWARE_URI]
    return None

def get_initial_db():
    return open_json(FILENAME)

def get_db_of_firmware(device_type, firmware_version):
    filename = "rc300.json" if device_type == RC300 else "default.json"
    filepath = os.path.join(MAINPATH, filename)
    db = open_json(filepath)
    if db:
        if firmware_version in db:
            return db[firmware_version]
    return None

def check_db(fw_version, db):
    return True
    if fw_version in db:
        subrow = db[fw_version]
        if DICT in subrow and GATEWAY in subrow:
            if not all(k in subrow[DICT] for k in (MANUAL, AUTO, MAX, MIN,
                                                   UNITS, STATE, INVALID,
                                                   VALUE, ALLOWED_VALUES,
                                                   OWNPROGRAM, HCPROGRAM,
                                                   OPEN, SHORT)):
                return False
            if not all(k in subrow[DICT] for k in (UUID, FIRMWARE_VERSION,
                                                   HARDWARE_VERSION,
                                                   SYSTEM_BRAND, SYSTEM_TYPE)):
                return False
        else:
            return False
    return True
