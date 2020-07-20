import pytest
import json
from webapp.api import app, socketio


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        test_client = socketio.test_client(app)
        yield flask_client, test_client

def test_classify_responds(client):
    flask_client, ws_client = client

    
    
    assert ws_client.is_connected()

    r = ws_client.get_received()

    ws_client.emit("joinGame", {})
    ws_client.emit("classify", json.dumps({}))
    r = ws_client.get_received()

    print(r)
    assert r[0]["name"] == "prediction"
    assert r[0]["args"][0]["foo"] == "bar"