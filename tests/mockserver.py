import requests
import json
from flask import jsonify
from flask import make_response
from threading import Thread
from bosch_thermostat_http.encryption import Encryption

class MockServer(Thread):
    def __init__(self, port=5000):
        super().__init__()
        from flask import Flask
        self.port = port
        self.app = Flask(__name__)
        self.url = "http://localhost:%s" % self.port

        self.app.add_url_rule("/shutdown", view_func=self._shutdown_server)

        self._encryption = Encryption("xxx", "xxx")

    def _shutdown_server(self):
        from flask import request
        if not 'werkzeug.server.shutdown' in request.environ:
            raise RuntimeError('Not running the development server')
        request.environ['werkzeug.server.shutdown']()
        return 'Server shutting down...'

    def shutdown_server(self):
        requests.get("http://localhost:%s/shutdown" % self.port)
        self.join()

    def add_callback_response(self, url, callback, methods=('GET',)):
        self.app.add_url_rule(url, view_func=callback, methods=methods)

    def add_json_response(self, url, serializable, methods=('GET',)):
        def callback():
            return jsonify(serializable)

        self.add_callback_response(url, callback, methods=methods)

    def add_encrypted_json_response(self, url, serializable, methods=('GET',)):
        def callback():
            data = json.dumps(serializable)            
            encrypted = self._encryption.encrypt(data)
            response = make_response( encrypted )
            response.mimetype = 'application/json'
            return response
 
        self.add_callback_response(url, callback, methods=methods)

    def run(self):
        self.app.run(port=self.port)