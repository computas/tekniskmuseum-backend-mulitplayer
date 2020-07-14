"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return "Yes, we're up!", 200
