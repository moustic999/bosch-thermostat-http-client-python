import unittest
import json
from bosch_thermostat_http.encryption import Encryption


class AesTest(unittest.TestCase):


    def setUp(self):
        self.client = Encryption('abc1abc2abc3abc4', 'passworddddd')

    # encrypt and decrypt a string
    def test_crypt(self):
        text = 'super_secret'
        text_encrypted = self.client.encrypt(text).decode('utf-8')
        print(text_encrypted)
        text_decrypted = self.client.decrypt(text_encrypted)
        self.assertEqual(text, text_decrypted)

    # decrypt a known encrypted string
    def test_decrypt(self):
        text_encrypted = 'NSsVDVOegzLWF+Kpgcscgw=='
        text_decrypted = self.client.decrypt(text_encrypted)
        self.assertEqual("super_secret", text_decrypted)


if __name__ == '__main__':
    unittest.main()