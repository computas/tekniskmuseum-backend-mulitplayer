import pytest
import json
from webapp.api import app, socketio


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        test_client = socketio.test_client(app, flask_test_client=flask_client)
        yield flask_client, test_client


def test_join_game_responds(client):
    flask_client, ws_client = client

    assert ws_client.is_connected()

    r = ws_client.get_received()

    ws_client.emit("joinGame", {})
    r = ws_client.get_received()

    print(r)
    assert r[0]["name"] == "message"


def test_classification_correct(client):
    flask_client, ws_client = client

    assert ws_client.is_connected()

    # ws_client.emit("joinGame", {})

    with open("harambe.png", "rb") as hh:
        ws_client.emit("classify", json.dumps({}), hh)

    r = ws_client.get_received()

    assert r[1]["name"] == "prediction"
    print(r[1])
    assert False
