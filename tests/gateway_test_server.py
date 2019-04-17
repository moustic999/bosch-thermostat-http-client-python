import aiohttp
import asyncio
import json
from bosch_thermostat_http.encryption import Encryption

class GatewayTestServer(aiohttp.test_utils.RawTestServer):
    def __init__(self, **kwargs):
        super().__init__(self._handle_request, **kwargs)
        self._requests = asyncio.Queue()
        self._responses = {}                # {id(request): Future}
        self._access_key = kwargs.get('access_key')
        self._password = kwargs.get('password')

    def access_key(self):
        return self._access_key

    def password(self):
        return self._password

    async def close(self):
        ''' cancel all pending requests before closing '''
        for future in self._responses.values():
            future.cancel()
        await super().close()

    async def _handle_request(self, request):
        ''' push request to test case and wait until it provides a response '''
        self._responses[id(request)] = response = asyncio.Future()
        self._requests.put_nowait(request)
        try:
            # wait until test case provides a response
            return await response
        finally:
            del self._responses[id(request)]

    async def receive_request(self):
        ''' wait until test server receives a request '''
        return await self._requests.get()

    def send_response(self, request, data=None):
        ''' send web response from test case to client code '''
       
        json_data = json.dumps(data)
        encryption = Encryption(self._access_key, self._password)
        data_encrypted = encryption.encrypt(json_data)
        response = aiohttp.web.Response(body=data_encrypted)
        response.headers['Content-Type'] = 'application/json'
        self._responses[id(request)].set_result(response)