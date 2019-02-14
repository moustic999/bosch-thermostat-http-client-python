"""Gateway module connecting to Bosch thermostat."""
import json
import asyncio
import aiohttp
from aiohttp import client_exceptions

from .const import (HTTP_HEADER, TIMEOUT, GET, UUID, SUBMIT, DHW, HC, GATEWAY,
                    SENSORS, TYPE_INFO, ROOT_PATHS, GATEWAY_PATH_LIST, 
                    SYTEM_CAPABILITIES, DETAILED_CAPABILITIES, SENSORS_CAPABILITIES)
from .encryption import Encryption
from .gateway_info import GatewayInfo
from .circuits import Circuits
from .sensors import Sensors
 
from .helper import RequestError
from .helper import deep_into


class Gateway:
    """Gateway to Bosch thermostat."""

    def __init__(self, websession, host, access_key, password=None):
        """
        :param access_key:
        :param password:
        :param host:
        """
        self._host = host
        self._websession = websession
        self._encryption = None

        if password:
            access_token = access_key.replace('-','')
            self._encryption = Encryption(access_token, password)
        else:
            self._encryption = Encryption(access_key)

        self._request_timeout = 10
        self._monitored_keys = {}
        # {'keyname': self._data[HC][HC_NAME][HC_CURRENT_ROOMSETPOINT]

        self._data = {
            GATEWAY: None,
            HC: None,
            DHW: None,
            SENSORS: None
        }
        self._empty_json = self.encrypt("{}")
        self._requests = {
            GET: self.get,
            SUBMIT: self.set_value
        }

    def encrypt(self, data):
        """ Encrypt message to gateway. """
        return self._encryption.encrypt(data)

    def decrypt(self, data):
        """ Decrypt message from gateway. """
        return self._encryption.decrypt(data)

    def format_url(self, path):
        """ Format URL to make requests to gateway. """
        return 'http://{}{}'.format(self._host, path)

    def get_items(self, data_type):
        """ Get items on types like Sensors, Heating Circuits etc. """
        return self._data[data_type].get_items()

    def set_timeout(self, timeout):
        self._request_timeout = timeout

    @property
    def access_key(self):
        """ Return key to store in config entry."""
        return self._encryption.key

    @property
    def heating_circuits(self):
        """ Get circuit list. """
        return self._data[HC].circuits
    
    @property
    def gateway_info(self):
        """ Get gateway info list. """
        return self._data[GATEWAY]

    @property
    def sensors(self):
        """ Get sensors list. """
        return self._data[SENSORS].sensors

    def get_property(self, qtype, property_name):
        """ Get property of gateway info. """
        if qtype == 'info':
            return self._data[GATEWAY].get_property(property_name)
        return None

    def get_request(self):
        """ For testing purposes only. Delete it in final lib."""
        return self.get

    async def get_info(self):
        gateway_info = []
        for key in GATEWAY_PATH_LIST:
            response = self.get(key)
            if 'value' in response:
                gateway_info.append({response['id'].split('/').pop() : response['value']})
        return gateway_info

    async def get_capabilities(self):
        capabilities = []
        for key, values in SYTEM_CAPABILITIES.items():
            for value in values:                  
                response = await self.get(value) 
                if (response['type'] == 'refEnum'):
                    for ref in response['references']:
                        if (key in DETAILED_CAPABILITIES) or (ref['id'] in SENSORS_CAPABILITIES):
                            capability = {
                                    'name' : None,
                                    'type' : None,
                                }
                            capability['name'] = ref["id"].split('/').pop()
                            capability['type'] = key                     
                            capabilities.append(capability)    
                       
        return  capabilities

    async def initialize_gatewayinfo(self, restored_data=None):
        self._data[GATEWAY] = GatewayInfo(self._requests, GATEWAY)
        await self._data[GATEWAY].update()

    async def initialize_circuits(self, circ_type, restored_data=None):
        # type = HC, DHW
        self._data[circ_type] = Circuits(self._requests, circ_type)
        await self._data[circ_type].initialize(restored_data)

    async def initialize_sensors(self, restored_data=None):
        self._data[SENSORS] = Sensors(self._requests)
        await self._data[SENSORS].initialize(restored_data)
            # here can sensors from memory
        # await self._data[SENSORS].update()

    async def initialize(self):
        """ Initialize gateway asynchronously. """
        await self.initialize_gatewayinfo()
        await self.initialize_sensors()
        await self.initialize_circuits(HC, None)
        await self.initialize_circuits(DHW, None)
    
    async def rawscan(self):
        """ print out all info from gateway """
        for root in ROOT_PATHS:
            await deep_into(root, self.get, True)

    async def check_connection(self):
        try:
            await self.initialize_gatewayinfo()
            return self.get_property(TYPE_INFO, UUID)
        except RequestError:
            return False

    async def _request(self, path):
        """ Make a get request to the API. """
        try:
            async with self._websession.get(
                    self.format_url(path),
                    headers=HTTP_HEADER,timeout=self._request_timeout) as res:
                if res.status != 200:
                    print("request returned status : ", res.status)
                    return None
                data = await res.text()
                return data
        except (client_exceptions.ClientError, TimeoutError) as err:
            raise RequestError(
                'Error getting data from {}, path: {}, message: {}'
                .format(self._host, path, err)
            )

    async def _submit(self, path, data):
        """Make a put request to the API."""
        try:
            async with self._websession.put(
                    self.format_url(path),
                    data=data,
                    headers=HTTP_HEADER) as req:
                data = await req.text()
                return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error putting data to {}, path: {}, message: {}'.
                format(self._host, path, err)
            )

    async def get(self, path):
        """ Get message from API with given path. """
        encrypted = await self._request(path)
        result = self._encryption.decrypt(encrypted)
        jsondata = json.loads(result)
        return jsondata

    async def _set(self, path, data):
        """ Send message to API with given path. """
        encrypted = self._encryption.encrypt(data)
        result = await self._submit(path, encrypted)
        return result

    async def set_value(self, path, value):
        """ Set value for thermostat. """
        data = json.dumps({"value": value})
        result = await self._set(path, data)
        return result