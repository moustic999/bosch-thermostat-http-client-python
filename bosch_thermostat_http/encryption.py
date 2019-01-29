import base64
import hashlib

from pyaes import AESModeOfOperationECB, Encrypter, Decrypter, PADDING_NONE

from .const import BS, MAGIC


class Encryption:

    def __init__(self, access_key, password):
        self._bs = BS
        key_arrray = bytearray(access_key, "utf8")
        password_array = bytearray(password, "utf8")
        self.key = (hashlib.md5(key_arrray + MAGIC).digest() +
                    hashlib.md5(MAGIC + password_array).digest())

    def encrypt(self, raw):
        if len(raw) % self._bs != 0:
            raw = self._pad(raw)
        cipher = Encrypter(
            AESModeOfOperationECB(self.key),
            padding=PADDING_NONE)
        ciphertext = cipher.feed(raw) + cipher.feed()

        return base64.b64encode(ciphertext)

    def decrypt(self, enc):
        # trying to decrypt empty data fails
        if not enc:
            return ""
        if len(enc) % self._bs != 0:
            enc = self._pad(enc)
        enc = base64.b64decode(enc)
        cipher = Decrypter(
            AESModeOfOperationECB(self.key),
            padding=PADDING_NONE)
        decrypted = cipher.feed(enc) + cipher.feed()
        return decrypted.decode("utf8").rstrip(chr(0))

    def _pad(self, s):
        return s + (self._bs - len(s) % self._bs) * chr(0)
