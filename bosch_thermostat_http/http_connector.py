"""HTTP connector class to Bosch thermostat."""
from aiohttp import client_exceptions
from .const import (HTTP_HEADER)

from .errors import RequestError, ResponseError


class HttpConnector:
    """HTTP connector to Bosch thermostat."""

    def __init__(self, host, websession):
        self._host = host
        self._websession = websession
        self._request_timeout = 10

    async def request(self, path):
        """ Make a get request to the API. """
        try:
            async with self._websession.get(
                    self._format_url(path),
                    headers=HTTP_HEADER, timeout=self._request_timeout) as res:
                if res.status == 200:
                    if res.content_type != 'application/json':
                        raise ResponseError('Invalid content type: {}'.
                                            format(res.content_type))
                    else:
                        data = await res.text()
                        return data
                else:
                    raise ResponseError('Invalid response code: {}'.
                                        format(res.status))
        except (client_exceptions.ClientError,
                client_exceptions.ClientConnectorError,
                TimeoutError) as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self._host, err)
            )

    async def submit(self, path, data):
        """Make a put request to the API."""
        try:
            async with self._websession.put(
                    self._format_url(path),
                    data=data,
                    headers=HTTP_HEADER,
                    timeout=self._request_timeout) as req:
                data = await req.text()
                return data
        except (client_exceptions.ClientError, TimeoutError) as err:
            raise RequestError(
                'Error putting data to {}, path: {}, message: {}'.
                format(self._host, path, err)
            )

    def _format_url(self, path):
        """ Format URL to make requests to gateway. """
        return 'http://{}{}'.format(self._host, path)

    def set_timeout(self, timeout=10):
        """ Set timeout for API calls. """
        self._request_timeout = timeout
