import pytest
import json
import tempfile
import werkzeug
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
    assert r[0]["name"] == "joinGame"


def test_classification_correct(client):
    flask_client, ws_client = client

    assert ws_client.is_connected()

    # ws_client.emit("joinGame", {})

    path = "harambe.png"
    with open(path, "rb") as hh:
        data_stream = hh.read()

        tmp = tempfile.SpooledTemporaryFile()
        tmp.write(data_stream)
        tmp.seek(0)
        # Create file storage object containing the image
        content_type = "image/png"
        image = werkzeug.datastructures.FileStorage(
            stream=tmp, filename=path, content_type=content_type
        )

        ws_client.emit("classify", {}, image)

    r = ws_client.get_received()

    assert r[1]["name"] == "prediction"
    print(r[1])
    assert False
