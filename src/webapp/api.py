"""
    This file contains all entry points for the API. The API will use
    Websockets for most of the communication, although an HTTP route to
    root has been established, since it makes it easy to check if the
    application is live.
"""
import json
import uuid
import datetime
from io import BytesIO
from PIL import Image
from base64 import decodestring, decodebytes
from flask import Flask
from flask import request
from flask_socketio import SocketIO, emit, send, join_room
from werkzeug import exceptions as excp

from webapp import models
from customvision.classifier import Classifier


# Initialize app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=False,)
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
        labels = models.get_n_labels(NUM_GAMES)
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
        state = {"ready": True}
        models.update_game_for_player(game_id, player_id, 1, "Waiting")
        models.update_game_for_player(
            game_id, opponent.player_id, 0, "Waiting"
        )
        emit("get_label", data, room=game_id)
        emit("state_info", json.dumps(state), room=game_id)
        # send(data, room=game_id)
    else:
        state = {"ready": False}
        emit("state_info", json.dumps(state), room=game_id)


def get_label(game_id):
    """
        Provides the client with a new word.
    """
    game = models.get_game(game_id)

    # Check if game complete
    if game.session_num > NUM_GAMES:
        send("Number of games exceeded")

    labels = json.loads(game.labels)
    label = labels[game.session_num - 1]
    norwegian_label = models.to_norwegian(label)
    data = {"label": norwegian_label}
    return json.dumps(data)


@socketio.on("classify")
def handle_classify(data, image):

    # TODO: do classification here
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
