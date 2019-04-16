import unittest
import requests
import aiounittest
from .mockserver import MockServer
from bosch_thermostat_http.gateway import Gateway



class TestGateway(aiounittest.AsyncTestCase):

    @classmethod
    def setUpClass(self):
        data_file = open("tests/data_file.txt", "r")
        self.data = data_file.read().splitlines()

        self.server = MockServer(port=1234)
        self.server.start()

    def setUp(self):
        pass

    def test_mock_with_json_encrypted(self):
        self.server.add_encrypted_json_response("/gateway/uuid", 
            {"id":"/gateway/uuid",
             "type":"stringValue",
             "writeable":0,
             "recordable":0,
             "value":"123456789",
             "allowedValues":["<123456789>"]})



        response = requests.get(self.server.url + "/gateway/uuid")

        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])

        self.assertEqual('123456789',response.text)
        print(response.text)
        #self.assertIn('hello', response.json())
        #self.assertEqual('welt', response.json()['hello'])    
    
    @classmethod
    def tearDownClass(self):
        self.server.shutdown_server()
    