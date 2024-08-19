"""
    Testfunctions for testing functions to manipulate the database. The
    functions is used on an identical test database.

    YOUR IP SHOULD BE WHITELISTED DB_SERVER ON THE AZURE PROJECT
"""
import uuid
import datetime
from pytest import raises
import sys
import os

#current_directory = os.getcwd()
utilities_directory = sys.path[0].replace("/test", "")
sys.path.insert(0, utilities_directory)

from utilities.difficulties import DifficultyId
from webapp import api
from webapp import models
from utilities.exceptions import UserError

class TestValues:
    PLAYER_ID = uuid.uuid4().hex
    PLAYER_2 = uuid.uuid4().hex
    GAME_ID = uuid.uuid4().hex
    TODAY = datetime.datetime.today()
    CV_ITERATION_NAME_LENGTH = 36
    LABELS = "label1, label2, label3"
    STATE = "Ready"


def test_create_tables():
    """
        Check that the tables exists.
    """
    result = models.create_tables(api.app)
    assert result


def test_insert_into_games():
    """
        Check that records exists in Games table after inserting.
    """
    with api.app.app_context():
        result = models.insert_into_games(
            TestValues.GAME_ID, TestValues.LABELS, TestValues.TODAY, DifficultyId.Easy
        )

    assert result

def test_insert_into_players():
    """
        Check that record exists in Players table after inserting.
    """
    with api.app.app_context():
        result = models.insert_into_players(
            TestValues.PLAYER_ID, TestValues.GAME_ID, TestValues.STATE
        )

    assert result


def test_insert_into_scores():
    """
        Check that records exists in Scores table after inserting.
    """
    with api.app.app_context():

       #models.insert_into_players(TestValues.PLAYER_ID, TestValues.GAME_ID, TestValues.STATE)
       
        result = models.insert_into_scores(
            TestValues.PLAYER_ID, 500, TestValues.TODAY, DifficultyId.Easy)

    assert result

def test_insert_into_multiplayer():
    """
        Check that record exists in MultiPlayer after inserting.
    """
    with api.app.app_context():
        result = models.insert_into_mulitplayer(
            TestValues.GAME_ID, TestValues.PLAYER_ID, TestValues.PLAYER_2
        )

    assert result


def test_illegal_parameter_games():
    """
        Check that exception is raised when illegal arguments is passed
        into games table.
    """
    with raises(UserError):
        models.insert_into_games(
            10, ["label1", "label2", "label3"], "date_time", DifficultyId.Easy
        )


def test_illegal_parameter_scores():
    """
        Check that exception is raised when illegal arguments is passed
        into scores table.
    """
    with raises(UserError):
        models.insert_into_scores(
            100, "score", "01.01.2020", DifficultyId.Medium)


def test_illegal_parameter_labels():
    """
        Check that exception is raised when illegal arguments is passed
        into games table.
    """
    with raises(UserError):
        models.insert_into_labels(1, None)


def test_illegal_parameter_players():
    """
        Check that exception is raised when illegal arguments is passed
        into player in game table.
    """
    with raises(UserError):
        models.insert_into_players(100, 200, 11)


def test_illegal_parameter_mulitplayer():
    """
        Check that exception is raised when illegal arguments is passed
        into player in MulitPlayer table.
    """
    with raises(UserError):
        models.insert_into_mulitplayer(100, 200, 11)


def test_query_equals_insert_games():
    """
        Check that inserted record is the same as record catched by query.
    """
    with api.app.app_context():
        result = models.get_game(TestValues.GAME_ID)

    assert result.labels == TestValues.LABELS
    # Datetime assertion can't be done due to millisec differents


def test_query_equals_insert_players():
    """
        Check that inserted record is the same as record catched by query.
    """
    with api.app.app_context():
        result = models.get_player(TestValues.PLAYER_ID)

    assert result.game_id == TestValues.GAME_ID
    assert result.state == TestValues.STATE


def test_delete_session_from_game():
    """
        Adds player to game, players and mulitplayer. Then deletes and checks if success.
    """
    game_id = uuid.uuid4().hex
    player_id = uuid.uuid4().hex
    with api.app.app_context():
        models.insert_into_games(game_id, TestValues.LABELS, TestValues.TODAY, DifficultyId.Medium)
        models.insert_into_players(player_id, game_id, "Waiting")
        models.insert_into_mulitplayer(game_id, player_id, None)
        result = models.delete_session_from_game(game_id)
    assert result == "Record deleted."


def test_get_iteration_name_is_string():
    """
        Tests if it's possible to get an iteration name from the database and the type is str
    """
    with api.app.app_context():
        iteration_name = models.get_iteration_name()

    assert isinstance(iteration_name, str)


def test_get_n_labels_correct_size():
    """
        Test that get_n_labels return lists of correct sizes
    """
    with api.app.app_context():
        for i in range(5):
            result = models.get_n_labels(i, DifficultyId.Hard)
            assert len(result) == i


def test_get_n_labels_bad_reqeust():
    """
        Test that get_n_labels raises exeption if n is larger than number of labels
    """
    with raises(Exception):
        models.get_n_labels(10000)


def test_to_norwegian_correct_translation():
    """
        Test that to_norwegian translates words correctly
    """
    english_words = ["mermaid", "axe", "airplane"]
    norwegian_words = ["havfrue", "øks", "fly"]

    with api.app.app_context():
        for i in range(0, len(english_words)):
            translation = models.to_norwegian(english_words[i])
            print(translation)
            assert translation == norwegian_words[i]


def test_to_norwegian_illegal_parameter():
    """
        Test that to_norwegian raises exception if input word is not found
    """
    with raises(Exception):
        models.to_norwegian("this word is not in the database")


def test_get_iteration_name_length():
    """
        Test if the result returned has specified length
    """
    with api.app.app_context():
        iteration_name = models.get_iteration_name()

    assert len(iteration_name) > 0
