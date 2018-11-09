import base64
import hashlib
import json
import logging

from pyaes import AESModeOfOperationECB, Encrypter, Decrypter, PADDING_NONE

_LOGGER = logging.getLogger(__name__)
version = __version__ = '0.0.1'

class AESCipher(object):
    def __init__(self, magic, access_key, password):
        self.bs = 16
        self.key = hashlib.md5(bytearray(access_key, "utf8") + magic).digest() + \
                   hashlib.md5(magic + bytearray(password, "utf8")).digest()

    def encrypt(self, raw):
        if len(raw) % self.bs != 0:
            raw = self._pad(raw)
        cipher = Encrypter(AESModeOfOperationECB(self.key), padding=PADDING_NONE)
        ciphertext = cipher.feed(raw) + cipher.feed()

        return base64.b64encode(ciphertext)

    def decrypt(self, enc):
        # trying to decrypt empty data fails
        if not enc:
            return ""
        enc = base64.b64decode(enc)
        cipher = Decrypter(AESModeOfOperationECB(self.key), padding=PADDING_NONE)
        decrypted = cipher.feed(enc) + cipher.feed()
        return decrypted.decode("utf8").rstrip(chr(0))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(0)


class Gateway(object):
    _magic = bytearray.fromhex("867845e97c4e29dce522b9a7d3a3e07b152bffadddbed7f5ffd842e9895ad1e4")

    host = None

    serial_number = None
    access_key = None
    password = None

    encryption = None

    def __init__(self, serial_number, access_key, password, host, sasl_mech="DIGEST-MD5"):
        """
        :param serial_number:
        :param access_key:
        :param password:
        :param host:
        :param sasl_mech:
        """
        serial_number = str(serial_number)
        self.serial_number = serial_number
        self.access_key = access_key
        self.password = password
        self.host = host

        self.encryption = AESCipher(self._magic, access_key, password)
  
    async def encrypt(self, data):
        return self.encryption.encrypt(data)

    async def decrypt(self, data):
        return self.encryption.decrypt(data)

    async def initialize(self):
        result = await self.request('get', '/')
        decrypted_result = decrypt(resutl)
        print decrypted_result

#        self.config = Config(result['config'], self.request)
#        self.groups = Groups(result['groups'], self.request)
#        self.lights = Lights(result['lights'], self.request)
#        self.scenes = Scenes(result['scenes'], self.request)
#        self.sensors = Sensors(result['sensors'], self.request)


    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        url = 'http://{}/api/'.format(self.host)
        if auth:
            url += '{}/'.format(self.username)
        url += path

        try:
            async with self.websession.request(method, url, json=json) as res:
                if res.content_type != 'application/json':
                    raise ResponseError(
                        'Invalid content type: {}'.format(res.content_type))
                data = await res.json()
                _raise_on_error(data)
                return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self.host, err)
            ) from None

