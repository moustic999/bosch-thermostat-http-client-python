import unittest
import json
import asyncio
import pytest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web, ClientSession
from bosch_thermostat_http.http_connector import HttpConnector
from bosch_thermostat_http.encryption import Encryption
from bosch_thermostat_http.errors import *
from .gateway_test_server import GatewayTestServer

TIMEOUT=1

@pytest.mark.asyncio
async def test_request_complete():
    async with GatewayTestServer() as server:
        async with ClientSession() as session:
            loop = asyncio.get_event_loop()
            gtw_host = str(server.host)+':' + str(server.port)
            httpConnector = HttpConnector(gtw_host, session)
            task = loop.create_task(httpConnector.request('/gateway/uuid'))
            request = await server.receive_request()
            assert request.path_qs == '/gateway/uuid'
            server.send_response(request, text='{"id":"/gateway/uuid"}', content_type='application/json')
            response = await task
            assert '{"id":"/gateway/uuid"}' == response
        

@pytest.mark.asyncio
async def test_request_notfound():
    async with GatewayTestServer() as server:
        async with ClientSession() as session:
            loop = asyncio.get_event_loop()
            gtw_host = str(server.host)+':' + str(server.port)
            httpConnector = HttpConnector(gtw_host, session)
            task = loop.create_task(httpConnector.request('/blablabla'))
            request = await server.receive_request()
            assert request.path_qs == '/blablabla'
            server.send_response(request, status=404)
            with pytest.raises(Response404Error):
                await task

@pytest.mark.asyncio
async def test_request_connection_failure(aiohttp_unused_port):
    async with GatewayTestServer() as server:
        async with ClientSession() as session:

            gtw_host = str(server.host)+':' + str(aiohttp_unused_port)
            httpConnector = HttpConnector(gtw_host, session)
            with pytest.raises(RequestError):
                await asyncio.wait_for(httpConnector.request('/blablabla'), TIMEOUT)

@pytest.mark.asyncio
async def test_request_forbidden():
    async with GatewayTestServer() as server:
        async with ClientSession() as session:
            loop = asyncio.get_event_loop()
            gtw_host = str(server.host)+':' + str(server.port)
            httpConnector = HttpConnector(gtw_host, session)
            task = loop.create_task(httpConnector.request('/blablabla'))
            request = await server.receive_request()
            assert request.path_qs == '/blablabla'
            server.send_response(request, status=403)
            with pytest.raises(ResponseError):
                await task