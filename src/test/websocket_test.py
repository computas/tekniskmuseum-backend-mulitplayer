import pytest
import json
import tempfile
import werkzeug
from webapp.api import app, socketio

HARAMBE_PATH = "../data/harambe.png"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        test_client = socketio.test_client(app, flask_test_client=flask_client)
        yield flask_client, test_client


def test_join_game_responds(client):
    """
        tests wether a player is able to join game
    """
    flask_client, ws_client = client

    assert ws_client.is_connected()

    r = ws_client.get_received()

    ws_client.emit("joinGame", {})
    r = ws_client.get_received()

    assert r[0]["name"] == "joinGame"
    print("joingame event: ", r)


def test_classification_correct(client):
    """
        tests wether a player is able to join a game and submit a image
        for classification and get the result from the classification
    """
    flask_client, ws_client = client

    assert ws_client.is_connected()

    ws_client.emit("joinGame", {})

    r = ws_client.get_received()
    print("joined game event", r[0]["args"][0])
    args = json.loads(r[0]["args"][0])
    game_id = args["game_id"]
    print("game id: ", game_id)
    with open(HARAMBE_PATH, "rb") as hh:
        data_stream = hh.read()

        tmp = tempfile.SpooledTemporaryFile()
        tmp.write(data_stream)
        tmp.seek(0)
        # Create file storage object containing the image
        content_type = "image/png"
        image = werkzeug.datastructures.FileStorage(
            stream=tmp, filename=HARAMBE_PATH, content_type=content_type
        )

        data = {"game_id": game_id, "time_left": 1}

        ws_client.emit("classify", data, image.stream.read())

    r = ws_client.get_received()

    print("prediction", r)
    assert r[0]["name"] == "prediction"
    assert type(r[0]["args"][0]["certainty"]) is dict
    assert type(r[0]["args"][0]["guess"]) is str
    assert type(r[0]["args"][0]["hasWon"]) is bool


def test_player_correct_state_after_classify(client):
    """TODO: implement me"""
    pass
