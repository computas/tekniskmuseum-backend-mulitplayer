"""
    Classes for describing tables in the database and additional functions for
    manipulating them.
"""

import datetime
import csv
import os
import random
from flask_sqlalchemy import SQLAlchemy
from werkzeug import exceptions as excp

db = SQLAlchemy()


class Iteration(db.Model):
    """
        Model for storing the currently used iteration of the ML model.
    """
    iteration_name = db.Column(db.String(64), primary_key=True)


class Games(db.Model):
    """
       This is the Games model in the database. It is important that the
       inserted values match the column values. Token column value cannot
       be String when a long hex is given.
    """
    game_id = db.Column(db.NVARCHAR(32), primary_key=True)
    session_num = db.Column(db.Integer, default=1)
    labels = db.Column(db.String(64))
    date = db.Column(db.DateTime)


class Scores(db.Model):
    """
        This is the Scores model in the database. It is important that the
        inserted values match the column values.
    """
    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)


class PlayerInGame(db.Model):
    """
        Table for attributes connected to a player in the game. game_id is a
        foreign key to the game table.
    """
    token = db.Column(db.NVARCHAR(32), primary_key=True)
    game_id = db.Column(db.NVARCHAR(32), primary_key=True, nullable=False)
    state = db.Column(db.String(32), nullable=False)


class MulitPlayer(db.Model):
    """
        Table for storing players who partisipate in the same game.
    """
    game_id = db.Column(db.NVARCHAR(32), primary_key=True)
    player_1 = db.Column(db.NVARCHAR(32))
    player_2 = db.Column(db.NVARCHAR(32))


class Labels(db.Model):
    """
        This is the Labels model in the database. It is important that the
        inserted values match the column values. This tabel is used for
        - translating english labels into norwgian
        - keeping track of all possible labels
    """
    english = db.Column(db.String(32), primary_key=True)
    norwegian = db.Column(db.String(32))


# Functions to manipulate the tables above
def create_tables(app):
    """
        The tables will be created if they do not already exist.
    """
    with app.app_context():
        db.create_all()

    return True


def insert_into_games(game_id, labels, date):
    """
        Insert values into Games table.

        Parameters:
        game_id : random uuid.uuid4().hex
        labels: list of labels
        date: datetime.datetime
    """
    if (
        isinstance(game_id, str)
        and isinstance(labels, str)
        and isinstance(date, datetime.datetime)
    ):

        try:
            game = Games(game_id=game_id, labels=labels, date=date)
            db.session.add(game)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into games :" + str(e))
    else:
        raise excp.BadRequest(
            "game_id has to be string, labels has to be string "
            "and date has to be datetime.datetime."
        )


def insert_into_scores(name, score, date):
    """
        Insert values into Scores table.

        Parameters:
        name: user name, string
        score: float
        date: datetime.date
    """
    score_int_or_float = isinstance(score, float) or isinstance(score, int)

    if (
        isinstance(name, str)
        and score_int_or_float
        and isinstance(date, datetime.date)
    ):
        try:
            score = Scores(name=name, score=score, date=date)
            db.session.add(score)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into scores: " + str(e))
    else:
        raise excp.BadRequest(
            "Name has to be string, score can be int or "
            "float and date has to be datetime.date."
        )


def insert_into_player_in_game(token, game_id, state):
    """
        Insert values into PlayerInGame table.

        Parameters:
        token: random uuid.uuid4().hex
        game_id: random uuid.uuid4().hex
        state: string
    """
    if (
        isinstance(token, str)
        and isinstance(game_id, str)
        and isinstance(state, str)
    ):
        try:
            player_in_game = PlayerInGame(
                token=token, game_id=game_id, state=state
            )
            db.session.add(player_in_game)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into games: " + str(e))
    else:
        raise excp.BadRequest(
            "All params has to be string."
        )


def insert_into_mulitplayer(player_1, player_2, game_id):
    """
        Docstring.
    """
    player2_is_str_or_none = isinstance(player_2, str) or player_2 is None
    if (
        isinstance(player_1, str)
        and player2_is_str_or_none
        and isinstance(game_id, str)
    ):
        try:
            mulitplayer = MulitPlayer(
                player_1=player_1, player_2=player_2, game_id=game_id
            )
            db.session.add(mulitplayer)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into mulitplayer: " + str(e))
    else:
        raise excp.BadRequest(
            "All params has to be string."
        )


