""" Test script of bosch_thermostat_http. """
import asyncio
import logging
import json
import aiohttp
import time
import bosch_thermostat_http as bosch
from bosch_thermostat_http.const import DHW, HC, OPERATION_MODE, UUID, DATE

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

HTTP_HEADER = {
    'User-agent': 'TeleHeater2',
    'Connection': 'keep-alive'
}


async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://192.168.4.29/gateway/uuid",
            headers=HTTP_HEADER,
            timeout=30,
            skip_auto_headers=["Accept-Encoding", "Accept"]
        ) as res:
            if res.status == 200:
                data = await res.text()
                print(data)
        async with session.get(
            "http://192.168.4.29/gateway/uuid",
            headers=HTTP_HEADER,
            timeout=30,
            skip_auto_headers=["Accept-Encoding", "Accept"]
        ) as res:
            if res.status == 200:
                data = await res.text()
        await session.close()
asyncio.get_event_loop().run_until_complete(main())
