"""HTTP connector class to Bosch thermostat."""
import logging
import asyncio
import json
from asyncio import TimeoutError as AsyncTimeout
from aiohttp.client_exceptions import (
    ClientResponseError,
    ClientConnectorError,
    ServerTimeoutError,
    ClientError
)

from .const import HTTP_HEADER, KEEP_ALIVE, CONNECTION, APP_JSON
from .exceptions import DeviceException, ResponseException

_LOGGER = logging.getLogger(__name__)


class HttpConnector:
    """HTTP connector to Bosch thermostat."""

    def __init__(self, host, websession, encryption):
        """Init of HTTP connector."""
        self._lock = asyncio.Lock()
        self._host = host
        self._websession = websession
        self._request_timeout = 10
        self._encryption = encryption

    @property
    def encryption_key(self):
        return self._encryption.key

    async def _request(self, method, path, **kwargs):
        _LOGGER.debug("Sending request to %s", path)

        async def get_response(method_name, res):
            if method_name == 'put':
                data = await res.text()
                if not data and res.status == 204:
                    return True
                return data
            if method_name == 'get' and res.status == 200 and res.content_type == APP_JSON:
                data = await res.json(
                    loads=self._encryption.json_encrypt
                )
                return data
            raise ResponseException(res)

        try:
            async with method(
                self._format_url(path),
                **kwargs
            ) as res:
                return await get_response(method.__name__, res)
        except ClientResponseError as err:
            raise DeviceException(f"URI {path} doesn not exist: {err}")
        except ClientConnectorError as err:
            raise DeviceException(err)
        except ResponseException as err:
            raise DeviceException(f"Error requesting data from {path}: {err}")
        except ClientError as err:
            raise DeviceException(f"Error connecting to client {path}: {err}")
        except AsyncTimeout:
            raise DeviceException(f"Connection timed out for {path}.")

    
    def _format_url(self, path):
        """Format URL to make requests to gateway."""
        return f"http://{self._host}{path}"

    def set_timeout(self, timeout=10):
        """Set timeout for API calls."""
        self._request_timeout = timeout

    async def get(self, path):
        """Get message from API with given path."""
        async with self._lock:
            return await self._request(
                self._websession.get,
                path,
                headers=HTTP_HEADER,
                timeout=self._request_timeout,
                skip_auto_headers=["Accept-Encoding", "Accept"],
                raise_for_status=True
            )

    async def put(self, path, value):
        """Send message to API with given path."""
        async with self._lock:
            return await self._request(
                self._websession.put,
                path,
                data=self._encryption.encrypt(json.dumps({"value": value})),
                headers=HTTP_HEADER,
                timeout=self._request_timeout,
            )
