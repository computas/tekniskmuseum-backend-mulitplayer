"""
    Classes for describing tables in the database and additional functions for
    manipulating them.
"""
import datetime
import csv
import os
import random
from flask_sqlalchemy import SQLAlchemy
from utilities.difficulties import DifficultyId
from utilities.exceptions import UserError

db = SQLAlchemy()


class Iteration(db.Model):
    """
        Model for storing the currently used iteration of the ML model.
    """

    iteration_name = db.Column(db.String(64), primary_key=True)


class Games(db.Model):
    """
       This is the Games model in the database. It is important that the
       inserted values match the column values. player_id column value cannot
       be String when a long hex is given.
    """

    game_id = db.Column(db.NVARCHAR(32), primary_key=True)
    session_num = db.Column(db.Integer, default=1)
    labels = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    difficulty_id = db.Column(
        db.Integer, db.ForeignKey("difficulty.id"), default=1)
    players = db.relationship(
        "Players", uselist=False, back_populates="game", cascade="all, delete"
    )
    mulitplay = db.relationship(
        "MulitPlayer", uselist=False, back_populates="game",
        cascade="all, delete"
    )


class Scores(db.Model):
    """
        This is the Scores model in the database. It is important that the
        inserted values match the column values.
    """

    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.NVARCHAR(32), db.ForeignKey(
        "players.player_id", ondelete='CASCADE'))
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    difficulty_id = db.Column(
        db.Integer, db.ForeignKey("difficulty.id"), default=1)


class Players(db.Model):
    """
        Table for attributes connected to a player in the game. game_id is a
        foreign key to the game table.
    """

    player_id = db.Column(db.NVARCHAR(32), primary_key=True)
    game_id = db.Column(db.NVARCHAR(32), db.ForeignKey(
        "games.game_id"), nullable=False)
    state = db.Column(db.String(32), nullable=False)

    game = db.relationship("Games", back_populates="players")
    scores = db.relationship("Scores", backref="Players", passive_deletes=True)


class MulitPlayer(db.Model):
    """
        Table for storing players who partisipate in the same game.
    """

    game_id = db.Column(
        db.NVARCHAR(32), db.ForeignKey("games.game_id"), primary_key=True
    )
    player_1 = db.Column(db.NVARCHAR(32))
    player_2 = db.Column(db.NVARCHAR(32))
    pair_id = db.Column(db.NVARCHAR(32))

    game = db.relationship("Games", back_populates="mulitplay")


class Labels(db.Model):
    """
        This is the Labels model in the database. It is important that the
        inserted values match the column values. This tabel is used for
        - translating english labels into norwgian
        - keeping track of all possible labels
    """

    english = db.Column(db.String(32), primary_key=True)
    norwegian = db.Column(db.String(32))
    difficulty_id = db.Column(
        db.Integer, db.ForeignKey("difficulty.id"), default=1)


class User(db.Model):
    """
        This is user model in the database to store username and psw for
        administrators.
    """
    username = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(256))


class Difficulty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    difficulty = db.Column(db.String(32), nullable=False)


class ExampleImages(db.Model):
    """
        Model for storing example image urls that the model has predicted correctly.
    """
    image = db.Column(db.String(256), primary_key=True)
    label = db.Column(db.String(32), db.ForeignKey("labels.english"))


# Functions to manipulate the tables above
def create_tables(app):
    """
        The tables will be created if they do not already exist.
    """
    with app.app_context():
        db.create_all()

    return True


def insert_into_games(game_id, labels, date, difficulty_id):
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
            game = Games(
                game_id=game_id,
                labels=labels,
                date=date,
                difficulty_id=difficulty_id)
            db.session.add(game)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into games :" + str(e))
    else:
        raise UserError(
            "game_id has to be string, labels has to be string "
            "and date has to be datetime.datetime."
        )


def insert_into_scores(player_id, score, date, difficulty_id: DifficultyId):
    """
        Insert values into Scores table.

        Parameters:
        name: user name, string
        score: float
        date: datetime.date
        difficulty_id: integer: For multiplayer: 4
    """
    score_int_or_float = isinstance(score, float) or isinstance(score, int)

    if (
        isinstance(player_id, str)
        and score_int_or_float
        and isinstance(date, datetime.date)
        and isinstance(difficulty_id, int)
    ):
        try:
            scores = Scores(player_id=player_id, score=score, date=date, difficulty_id=difficulty_id)
            db.session.add(scores)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into scores: " + str(e))
    else:
        raise UserError(
            "Name has to be string, score can be int or "
            "float, difficulty_id has to be an integer and date has to be datetime.date.")


