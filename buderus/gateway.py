import asyncio
import json

from io import StringIO

from aiohttp import client_exceptions

from .encryption import Encryption  
from .gateway_info import Gateway_Info
from .sensors import Sensors

class Gateway(object):
    _magic = bytearray.fromhex("867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")

    host = None

    serial_number = None
    access_key = None
    password = None

    encryption = None
    
    websession = None
    info = None
    sensors = None


    def __init__(self, websession, host, access_key, password, ):
        """
        :param access_key:
        :param password:
        :param host:
        """

        self.access_key = access_key
        self.password = password
        self.host = host
        self.websession = websession

        self.encryption = Encryption(self._magic, access_key, password)
  
    def encrypt(self, data):
        return self.encryption.encrypt(data)

    def decrypt(self, data):
        return self.encryption.decrypt(data)


    async def initialize(self):
        self.info = Gateway_Info(self.get)
        await self.info.update()

        self.sensors = Sensors(self.get)
        self.sensors.registerSensor('outdoor Temp', '/system/sensors/temperatures/outdoor_t1')
        self.sensors.registerSensor('supply Temp Setpoint', '/system/sensors/temperatures/supply_t1_setpoint')
        self.sensors.registerSensor('supply Temp', '/system/sensors/temperatures/supply_t1')
        self.sensors.registerSensor('return Temp', '/system/sensors/temperatures/return')
        await self.sensors.update()

#    async def initialize(self):
#        result = await self.request('get', '/')
     #   decrypted_result = decrypt(resutl)
     #   print decrypted_result

#        self.config = Config(result['config'], self.request)
#        self.groups = Groups(result['groups'], self.request)
#        self.lights = Lights(result['lights'], self.request)
#        self.scenes = Scenes(result['scenes'], self.request)
#        self.sensors = Sensors(result['sensors'], self.request)

    async def request(self, path):

        headers = {'User-agent': 'TeleHeater/2.2.3' ,'Accept': 'application/json'}
        
        """Make a request to the API."""
        url = 'http://{}'.format(self.host)
        
        url += path

        try:
            async with self.websession.get(url, headers=headers) as res:
                data = await res.text()
                return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self.host, err)
            ) from None

    async def submit(self, path, data):
        headers = {'User-agent': 'TeleHeater/2.2.3' ,'Accept': 'application/json'}
        
        """Make a request to the API."""
        url = 'http://{}'.format(self.host)
        
        url += path

        try:
            async with self.websession.put(url, data=data, headers=headers) as req:
                await req.text()

        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error putting data to {}: {}'.format(self.host, err)
            ) from None


    async def get(self, path):
        encrypted = await self.request(path) 
        result = self.encryption.decrypt(encrypted)
        jsondata =  json.loads(result)
        return jsondata

    async def set_value(self, path, value):
        data = json.dumps({"value": value})
        encrypted = self.encryption.encrypt(data)
        result = await self.submit(path, encrypted)
        return result
    
            

