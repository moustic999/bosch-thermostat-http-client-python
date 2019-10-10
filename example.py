""" Test script of bosch_thermostat_http. """
import asyncio
import logging
import json
import aiohttp
import time
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import DHW, HC, OPERATION_MODE, UUID, DATE

#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)



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
        await gateway.check_connection()
        print(gateway.firmware)
        print(gateway.device_name)
        await gateway.initialize_circuits(HC)
        
        hcs = gateway.heating_circuits
        hc = hcs[1]
        time.sleep(1)
        await hc.update()
        print(hc.hvac_modes)
        print(hc.hvac_mode)
        print(hc.target_temperature)
        print(hc.schedule)
        print(gateway.get_info(DATE))
        print(hc.schedule.get_temp_for_date(gateway.get_info(DATE)))
        # await hc.set_operation_mode("auto")
        return
        aa=0
        while aa < 10:
            time.sleep(1)
            await hc.update()
            print(hc.target_temperature)
            aa = aa+1
        
        await hc.set_operation_mode("auto")

        aa=0
        while aa < 10:
            time.sleep(1)
            await hc.update()
            print(hc.target_temperature)
            aa = aa+1

        # print(gateway.get_property(TYPE_INFO, UUID))
        await session.close()
asyncio.get_event_loop().run_until_complete(main())
