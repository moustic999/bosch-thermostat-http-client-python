import asyncio
import time
import aiohttp
import binascii
import hashlib
from bosch_thermostat_http.helper import crawl
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import (FIRMWARE_VERSION, HARDWARE_VERSION,
                                         UUID, SENSORS, DHW, HC, GATEWAY,
                                         OPERATION_MODE, DHW_OFFTEMP_LEVEL,
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
        #await gateway.initialize_circuits(DHW)
        #await gateway.initialize_circuits(HC)
        #dhws = gateway.dhw_circuits
        #dhw = dhws[0]

        #print("getting property")
        #print(dhw.get_property(DHW_OFFTEMP_LEVEL))
        #await dhw.update()
        #print(dhw.get_property(DHW_OFFTEMP_LEVEL))
        # await hc.set_operation_mode("manual")
        await gateway.set_value("/heatingCircuits/hc1/suWiSwitchMode", "forced")
        #time.sleep(5)
        print(await gateway.get("/heatingCircuits/hc1/currentSuWiMode"))
        print(await gateway.get("/heatingCircuits/hc1/suWiSwitchMode"))
        #print(await gateway.get("/heatingCircuits/hc1/currentRoomSetpoint"))
        #await gateway.set_value("/heatingCircuits/hc1/manualRoomSetpoint", 22.0)
        #time.sleep(3)
        #print(await gateway.get("/heatingCircuits/hc1/currentRoomSetpoint"))
        #print(await gateway.get("/heatingCircuits/hc1/operationMode"))
       
        await session.close()
asyncio.get_event_loop().run_until_complete(main())