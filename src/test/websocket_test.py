import pytest
import json
import tempfile
import werkzeug
from webapp.api import app, socketio

HARAMBE_PATH = "data/harambe.png"


@pytest.fixture
def test_clients():
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        test_client1 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        test_client2 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        yield flask_client, test_client1, test_client2


@pytest.fixture
def four_test_clients():
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        test_client1 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        test_client2 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        test_client3 = socketio.test_client(
            app, flask_test_client=flask_client
        )
        test_client4 = socketio.test_client(
            app, flask_test_client=flask_client
        )

        yield flask_client, test_client1, test_client2, test_client3, test_client4

@pytest.mark.parametrize('data', [
    (''),
    ('{"pair_id": "same_pair_id"}')])
def test_join_game_same_pair_id(test_clients, data, ):
    """
        tests wether a player is able to join game
    """
    _, ws_client1, ws_client2 = test_clients

    ws_client1.emit("joinGame", data)

    r1 = ws_client1.get_received()
    assert r1[0]["name"] == "joinGame"
    assert r1[0]["args"][0]['player_nr'] == 'player_1'
    assert not r1[1]["args"][0]['ready']
    r2 = ws_client2.get_received()
    assert r2 == []

    ws_client2.emit("joinGame", data)

    r1 = ws_client1.get_received()
    assert r1[0]["name"] == "joinGame"
    r2 = ws_client2.get_received()
    assert r2[0]["name"] == "joinGame"
    assert r2[0]["args"][0]['player_nr'] == 'player_2'
    assert r2[1]["args"][0]['ready']


def test_join_game_diff_pair_id(four_test_clients):
    """
        tests wether a player is able to join game
    """
    _, ws_client1_1, ws_client1_2, ws_client2_1, ws_client2_2 = four_test_clients
    data_1 = '{"pair_id": "pair_id_1"}'
    data_2 = '{"pair_id": "pair_id_2"}'

    # the first player is added to both games
    ws_client1_1.emit("joinGame", data_1)

    r11 = ws_client1_1.get_received()
    assert r11[0]["name"] == "joinGame"
    assert r11[0]["args"][0]['player_nr'] == 'player_1'
    assert not r11[1]["args"][0]['ready']
    r21 = ws_client2_1.get_received()
    assert r21 == []

    ws_client2_1.emit("joinGame", data_2)

    r21 = ws_client2_1.get_received()
    assert r21[0]["name"] == "joinGame"
    assert r21[0]["args"][0]['player_nr'] == 'player_1'
    assert not r21[1]["args"][0]['ready']
    r11 = ws_client1_1.get_received()
    assert r11 == []

    # a second player is added to both games
    ws_client1_2.emit("joinGame", data_1)

    r12 = ws_client1_2.get_received()
    assert r12[0]["name"] == "joinGame"
    assert r12[0]["args"][0]['player_nr'] == 'player_2'
    assert r12[1]["args"][0]['ready']
    r11 = ws_client1_1.get_received()
    assert r11[0]["name"] == "joinGame"
    r21 = ws_client2_1.get_received()
    assert r21 == []

    ws_client2_2.emit("joinGame", data_2)

    r2 = ws_client2_2.get_received()
    assert r2[0]["name"] == "joinGame"
    assert r2[0]["args"][0]['player_nr'] == 'player_2'
    assert r2[1]["args"][0]['ready']
    r11 = ws_client1_1.get_received()
    assert r11 == []
    r21 = ws_client2_1.get_received()
    assert r21[0]["name"] == "joinGame"

def test_classification_correct(test_clients):
    """
        tests wether a player is able to join a game and submit a image
        for classification and get the result from the classification
    """
    _, ws_client1, _ = test_clients

    assert ws_client1.is_connected()

    ws_client1.emit("joinGame", 'classify')
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


def test_players_not_with_same_playerid(test_clients):
    """TODO: implement me"""
    _, ws_client1, ws_client2 = test_clients

    ws_client1.emit("joinGame", '')
    ws_client2.emit("joinGame", '')

    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    assert r1[0]["args"][0]["player_id"] != r2[0]["args"][0]["player_id"]
    assert r1[0]["args"][0]["game_id"] == r2[0]["args"][0]["game_id"]

def test_players_can_keep_guessing(test_clients):
    _, ws_client1, ws_client2 = test_clients
    ws_client1.emit("joinGame", '')
    ws_client2.emit("joinGame", '')
    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    game_id = r1[0]["args"][0]["game_id"]

    for i in range(3):
        data = {"game_id": game_id, "time_left": 1}

        ws_client1.emit("classify", data, _get_image_as_stream(HARAMBE_PATH))
        ws_client2.emit("classify", data, _get_image_as_stream(HARAMBE_PATH))
        
        r1 = ws_client1.get_received()
        r2 = ws_client2.get_received()
        assert not r1[0]["args"][0]["hasWon"]
        assert not r2[0]["args"][0]["hasWon"]


def test_players_can_reach_timeout(test_clients):
    _, ws_client1, ws_client2 = test_clients
    ws_client1.emit("joinGame", '')
    ws_client2.emit("joinGame", '')
    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    game_id = r1[0]["args"][0]["game_id"]
    data = {"game_id": game_id, "time_left": 0}

    ws_client1.emit("classify", data, _get_image_as_stream(HARAMBE_PATH))
    
    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    assert r1[0]["args"][0]['round_over']
    assert r2[0]["args"][0]['round_over']


def test_end_game(test_clients):
    _, ws_client1, ws_client2 = test_clients
    ws_client1.emit("joinGame", '')
    ws_client2.emit("joinGame", '')
    r1 = ws_client1.get_received()
    r2 = ws_client2.get_received()
    player_1_id = r1[0]["args"][0]["player_id"]
    game_id = r1[0]["args"][0]["game_id"]
    data = json.dumps({"game_id": game_id, "player_id": player_1_id, "score": 100})

    ws_client1.emit('endGame', data)

    assert ws_client1.get_received() == []
    r2 = ws_client2.get_received()
    r2_json = json.loads(r2[0]["args"][0])
    assert r2_json['score'] == 100
    assert r2_json['playerId'] == player_1_id


def _get_image_as_stream(file_path):
    image_file = open(file_path, "rb")
    data_stream = image_file.read()

    tmp = tempfile.SpooledTemporaryFile()
    tmp.write(data_stream)
    tmp.seek(0)
    # Create file storage object containing the image
    content_type = "image/png"
    image = werkzeug.datastructures.FileStorage(
        stream=tmp, filename=HARAMBE_PATH, content_type=content_type
    )
    return image.stream.read()
