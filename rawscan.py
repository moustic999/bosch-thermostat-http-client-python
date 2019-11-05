""" Test script of bosch_thermostat_http. """
import asyncio
import aiohttp
import json

from bosch_thermostat_http.gateway import Gateway
from bosch_thermostat_http.const import FIRMWARE_VERSION

async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    async with aiohttp.ClientSession() as session:

        data_file = open("data_file.txt", "r")
        data = data_file.read().splitlines()
        gateway = Gateway(session=session,
                          host=data[0],
                          access_key=data[1],
                          password=data[2])
        print(await gateway.check_connection())
        
        result = await gateway.rawscan()
        with open("myjson.json", 'w') as logfile:
                json.dump(result, logfile, indent=4)
        # print(json.dumps(result, indent=4, sort_keys=True))


        await session.close()


asyncio.get_event_loop().run_until_complete(main())
