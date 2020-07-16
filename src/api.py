"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
import json
import uuid
import models
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
NUM_GAMES = 3  # This is placed here temporarily(?)

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
    """
        Check if player2 is none in mulitplayer table.
        * If check is false create new mulitplayer game.
        * If check is true insert player where player2 is none and start
          the game.
    """
    player_id = request.sid
    game_id = models.check_player2_in_mulitplayer
    if game_id is not None:
        models.update_mulitplayer(player_id, game_id)
        models.insert_into_player_in_game(player_id, game_id, "Ready")  # State not sure
        join_room(game_id)

    else:
        game_id = uuid.uuid4().hex
        labels = models.get_n_labels(NUM_GAMES)
        models.insert_into_games(game_id, labels, date)
        models.insert_into_player_in_game(player_id, game_id, "Waiting")
        models.insert_into_mulitplayer((player_id, None, game_id))
        join_room(game_id)
    pass


@socketio.on("newRound")
def handle_newRound(json_data):
    # TODO: implement me!
    request.sid
    data = json.loads(json_data)
    models.update_player_in_game(data.player_id, data.game_id, "Ready")
    
    while models.get_record_from_player_in_game()
    


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

