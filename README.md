

# buderus-client-python
Python3 asyncio package to talk to Buderus KM200

example :
```python
import asyncio 
import aiohttp

from buderus.gateway import Gateway
async def main():
    async with aiohttp.ClientSession() as session:
        gateway =  Gateway(session, '<Local IP of gateway>','<gateway password>','<user password>')
        await gateway.initialize()
       
      
        print(gateway.info.uuid)

        for sensor in gateway.sensors.items:
            print (sensor.name, sensor.value)

asyncio.get_event_loop().run_until_complete(main())
```

