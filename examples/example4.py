from bosch_thermostat_http.encryption import Encryption

client = Encryption('xxx', 'xxx2')
text_encrypted = client.encrypt("testing text")
print(text_encrypted)
#text_encrypted = 'NSsVDVOegzLWF+Kpgcscgw=='
text_decrypted = client.decrypt(text_encrypted)
print(text_decrypted)
