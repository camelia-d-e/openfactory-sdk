from flask import Flask, send_from_directory

class ClientApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/")
        def index():
            return send_from_directory('static', 'index.html')

    def run(self):
        self.app.run()

if __name__ == "__main__":
    my_app = ClientApp()
    my_app.run()