"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
from customvision.classifier import Classifier
from werkzeug import exceptions as excp
from flask_socketio import SocketIO, emit, send, join_room
from flask import request
from flask import Flask
from base64 import decodestring, decodebytes
from PIL import Image
from io import BytesIO
from webapp import models
from utilities.exceptions import UserError
from utilities import setup
import logging
import os
import json
import uuid
import datetime


# Initialize app
app = Flask(__name__)
logger = False
if "IS_PRODUCTION" in os.environ:
    logger = True

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=logger,
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
    """
        When a player disconnects from a session this function tells the
        other player in the room who left and deletes all records in the
        database connected to the session. Old sessions is also deleted.
    """
    player_id = request.sid
    player = models.get_player(player_id)
    game = models.get_game(player.game_id)
    if player_id == models.get_mulitplayer(player.game_id).player_1:
        id = "1"
    else:
        id = "2"
    data = {
        "game_over": True,
        "player_left": id
    }
    emit("game_over", json.dumps(data), room=game.game_id)
    models.delete_session_from_game(game.game_id)
    print("=== client disconnected ===")


@socketio.on("message")
def handle_message(message):
    print("client: " + str(message))


@socketio.on("filetest")
def handle_filetest(json_data, image):
    print(json_data)
    with open("harambe.png", "wb") as f:
        f.write(image)


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
        player = "player_2"
        is_ready = True

    else:
        game_id = uuid.uuid4().hex
        labels = models.get_n_labels(setup.NUM_GAMES)
        today = datetime.datetime.today()
        models.insert_into_games(game_id, json.dumps(labels), today)
        models.insert_into_players(player_id, game_id, "Waiting")
        models.insert_into_mulitplayer(game_id, player_id, None)
        player = "player_1"
        is_ready = False

    join_room(game_id)
    data = {"player": player, "player_id": player_id, "game_id": game_id}
    state = {"ready": is_ready}
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
        state = {"ready": False}
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
    data = {"label": norwegian_label}
    return json.dumps(data)


@socketio.on("classify")
def handle_classify(data, image):

    image_stream = BytesIO(image)
    allowed_file(image_stream)

    prob_kv, best_guess = classifier.predict_image(image_stream)

    response = {"cerainty": prob_kv, "guess": best_guess, "hasWon": False}
    emit("prediction", response)


@socketio.on("endGame")
def handle_endGame(json_data):
    # TODO: implement me!
    data = json.loads(json_data)
    emit("endGame", data)


@socketio.on_error()
def error_handler(error):
    """
        Captures all Exeptions raised. If error is an Exception, the
        error message is returned to the client. Else the error is
        logged.
    """
    if isinstance(error, UserError):
        emit("error", str(error))
    else:
        app.logger.error(error)


def allowed_file(image):
    """
        Check if image satisfies the constraints of Custom Vision.
    """
    # Ensure the file isn't too large
    too_large = len(image.read()) > 4000000
    # Ensure the file has correct resolution
    image.seek(0)
    pimg = Image.open(image)

    is_png = pimg.format == "PNG"

    height, width = pimg.size
    correct_res = (height >= 256) and (width >= 256)

    image.seek(0)

    if is_png or too_large or not correct_res:
        raise excp.UnsupportedMediaType("Wrong image format")
