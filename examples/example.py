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
        print(await gateway.check_connection())
        my_sensors = [ "outdoor_t1" ]
        options_sensors = {sensor: (True if sensor in my_sensors else False) for sensor in gateway.database["sensors"].keys() }
        print(options_sensors)
        return
        db = gateway.database
        # print(db["sensors"])
        all_sensors = gateway.database["sensors"]
        scheme = {sensor: bool for sensor in all_sensors.keys()}
        print(scheme)
        return
        for sensor, item in db["sensors"].items():
            name = item["name"]
            print(f'"{sensor}": "{name}",')

        for sensor, item in db["sensors"].items():
            print(f'vol.Required("{sensor}"): bool,')
        return
        print(gateway.firmware)
        print(gateway.device_name)
        await gateway.initialize_circuits(HC)
        
        hcs = gateway.heating_circuits
        hc = hcs[0]
        time.sleep(1)
        await hc.update()
        print(hc.hvac_mode)
        print(hc.target_temperature)
        # print(hc.schedule)
        print(gateway.get_info(DATE))
        # print(await gateway.rawscan())
        #print(hc.schedule.get_temp_for_date(gateway.get_info(DATE)))
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
