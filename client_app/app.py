from flask import Flask, render_template
from openfactory_api_client import OpenFactoryAPIClient


class ClientApp:
    """Client app that displays devices states."""

    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.api_client = OpenFactoryAPIClient(base_url="http://localhost:8000")

    def setup_routes(self):
        @self.app.route("/")
        def index():
            return render_template('index.html', devices=self.api_client.get_all_devices() )

        @self.app.route("/devices/<device_uuid>/status")
        def device_status(device_uuid):
            pass


    def run(self):
        self.app.run(port=3000)


if __name__ == "__main__":
    my_app = ClientApp()
    my_app.run()