def check_player2_in_mulitplayer(player_id):
    """
        Function to check if player2 is none in database. If none, a player
        can be added to the game.
    """
    # If there is no rows with player_2=None, game will be None
    game = MulitPlayer.query.filter_by(player_2=None).first()
    if game is not None:
        if game.player_1 == player_id:
            raise excp.BadRequest("you can't join a game with yourself")
        return game.game_id

    return None


def get_record_from_game(game_id):
    """
        Return the game record with the corresponding game_id.
    """
    game = Games.query.get(game_id)
    if game is None:
        raise excp.BadRequest("game_id invalid or expired")

    return game


def get_record_from_player_in_game(token):
    """
        Return the player in game record with the corresponding token.
    """
    player_in_game = PlayerInGame.query.get(token)
    if player_in_game is None:
        raise excp.BadRequest("Token invalid or expired")

    return player_in_game


def get_record_from_player_in_game_by_game_id(game_id, player_id):
    """
        Return the player in game record with the corresponding token.
    """
    mp = MulitPlayer.query.filter_by(game_id=game_id).first()

    if player_in_game is None:
        raise excp.BadRequest("Token invalid or expired")
    elif mp.player_1 == player_id:
        player_in_game = PlayerInGame.query.get(mp.player_2)
    elif mp.player_2 == player_id:
        player_in_game = PlayerInGame.query.get(mp.player_1)
    return player_in_game


def update_game_for_player(game_id, token, session_num, state):
    """
        Update game and player_in_game record for the incomming game_id and
        token with the given parameters.
    """
    try:
        game = Games.query.get(game_id)
        game.session_num += 1
        player_in_game = PlayerInGame.query.get(token)
        player_in_game.state = state
        db.session.commit()
        return True
    except Exception as e:
        raise Exception("Could not update game for player: " + str(e))


def update_mulitplayer(player2_id, game_id):
    """
        Update mulitplayer with player 2's id.
    """
    try:
        mp = MulitPlayer.query.filter_by(game_id=game_id).first()
        player_1 = PlayerInGame.query.filter_by(token=mp.player_1).first()
        player_1.game_state = "Ready"
        mp.player_2 = player2_id
        db.session.commit()
        return True
    except Exception as e:
        raise Exception("Could not update mulitplayer for player: " + str(e))


def delete_session_from_game(game_id):
    """
        To avoid unecessary data in the database this function is called by
        the api after a session is finished. The record in games table,
        connected to the particular game_id, is deleted.
    """
    try:
        game = Games.query.get(game_id)
        db.session.query(PlayerInGame).filter(
            PlayerInGame.game_id == game_id
        ).delete()
        db.session.delete(game)
        db.session.commit()
        return "Record deleted."
    except AttributeError as e:
        db.session.rollback()
        raise AttributeError("Couldn't find game_id: " + str(e))


def delete_old_games():
    """
        Delete records in games older than one hour.
    """
    try:
        games = (
            db.session.query(Games)
            .filter(
                Games.date
                < (datetime.datetime.today() - datetime.timedelta(hours=1))
            )
            .all()
        )
        for game in games:
            db.session.query(PlayerInGame).filter(
                PlayerInGame.game_id == game.game_id
            ).delete()
            db.session.delete(game)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Couldn't clean up old game records: " + str(e))


def seed_labels(app, filepath):
    """
        Function for updating labels in database.
    """
    with app.app_context():
        if os.path.exists(filepath):
            with open(filepath) as csvfile:
                try:
                    readCSV = csv.reader(csvfile, delimiter=",")
                    for row in readCSV:
                        # Insert label into Labels table if not present
                        if Labels.query.get(row[0]) is None:
                            insert_into_labels(row[0], row[1])
                except AttributeError as e:
                    raise AttributeError(
                        "Could not insert into Labels table: " + str(e)
                    )
        else:
            raise AttributeError("File path not found")


def insert_into_labels(english, norwegian):
    """
        Insert values into Scores table.
    """
    if isinstance(english, str) and isinstance(norwegian, str):
        try:
            label_row = Labels(english=english, norwegian=norwegian)
            db.session.add(label_row)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into Labels table: " + str(e))
    else:
        raise excp.BadRequest("English and norwegian must be strings")


def get_n_labels(n):
    """
        Reads all rows from database and chooses 3 random labels in a list
    """
    try:
        # read all english labels in database
        labels = Labels.query.all()
        english_labels = [str(label.english) for label in labels]
        random_list = random.sample(english_labels, n)
        return random_list

    except Exception as e:
        raise Exception("Could not read Labels table: " + str(e))
