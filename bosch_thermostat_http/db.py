"""Retrieve standard data."""
import json
import os

from .const import (PATHS, GATEWAY, DICT, GATEWAY, HEATING_CIRCUITS,
                    DHW_CIRCUITS, MANUAL, AUTO, MAX, MIN, UNITS, STATE,
                    INVALID, VALUE, ALLOWED_VALUES, OWNPROGRAM, HCPROGRAM,
                    OPEN, SHORT, UUID, FIRMWARE_VERSION, HARDWARE_VERSION,
                    SYSTEM_BRAND, SYSTEM_TYPE, MAIN_URI, REFS)

FILENAME = os.path.join(os.path.dirname(__file__), 'db.json')

DATA = "data"
FIRMWARE_URI = "versionFirmwarePath"
SENSORS = "sensors"


def open_json():
    """Open json file."""
    with open(FILENAME, 'r') as f:
        datastore = json.load(f)
        return datastore
    return None


def get_firmware_uri():
    with open(FILENAME, 'r') as f:
        datastore = json.load(f)
        if FIRMWARE_URI in datastore:
            return datastore[FIRMWARE_URI]
    return None


def get_db_of_firmware(firmware_version):
    db = open_json()
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
