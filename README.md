

# bosch-thermostat-http-client-python
Python3 asyncio package to talk to Bosch Thermostats via their gateway, especially for Buderus KM200/KM50 and Nefit IP modules used in Enviline heat pumps. These gateways support Http access in local network.

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

To run this code do the following:

* create file data_file.txt and insert like this:
```
ip
access_key
password
```
replace strings with proper values

* run in dir `python3 -m venv .`
* run `python3 test.py`

# Helper
Now there is extra command added with this package `bosch_scan`.
```
Usage: bosch_scan [OPTIONS] COMMAND [ARGS]...

  A tool to create rawscan of Bosch thermostat.

Options:
  --ip TEXT                       IP address of gateway  [required]
  --token TEXT                    Token from sticker without dashes.
                                  [required]
  --password TEXT                 Password you set in mobile app.
  -o, --output TEXT               Path to output file of scan. Default to
                                  [raw/small]scan_uuid.json
  --stdout                        Print scan to stdout
  -d, --debug
  -s, --smallscan [HC|DHW|SENSORS]
                                  Scan only single circuit of thermostat.
  --help                          Show this message and exit.

```

# Examples 

SENSORS:
```
bosch_examples sensors --help
bosch_examples sensors --ip {IP} --token {TOKEN} --password {PASS} -s outdoor_t1
```

DHW:
```
bosch_examples dhw --help
bosch_examples dhw --ip {IP} --token {TOKEN} --password {PASS} -t --op_modes --setpoints -m
```

HC:
```
bosch_examples hc --help
bosch_examples hc --ip {IP} --token {TOKEN} --password {PASS} -t --op_modes --setpoints -m
```