"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
import json
import uuid
import datetime
from webapp import models
from utilities import setup
from flask import Flask
from flask import request
from customvision.classifier import Classifier
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
app.config.from_object("utilities.setup.Flask_config")
models.db.init_app(app)
models.create_tables(app)
models.seed_labels(app, "./dict_eng_to_nor.csv")
classifier = Classifier()


@socketio.on("connect")
def connect():
    print("===== client connected =====")


@socketio.on("disconnect")
def disconnect():
    player_id = request.sid
    player = models.get_player(player_id)
    game = models.get_game(player.game_id)
    if player_id == models.get_mulitplayer(player.game_id).player_1:
        id = "1"
    else:
        id = "2"
    emit("game_over", "Player " + id + " left", room=game.game_id)
    models.delete_session_from_game(game.game_id)
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
    game_id = models.check_player2_in_mulitplayer(player_id)

    if game_id is not None:
        # Update mulitplayer table by inserting player_id for player_2 and
        # change state of palyer_1 in PIG to "Ready"
        models.update_mulitplayer(player_id, game_id)
        models.insert_into_players(player_id, game_id, "Ready")
        join_room(game_id)

        data = {
            "player": "player_2",
            "player_id": player_id,
            "game_id": game_id,
        }
        state = {
            "ready": True
        }
        emit("player_info", json.dumps(data), sid=player_id)
        emit("state_info", json.dumps(state), room=game_id)

    else:
        game_id = uuid.uuid4().hex
        labels = models.get_n_labels(setup.NUM_GAMES)
        today = datetime.datetime.today()
        models.insert_into_games(game_id, json.dumps(labels), today)
        models.insert_into_players(player_id, game_id, "Waiting")
        models.insert_into_mulitplayer(game_id, player_id, None)
        join_room(game_id)

        data = {
            "player": "player_1",
            "player_id": player_id,
            "game_id": game_id
        }
        state = {
            "ready": False
        }
        emit("player_info", json.dumps(data), sid=player_id)
        emit("state_info", json.dumps(state), room=game_id)


@socketio.on("newRound")
def handle_newRound(json_data):
    player_id = request.sid
    data = json.loads(json_data)
    game_id = data["game_id"]
    models.update_game_for_player(game_id, player_id, 0, "ReadyToDraw")
    opponent = models.get_opponent(game_id, player_id)
    if opponent.state == "ReadyToDraw":
        data = get_label(game_id)
        state = {
            "ready": True
        }
        models.update_game_for_player(game_id, player_id, 0, "Drawing")
        models.update_game_for_player(game_id, opponent.player_id, 0, "Drawing")
        emit("get_label", data, room=game_id)
        emit("state_info", json.dumps(state), room=game_id)
    else:
        state = {
            "ready": False
        }
        emit("state_info", json.dumps(state), room=game_id)


def get_label(game_id):
    """
        Provides the client with a new word.
    """
    game = models.get_game(game_id)

    # Check if game complete
    if game.session_num > setup.NUM_GAMES:
        send("Number of games exceeded")

    labels = json.loads(game.labels)
    label = labels[game.session_num - 1]
    norwegian_label = models.to_norwegian(label)
    data = {
        "label": norwegian_label
    }
    return json.dumps(data)


@socketio.on("classify")
def handle_classify(json_data):
    pass


@socketio.on("endGame")
def handle_endGame(json_data):
    # TODO: implement me!
    data = json.loads(json_data)
    emit("endGame", data)
