"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
import json
import uuid
from flask import Flask
from flask import request
from flask_socketio import (
    SocketIO,
    emit,
    send,
    join_room
)



# Initialize app
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


@socketio.on("joinGame")
def handle_joinGame(json_data):
    # TODO: implement me
    pass

@socketio.on("classify")
def handle_classify(json_data):
    data = json.loads(json_data)
    # TODO: do classification here
    response = {
        "foo": "bar"
        }
    emit("prediction", response)

@socketio.on("endGame")
def handle_endGame(json_data):
    # TODO: implement me!
    data = json.loads(json_data)

