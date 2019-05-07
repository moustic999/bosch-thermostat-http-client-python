
import pytest
import asyncio
from asynctest import CoroutineMock
from unittest.mock import patch, MagicMock
from aiohttp import web, ClientSession
from bosch_thermostat_http.gateway import Gateway
from bosch_thermostat_http.errors import Response404Error, ResponseError
@pytest.mark.asyncio
async def test_get_success():
     async with ClientSession() as session:
       
        with patch('bosch_thermostat_http.http_connector.HttpConnector.request', new=CoroutineMock(return_value="bla")) as mocked_get:
            with patch('bosch_thermostat_http.encryption.Encryption.decrypt', MagicMock(return_value='{"id": "/gateway/uuid"}')) as mocked_decrypt:
                gateway = Gateway(session, 'bla', 'aaa', 'xxx')
                gtw_resp = await gateway.get('/gateway/uuid')
                mocked_get.assert_called_once_with('/gateway/uuid')
                mocked_decrypt.assert_called_once_with('bla')
                assert gtw_resp == {'id': '/gateway/uuid'}
        
@pytest.mark.asyncio
async def test_get_notfound():
     async with ClientSession() as session:
       
        with patch('bosch_thermostat_http.http_connector.HttpConnector.request', new=CoroutineMock(side_effect=Response404Error())) as mocked_get:
            with patch('bosch_thermostat_http.encryption.Encryption.decrypt', MagicMock(return_value='{"id": "/gateway/uuid"}')) as mocked_decrypt:
                with pytest.raises(ResponseError) as exc_info:
                    gateway = Gateway(session, 'bla', 'aaa', 'xxx')
                    await gateway.get('/gateway/uuid')
                    mocked_get.assert_called_once_with('/gateway/uuid')
                    mocked_decrypt.assert_called_once_with('bla')
                assert 'Path does not exist' in str(exc_info.value)
                assert '/gateway/uuid' in str(exc_info.value)  
   
@pytest.mark.asyncio
async def test_get_invalidjson():
     async with ClientSession() as session:
       
        with patch('bosch_thermostat_http.http_connector.HttpConnector.request', new=CoroutineMock(return_value="bla")) as mocked_get:
            with patch('bosch_thermostat_http.encryption.Encryption.decrypt', MagicMock(return_value='some_invalid_json')) as mocked_decrypt:
                with pytest.raises(ResponseError) as exc_info:
                    gateway = Gateway(session, 'bla', 'aaa', 'xxx')
                    gtw_resp = await gateway.get('/gateway/uuid')
                    mocked_get.assert_called_once_with('/gateway/uuid')
                    mocked_decrypt.assert_called_once_with('bla')
                assert 'Unable to decode Json response' in str(exc_info.value)   

async def test_update_info():
    async with  ClientSession() as session:
        with patch('bosch_thermostat_http.gateway.Gateway.get', new=CoroutineMock(return_value={'id': '/gateway/uuid', 'value':'test_gtw_update'})) as mocked_get:
            gateway = Gateway(session, 'bla', 'aaa', 'xxx')
            await gateway._update_info()
            assert gateway._data['/gateway']['uuid'] == 'test_gtw_update'
