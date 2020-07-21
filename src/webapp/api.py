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
    game_id = models.check_player2_in_mulitplayer(player_id)
    if game_id is not None:
        # Update mulitplayer table by inserting player_id for player_2 and
        # change state of palyer_1 in PIG to "Ready"
        models.update_mulitplayer(player_id, game_id)
        models.insert_into_players(player_id, game_id, "Ready")
        join_room(game_id)
        data = {
            "player_id": player_id,
            "game_id": game_id
        }
        send(json.dumps(data), sid=game_id)
    else:
        game_id = uuid.uuid4().hex
        labels = models.get_n_labels(NUM_GAMES)
        today = datetime.datetime.today()
        models.insert_into_games(game_id, json.dumps(labels), today)
        models.insert_into_players(player_id, game_id, "Waiting")
        models.insert_into_mulitplayer(game_id, player_id, None)
        join_room(game_id)
        data = {
            "player_id": player_id,
            "game_id": game_id
        }
        send(json.dumps(data), sid=game_id)


@socketio.on("newRound")
def handle_newRound(json_data):
    # TODO: implement me!
    player_id = request.sid
    data = json.loads(json_data)
    game_id = data["game_id"]
    models.update_game_for_player(game_id, player_id, 0, "ReadyToDraw")
    opponent = models.get_opponent(game_id, player_id)
    if opponent.state == "ReadyToDraw":
        data = get_label(game_id)
        models.update_game_for_player(game_id, player_id, 1, "Waiting")
        models.update_game_for_player(game_id, opponent.player_id, 0, "Waiting")
        send(data, room=game_id)
    else:
        send("Player" + player_id + "is done", room=game_id)


def get_label(game_id):
    """
        Provides the client with a new word.
    """
    game = models.get_record_from_game(game_id)

    # Check if game complete
    if game.session_num > NUM_GAMES:
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
    # data = json.loads(json_data)
    # TODO: do classification here
    response = {
        "foo": "bar"
    }
    emit("prediction", response)


@socketio.on("endGame")
def handle_endGame(json_data):
    """
        Event which ends the final game of the two players. The players provide
        their scores and the player with the highest score is deemed the winner.
        The two scores are finally stored in the database.
    """
    date = datetime.datetime.today()
    data = json.loads(json_data)
    # Get data from given player
    game_id = data["gameId"]
    score_player = data["score"]
    player_id = data["playerId"]
    name_player = data["name"]
    # Insert score information into db
    models.insert_into_scores(name_player, score_player, date)
    # Create a list containing player data which is sent out to both players
    return_data = {
        "score": score_player,
        "playerId": player_id
    }
    emit("endGame", json.dumps(return_data), room=game_id)
