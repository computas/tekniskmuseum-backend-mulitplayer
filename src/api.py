"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
import json
import subprocess
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send
from flask_socketio import emit

app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    engineio_logger=False,
)


@socketio.on("connect")
def connect():
    print("===== client connected =====")

@socketio.on("disconnect")
def disconnect():
    print("=== client disconnected ===")

@socketio.on("message")
def handle_message(message):
    print("client: " + str(message))


@socketio.on("startGame")
def handle_startGame(data):
    datadict = json.loads(data)
    for key, value in datadict.items():
        print(key, ": ", value)

