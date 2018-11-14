import base64
import hashlib
import logging

from pyaes import AESModeOfOperationECB, Encrypter, Decrypter, PADDING_NONE

_LOGGER = logging.getLogger(__name__)
version = __version__ = '0.0.1'

class Encryption(object):
   
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
        if len(enc) % self.bs != 0:
            enc = self._pad(enc)
        enc = base64.b64decode(enc)
        cipher = Decrypter(AESModeOfOperationECB(self.key), padding=PADDING_NONE)
        decrypted = cipher.feed(enc) + cipher.feed()
        return decrypted.decode("utf8").rstrip(chr(0))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(0)