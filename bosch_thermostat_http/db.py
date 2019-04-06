""" Retrieve standard data. """
import json
import os

FILENAME = os.path.join(os.path.dirname(__file__), 'db.json')

DATA = "data"
SENSORS = "sensors"


def open_json():
    with open(FILENAME, 'r') as f:
        datastore = json.load(f)
        if DATA in datastore:
            return datastore[DATA]
    return None


def bosch_sensors(firmware_version):
    db = open_json()
    if db:
        if firmware_version in db and SENSORS in db[firmware_version]:
            return db[firmware_version][SENSORS]
    return None
