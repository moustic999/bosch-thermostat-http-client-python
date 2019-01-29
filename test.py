import asyncio
import aiohttp
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import (FIRMWARE_VERSION, HARDWARE_VERSION,
                                         UUID, TYPE_INFO,
                                         SENSOR_NAME, SENSOR_VALUE)


async def main():
    async with aiohttp.ClientSession() as session:
        data_file = open("data_file.txt", "r")
        data = data_file.read().splitlines()
        gateway = bosch.Gateway(session,
                                host=data[0],
                                access_key=data[1],
                                password=data[2])
        await gateway.initialize()
        print("UUID")
        print(gateway.get_property(TYPE_INFO, UUID))
        print(gateway.get_property(TYPE_INFO, HARDWARE_VERSION))
        print(gateway.get_property(TYPE_INFO, FIRMWARE_VERSION))
        print("SENSORS")
        for sensor in gateway.get_sensors():
            print(sensor.get_property(SENSOR_NAME),
                  sensor.get_property(SENSOR_VALUE))

asyncio.get_event_loop().run_until_complete(main())
