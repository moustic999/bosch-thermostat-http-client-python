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
        await gateway.initialize_circuits(HC)
        hcs = gateway.heating_circuits
        hc = hcs[0]
        
        await hc.update()
        #await hc.set_temperature("23.0")
        #await hc.update()
        #
        # print(hc.get_property(OPERATION_MODE))
        # print(hc.get_property(HC_CURRENT_ROOMSETPOINT))
        # keeey = gateway.access_key
        # import base64
        # key_b64 = base64.b64encode(keeey)
        # w = {
        #     "da": key_b64
        # }
        # print(key_b64)
        # import json
        # print(json.dumps(w))
        # await gateway.initialize()
        # await gateway.initialize_hc_circuits()

        # await hc.initialize()
        # await hc.update()
        # print(hc.get_property(OPERATION_MODE))
        # await hc.set_mode("manual")
        #
        # await hc.update()
        # await hc.update_requested_keys(OPERATION_MODE)
        # print(hc.get_property(OPERATION_MODE))
        #geta = gateway.get_request()
        # print("GATEWAY")
        # # print("SYSTEM")
        # print(await geta("/heatingCircuits/hc1/currentRoomSetpoint"))
        #print(await crawl("/heatingCircuits/hc1", [], 3, geta))
        # print("SENSORS")
        #   rint(await geta("/system/sensors"))
        #   rint("HS")
        #   rint(await geta("/heatSources/hs1/status"))
        #   rint("HC")
        # print(await geta("/heatingCircuits"))
        # print("DHW")
        # print(await geta("/dhwCircuits/dhw1/status"))
        # print("ale duzo")
        # print(await geta("/heatingCircuits/hc1/controlType"))
        # a = "HC1"
        # intValue = a.replace("HC", "")
        # print(intValue)
        # print("UUID")
        # print(gateway.get_property(TYPE_INFO, UUID))
        # print(gateway.get_property(TYPE_INFO, HARDWARE_VERSION))
        # print(gateway.get_property(TYPE_INFO, FIRMWARE_VERSION))
        # print(await geta("/system/sensors/temperatures/outdoor_t1"))
        # print("SENSORS")
        # for sensor in gateway.get_items(SENSORS):
        #     print(sensor.get_property(SENSOR_NAME),
        #           sensor.get_property(SENSOR_VALUE))
        session.close()
asyncio.get_event_loop().run_until_complete(main())