def insert_into_players(player_id, game_id, state):
    """
        Insert values into Players table.

        Parameters:
        player_id: random uuid.uuid4().hex
        game_id: random uuid.uuid4().hex
        state: string
    """
    if (
        isinstance(player_id, str)
        and isinstance(game_id, str)
        and isinstance(state, str)
    ):
        try:
            player = Players(player_id=player_id, game_id=game_id, state=state)
            db.session.add(player)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into games: " + str(e))
    else:
        raise UserError("All params has to be string.")


def insert_into_mulitplayer(game_id, player_id, pair_id):
    """
        Insert values into MulitPlayer table.

        Parameters:
        game_id: random uuid.uuid4().hex
        player_id: random uuid.uuid4().hex
        pair_id: string
    """
    pair_id_is_str_or_none = (
        isinstance(pair_id, str) or pair_id is None
    )
    if (
        isinstance(player_id, str)
        and pair_id_is_str_or_none
        and isinstance(game_id, str)
    ):
        try:
            mulitplayer = MulitPlayer(
                player_1=player_id,
                player_2=None,
                game_id=game_id,
                pair_id=pair_id)
            db.session.add(mulitplayer)
            db.session.commit()
            return True
        except Exception as e:
            raise Exception("Could not insert into mulitplayer: " + str(e))
    else:
        raise UserError("All params has to be string.")


def check_player_2_in_mulitplayer(player_id, pair_id):
    """
        Function to check if player2 is none in database. If none, a player
        can be added to the game.
    """
    # If there is no rows with player_2=None, game will be None
    game = MulitPlayer.query.filter_by(player_2=None, pair_id=pair_id).first()
    if game is not None:
        if game.player_1 == player_id:
            raise UserError("you can't join a game with yourself")
        return game.game_id

    return None


def get_game(game_id):
    """
        Return the game record with the corresponding game_id.
    """
    game = Games.query.get(game_id)
    if game is None:
        raise UserError("game_id invalid or expired")

    return game


def get_player(player_id):
    """
        Return the player record with the corresponding player_id.
    """
    player = Players.query.get(player_id)
    if player is None:
        raise UserError("player_id invalid or expired")

    return player


def get_mulitplayer(game_id):
    """
        Return the mulitplayer with the corresponding game_id.
    """
    mp = MulitPlayer.query.get(game_id)
    if mp is None:
        raise UserError("game_id invalid or expired")

    return mp


def get_opponent(game_id, player_id):
    """
        Return the player in game record with the corresponding gameID.
    """
    mp = MulitPlayer.query.get(game_id)
    if mp is None:
        # Needs to be changed to socket error
        raise UserError("Token invalid or expired")
    elif mp.player_1 == player_id:
        if mp.player_2 is not None:
            return Players.query.get(mp.player_2)
        else:
            return None
    return Players.query.get(mp.player_1)


def update_game_for_player(game_id, player_id, increase_ses_num, state):
    """
        Update game and player record for the incoming game_id and
        player_id with the given parameters.
    """
    try:
        game = Games.query.get(game_id)
        game.session_num += increase_ses_num
        new_ses_new = game.session_num
        print(new_ses_new)
        player = Players.query.get(player_id)
        player.state = state
        db.session.commit()
        return True
    except Exception as e:
        raise Exception("Could not update game for player: " + str(e))


def update_mulitplayer(player_2_id, game_id):
    """
        Update mulitplayer with player 2's id.
    """
    try:
        mp = MulitPlayer.query.get(game_id)
        player_1 = Players.query.get(mp.player_1)
        player_1.state = "Ready"
        mp.player_2 = player_2_id
        db.session.commit()
        return True
    except Exception as e:
        raise Exception("Could not update mulitplayer for player: " + str(e))


def update_iteration_name(new_name):
    """
        updates the one only iteration_name to new_name
    """
    iteration = Iteration.query.filter_by().first()
    if iteration is None:
        iteration = Iteration(iteration_name=new_name)
        db.session.add(iteration)
    else:
        iteration.iteration_name = new_name

    db.session.commit()
    return new_name


def delete_session_from_game(game_id):
    """
        To avoid unnecessary data in the database this function is called by
        the api after a session is finished. The record in games table,
        connected to the particular game_id, is deleted.
    """
    try:
        game = Games.query.get(game_id)
        db.session.query(Players).filter(
            Players.game_id == game_id
        ).delete()
        mp = MulitPlayer.query.get(game_id)
        db.session.delete(game)
        db.session.delete(mp)
        db.session.commit()
        return "Record deleted."
    except AttributeError as e:
        db.session.rollback()
        raise AttributeError("Couldn't find game_id: " + str(e))


def delete_old_games():
    """
        Delete records in games older than one day.
    """
    try:
        games = (
            db.session.query(Games)
            .filter(
                Games.date
                < (datetime.datetime.today() - datetime.timedelta(days=1))
            )
            .all()
        )
        for game in games:
            db.session.query(Players).filter(
                Players.game_id == game.game_id
            ).delete()
            db.session.query(MulitPlayer).filter(
                MulitPlayer.game_id == game.game_id
            ).delete()
            db.session.delete(game)

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception("Couldn't clean up old game records: " + str(e))


