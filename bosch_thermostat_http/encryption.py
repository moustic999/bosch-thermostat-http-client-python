""" Encryption logic of Bosch thermostat. """
import base64
import hashlib

from pyaes import PADDING_NONE, AESModeOfOperationECB, Decrypter, Encrypter

from .const import BS, MAGIC

class Encryption:
    """ Encryption class. """

    def __init__(self, access_key, password):
        """
        :param str access_key: Access key to Bosch thermostatself.
        :param str password: Password created with Bosch app.
        """
        self._bs = BS
        key_arrray = bytearray(access_key, "utf8")
        password_array = bytearray(password, "utf8")
        self.key = (hashlib.md5(key_arrray + MAGIC).digest() +
                    hashlib.md5(MAGIC + password_array).digest())

    def encrypt(self, raw):
        """ Encrypt raw message. """
        if len(raw) % self._bs != 0:
            raw = self._pad(raw)
        cipher = Encrypter(
            AESModeOfOperationECB(self.key),
            padding=PADDING_NONE)
        ciphertext = cipher.feed(raw) + cipher.feed()
        return base64.b64encode(ciphertext)

    def decrypt(self, enc):
        """
        Decrypt raw message only if length > 2.
        Padding is not working for lenght less than 2.
        """
        if enc and len(enc) > 2:
            if len(enc) % self._bs != 0:
                enc = self._pad(enc)
            enc = base64.b64decode(enc)
            cipher = Decrypter(
                AESModeOfOperationECB(self.key),
                padding=PADDING_NONE)
            decrypted = cipher.feed(enc) + cipher.feed()
            return decrypted.decode("utf8").rstrip(chr(0))
        return "{}"

    def _pad(self, _s):
        """ Padding of encryption. """
        return _s + (self._bs - len(_s) % self._bs) * chr(0)
