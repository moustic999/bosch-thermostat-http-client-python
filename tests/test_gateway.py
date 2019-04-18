import unittest
import json
import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web, ClientSession
from bosch_thermostat_http.gateway import Gateway
from bosch_thermostat_http.encryption import Encryption
from .gateway_test_server import GatewayTestServer



class GatewayTestCase(AioHTTPTestCase):

    async def get_application(self):
        return web.Application()

    async def get_server(self, app):
        server = GatewayTestServer()
        return server

    
    @unittest_run_loop
    async def test_get(self):
        async with ClientSession() as session:
            loop = asyncio.get_event_loop()

            gtw_host = str(self.server.host)+':' + str(self.server.port)
            gateway = Gateway(session, gtw_host, 'aaa', 'xxx')
            task = loop.create_task(gateway.get('/gateway/uuid'))
            request = await self.server.receive_request()
            assert request.path_qs == '/gateway/uuid'
            self.server.send_response(request, text='{"id":"/gateway/uuid"}', content_type='application/json')
            g_resp = await task
            assert {'id':'/gateway/uuid'} == g_resp
    
