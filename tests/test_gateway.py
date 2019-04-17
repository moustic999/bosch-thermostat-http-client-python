import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from bosch_thermostat_http.gateway import Gateway

class GatewayTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """
        async def handler(request):
            response = web.Response(text={'id':'/gateway/uuid'})
            response.headers['Content-Type'] = 'application/json'
            return response

        app = web.Application()
        app.router.add_get('/gateway/uuid', hello)
        return app

    

    @unittest_run_loop
    async def test_example(self):
        async with aiohttp.ClientSession() as session:
            resp = await self.client.request("GET", "/gateway/uuid")
            assert resp.status == 200
            text = await resp.text()
            assert "Hello, world" in text

   