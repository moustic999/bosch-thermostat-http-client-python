""" Test script of bosch_thermostat_http. """
import asyncio

import aiohttp
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import (FIRMWARE_VERSION, HARDWARE_VERSION,
                                         SENSOR_NAME, SENSOR_VALUE, TYPE_INFO,
                                         UUID, SENSORS, DHW, HC, GATEWAY)


async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    async with aiohttp.ClientSession() as session:
        data_file = open("data_file.txt", "r")
        data = data_file.read().splitlines()
        gateway = bosch.Gateway(session,
                                host=data[0],
                                access_key=data[1],
                                password=data[2])
        await gateway.initialize()
        geta = gateway.get_request()
        # print("GATEWAY")
        # print(await geta("/gateway"))
        # print("SYSTEM")
        # print(await geta("/system"))
        # print("SENSORS")
        # print(await geta("/system/sensors"))
        # print("HS")
        # print(await geta("/heatSources/hs1/status"))
        # print("HC")
        # print(await geta("/heatingCircuits"))
        # print("DHW")
        # print(await geta("/dhwCircuits/dhw1/status"))
        # print("ale duzo")
        # print(await geta("/heatingCircuits/hc1"))
        # print("UUID")
        # print(gateway.get_property(TYPE_INFO, UUID))
        # print(gateway.get_property(TYPE_INFO, HARDWARE_VERSION))
        # print(gateway.get_property(TYPE_INFO, FIRMWARE_VERSION))
        # print(await geta("/system/sensors/temperatures/outdoor_t1"))
        # print("SENSORS")
        for sensor in gateway.get_items(SENSORS):
            print(sensor.get_property(SENSOR_NAME),
                  sensor.get_property(SENSOR_VALUE))

asyncio.get_event_loop().run_until_complete(main())
