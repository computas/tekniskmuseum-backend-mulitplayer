"""
    Functions for testing to manipulate the database. The
    functions is used on an identical test database.

    YOUR IP SHOULD BE WHITELISTED DB_SERVER ON THE AZURE PROJECT
"""
import uuid
import datetime
from pytest import raises
import sys
import os

current_directory = os.getcwd()
utilities_directory = current_directory.replace("/tests", "")
sys.path.insert(0, utilities_directory)

from utilities.difficulties import DifficultyId
from webapp import api
from webapp import models
#from utilities.exceptions import UserError

class TestValues:
    PLAYER_ID = uuid.uuid4().hex
    PLAYER_2 = uuid.uuid4().hex
    GAME_ID = uuid.uuid4().hex
    TODAY = datetime.datetime.today()
    CV_ITERATION_NAME_LENGTH = 36
    LABELS = "label1, label2, label3"
    STATE = "Ready"
    DIFFICULTY_ID = 1


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
            TestValues.GAME_ID, TestValues.LABELS, TestValues.TODAY, TestValues.DIFFICULTY_ID
        )

    assert result
