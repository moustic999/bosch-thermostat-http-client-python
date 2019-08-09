"""Retrieve standard data."""
import json
import os

from .const import (PATHS, GATEWAY)

FILENAME = os.path.join(os.path.dirname(__file__), 'db2_prototype.json')

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


def bosch_sensors(firmware_version):
    """Get bosch sensors from db.json file."""
    db = open_json()
    if db:
        if firmware_version in db and SENSORS in db[firmware_version]:
            return db[firmware_version]
    return None

def check_db(db):
    if PATHS in db:
        if GATEWAY in db[PATHS]:
            if "uuid" in db[PATHS][GATEWAY]:
                return True
    return False