def get_daily_high_score(difficulty_id):
    """
        Function for reading all daily scores.

        Returns list of dictionaries.
    """
    try:
        today = datetime.date.today()
        # filter by today and sort by score
        top_n_list = (
            Scores.query.filter_by(date=today, difficulty_id=difficulty_id)
            .order_by(Scores.score.desc())
            .all()
        )
        # structure data
        new = [
            {"id": score.score_id, "score": score.score}
            for score in top_n_list
        ]
        return new

    except AttributeError as e:
        raise AttributeError(
            "Could not read daily highscore from database: " + str(e)
        )


def get_top_n_high_score_list(top_n, difficulty_id):
    """
        Function for reading total top n list from database.

        Parameter: top_n, number of players in top list.

        Returns list of dictionaries.
    """
    try:
        # read top n high scores
        top_n_list = (
            Scores.query.filter_by(difficulty_id=difficulty_id).order_by(
                Scores.score.desc()).limit(top_n).all()
        )
        new = [
            {"id": score.score_id, "score": score.score}
            for score in top_n_list
        ]
        return new

    except AttributeError as e:
        raise AttributeError(
            "Could not read top high score from database: " + str(e)
        )


def to_norwegian(english_label):
    """
        Reads the labels-table and return the norwegian translation of the
        english word.
    """
    try:
        query = Labels.query.get(english_label)
        return str(query.norwegian)

    except AttributeError as e:
        raise AttributeError(
            "Could not find translation in Labels table: " + str(e)
        )


def to_english(norwegian_label):
    """
        Reads the labels-table and return the english translation of the norwegian label
    """
    try:
        query = Labels.query.filter(Labels.norwegian == norwegian_label)[0]
        return str(query.english)

    except AttributeError as e:
        raise AttributeError(
            "Could not find translation in Labels table: " + str(e)
        )


def seed_labels(app, filepath):
    """
        Function for updating labels in database.
    """
    app.logger.info("seeding database")
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
        raise UserError("English and norwegian must be strings")


def get_n_labels(n, difficulty_id):
    """
        Reads all rows from database and chooses n random labels in a list.
    """
    try:
        # read all english labels in database
        labels = Labels.query.filter(
            Labels.difficulty_id <= difficulty_id).all()
        english_labels = [str(label.english) for label in labels]
        random_list = random.sample(english_labels, n)
        return random_list

    except Exception as e:
        raise Exception("Could not read Labels table: " + str(e))


def get_all_labels():
    """
        Reads all labels from database
    """
    try:
        # read all english labels in database
        labels = Labels.query.all()
        return [str(label.english) for label in labels]

    except Exception as e:
        raise Exception("Could not read Labels table: " + str(e))


def get_iteration_name():
    """
        Returns the first and only iteration name that should be in the model
    """
    iteration = Iteration.query.filter_by().first()
    assert iteration.iteration_name is not None
    return iteration.iteration_name


def get_translation_dict():
    """
        Reads all labels from database and create dictionary
    """
    try:
        labels = Labels.query.all()
        return dict(
            [(str(label.english), str(label.norwegian)) for label in labels]
        )
    except Exception as e:
        raise Exception("Could not read Labels table: " + str(e))


def insert_into_example_images(images, label):
    """
        Insert values into ExampleImages table.
    """
    if isinstance(images, list) and isinstance(label, str):
        try:
            for image in images:
                example_image = ExampleImages(image=image, label=label)
                db.session.add(example_image)
            db.session.commit()
        except Exception as e:
            raise Exception(
                "Could not insert into ExampleImages table: " + str(e))
    else:
        raise UserError("Images must be a list and label must be a string")


def get_n_random_example_images(label, number_of_images):
    """
        Returns n random example images for the given label.
    """
    try:
        example_images = ExampleImages.query.filter_by(label=label).all()
        selected_images = random.sample(
            example_images, min(
                number_of_images, len(example_images)))
        images = [image.image for image in selected_images]
        return images
    except Exception as e:
        raise Exception("Could not read ExampleImages table: " + str(e)
                        )


def populate_example_images(app):
    """
        Function for populating example images table with exported csv data. Used so you dont need to
        run the prediction job twice
    """
    with app.app_context():
        try:
            # read all rows from safe_images.csv
            with open("safe_images.csv") as csvfile:
                readCSV = csv.reader(csvfile, delimiter=",")
                for row in readCSV:
                    example_image = ExampleImages(image=row[0], label=row[1])
                    db.session.add(example_image)
                db.session.commit()
        except Exception as e:
            raise Exception(
                "Could not insert into ExampleImages table: " + str(e))
