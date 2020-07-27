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
        test_client1 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        test_client2 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        yield flask_client, test_client1, test_client2


def test_join_game_responds(client):
    """
        tests wether a player is able to join game
    """
    flask_client, ws_client1, ws_client2 = client

    assert ws_client1.is_connected()

    r = ws_client1.get_received()

    ws_client1.emit("joinGame", {})
    r = ws_client1.get_received()

    assert r[0]["name"] == "joinGame"
    print("joingame event: ", r)


def test_classification_correct(client):
    """
        tests wether a player is able to join a game and submit a image
        for classification and get the result from the classification
    """
    flask_client, ws_client1, ws_client2 = client

    assert ws_client1.is_connected()

    ws_client1.emit("joinGame", {})

    r = ws_client1.get_received()
    print("joined game event", r[0]["args"][0])
    args = r[0]["args"][0]
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

        ws_client1.emit("classify", data, image.stream.read())

    r = ws_client1.get_received()

    print("prediction", r)
    assert r[0]["name"] == "prediction"
    assert type(r[0]["args"][0]["certainty"]) is dict
    assert type(r[0]["args"][0]["guess"]) is str
    assert type(r[0]["args"][0]["hasWon"]) is bool


def test_player_not_same_playerid(client):
    """TODO: implement me"""
    flask_client, ws_client1, ws_client2 = client

    ws_client1.emit("joinGame", {})
    ws_client2.emit("joinGame", {})

    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()

    print(r1)
    print(r2)
    assert r1[0]["args"][0]["player_id"] != r2[0]["args"][0]["player_id"]


def test_player_can_finish_game(client):
    """TODO: implement me"""
    flask_client, ws_client1, ws_client2 = client

    ws_client1.emit("joinGame", {})
    ws_client2.emit("joinGame", {})

    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    game_id = r1[0]["args"][0]["game_id"]
    print(f"game_id: {game_id}")
    for i in range(3):
        ws_client1.emit("getLabel", game_id)
        ws_client2.emit("getLabel", game_id)

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

            ws_client1.emit("classify", data, image.stream.read())
            image.seek(0)
            ws_client2.emit("classify", data, image.stream.read())

        r1 = ws_client1.get_received()
        r2 = ws_client2.get_received()

        print(r1)
        print(r2)
        assert not r1[0]["args"][0]["hasWon"]
        assert not r2[0]["args"][0]["hasWon"]
