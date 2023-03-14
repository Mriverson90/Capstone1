"""SQLAlchemy Models for Capstone1"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

"""User model"""


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    roster = db.relationship('rosters')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Players(db.Model):
    """Player model to pull info from api and save to database"""

    __tablename__ = 'players'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    playerID = db.Column(
        db.Integer,
        nullable=False
    )

    name = db.Column(
        db.String(50),
        nullable=False,
    )

    age = db.Column(
        db.Integer,
        nullable=False
    )

    position = db.Column(
        db.String(5),
        nullable=False
    )

    number = db.Column(
        db.Integer,
        nullable=False
    )

    adp = db.Column(
        db.Integer,
        nullable=False
    )

    birthday = db.Column(
        db.String(50),
        nullable=False
    )

    byeweek = db.Column(
        db.Integer,
        nullable=False
    )

    draftyear = db.Column(
        db.Integer,
    )

    draftpick = db.Column(
        db.Integer,
    )

    depthOrder = db.Column(
        db.Integer,
    )

    team = db.Column(
        db.String(120)
    )

    inactive = db.Column(
        db.Boolean,
        nullable=False
    )

    experience = db.Column(
        db.String(120),
        nullable=False
    )

    height = db.Column(
        db.String(120),
        nullable=False
    )

    weight = db.Column(
        db.Integer,
        nullable=False
    )

    news = db.Column(
        db.Text
    )

    photo = db.Column(
        db.Text
    )

    yahoo = db.Column(
        db.Integer,
        nullable=False
    )

    teamID = db.Column(
        db.Integer
    )

    opponent = db.Column(
        db.Text
    )

    active = db.Column(
        db.Boolean,
        nullable=False
    )

    status = db.Column(
        db.String(12),
        nullable=False
    )


class Rosters(db.Model):
    """User created Roster"""

    __tablename__ = 'rosters'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False
    )

    player = db.Column(
        db.Integer,
        db.ForeignKey('players.id')
    )


def connect_db(app):
    """Connect this database to Flask app"""

    db.app = app
    db.init_app(app)
