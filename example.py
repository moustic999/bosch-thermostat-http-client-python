""" Test script of bosch_thermostat_http. """
import asyncio
import logging
import json
import aiohttp
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import DHW, HC, OPERATION_MODE, UUID

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


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
        # await gateway.initialize_circuits(HC)
        # print(json.dumps(await gateway.rawscan()))
        await gateway.initialize_circuits(DHW)
        # await gateway.initialize_sensors()
        dhws = gateway.dhw_circuits
        dhw = dhws[0]
        await dhw.update()
        print(dhw.current_temp)
        print(dhw.target_temperature)
        await dhw.set_temperature(50.5)
        await dhw.update()
        print(dhw.target_temperature)
        return
        print(dhw.get_property("operation_mode"))
        print(dhws)
        hcs = gateway.heating_circuits
        print(hcs)
        hc = hcs[0]
        await hc.update()
        print(hc.current_temp)
        return
        await hc.set_operation_mode("auto")
        await hc.set_temperature(20)
        await hc.update()
        print(hc.get_value("manual_room_setpoint"))
        print(hc.get_property("manual_room_setpoint"))
        sensors = gateway.sensors
        print(sensors)
        for sensor in sensors:
            await sensor.update()
            print(sensor.name)
            print(sensor.get_all_properties())
        
        
        # print(gateway.get_property(TYPE_INFO, UUID))
        await session.close()
asyncio.get_event_loop().run_until_complete(main())
