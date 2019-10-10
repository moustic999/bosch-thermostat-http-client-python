""" Test script of bosch_thermostat_http. """
import asyncio
import logging
import json
import aiohttp
import time
from datetime import datetime, date

days_int = [ "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su" ]
days = {
    "Mo": "monday",
    "Tu": "tuesday",
    "We": "wednesday",
    "Th": "thursday",
    "Fr": "friday",
    "Sa": "saturday",
    "Su": "sunday"
}

#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)

def open_json(file):
    """Open json file."""
    with open(file, 'r') as f:
        datastore = json.load(f)
        return datastore
    return None


myjson = open_json("schedule.json")["switchPoints"]
out = {
    "monday": [],
    "tuesday": [],
    "wednesday": [],
    "thursday": [],
    "friday": [],
    "saturday": [],
    "sunday": []
}
for line in myjson:
    day = days[line["dayOfWeek"]]
    start = line["time"]
    stop = 1440
    current_day_array = out[day]
    current_day_array.append({
        "mode": line["setpoint"],
        "start": start,
        "stop": stop
    })
    if len(current_day_array) > 1:
        current_day_array[-2]["stop"] = start-1

curr_time = "2019-09-29T23:01:44"
datetime_object = datetime.strptime(curr_time, "%Y-%m-%dT%H:%M:%S")
midnight_obj = datetime(datetime_object.year, datetime_object.month, datetime_object.day, 0, 0, 0)
minutes_since_midnight = (datetime_object - datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()/60;
dayOfWeek = days[days_int[datetime_object.weekday()]]
day = out[dayOfWeek]
foundSetpoint = None
for setpoint in day:
    if minutes_since_midnight > setpoint["start"] and minutes_since_midnight < setpoint["stop"]:
        foundSetpoint = setpoint["mode"]
        break
aha = ""
# for (line in myjson):
#     if line["dayOfWeek"] == dayOfWeek:


tt = "";
