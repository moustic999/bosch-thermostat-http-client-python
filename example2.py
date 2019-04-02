""" Test script of bosch_thermostat_http. """
import asyncio

import aiohttp
import binascii
import hashlib
from bosch_thermostat_http.helper import crawl
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import (FIRMWARE_VERSION, HARDWARE_VERSION,
                                         SENSOR_NAME, SENSOR_VALUE, TYPE_INFO,
                                         UUID, SENSORS, DHW, HC, GATEWAY,
                                         OPERATION_MODE,
                                         HC_CURRENT_ROOMSETPOINT)


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
        print(await gateway.check_connection())
        await gateway.initialize_sensors()
       
#        await gateway.rawscan()

        await session.close()


asyncio.get_event_loop().run_until_complete(main())
