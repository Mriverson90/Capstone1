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
        autoincrement=True,
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

    roster = db.relationship('Roster', backref='user')

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


class Player(db.Model):
    """Player model to pull info from api and save to database"""

    __tablename__ = 'players'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    playerID = db.Column(
        db.Integer,
        nullable=False,
    )

    name = db.Column(
        db.String(50),
        nullable=False,
    )

    position = db.Column(
        db.String(5),
        nullable=False
    )

    team = db.Column(
        db.String(120)
    )

    byeweek = db.Column(
        db.Integer,
    )

    projFantasyPoints = db.Column(
        db.Integer,
    )

    projFantasyPointsPPR = db.Column(
        db.Integer,
    )

    adp = db.Column(
        db.Integer,
    )

    adpRookie = db.Column(
        db.Integer,
    )

    adpPPR = db.Column(
        db.Integer,
    )

    adpDynasty = db.Column(
        db.Integer,
    )

    adp2QB = db.Column(
        db.Integer,
    )

    age = db.Column(
        db.Integer,
    )

    number = db.Column(
        db.Integer
    )

    birthday = db.Column(
        db.String(50),
    )

    experience = db.Column(
        db.String(120),
    )

    height = db.Column(
        db.String(120),
    )

    weight = db.Column(
        db.Integer,
    )

    photo = db.Column(
        db.Text
    )

    teamID = db.Column(
        db.Integer
    )

    yahoo = db.Column(
        db.Integer,
    )

    opponent = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(120),
    )
    
    rosters = db.relationship('Roster', secondary='roster_player', backref='players')

class Roster(db.Model):
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

    players = db.relationship('Player'),

    def __repr__(self):
        return f"<Roster #{self.id} for User #{self.user_id}>"


class News(db.Model):
    """News Stories"""
    __tablename__ = 'news'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    source = db.Column(
        db.String,
    )

    newsID = db.Column(
        db.Integer,
    )

    time_ago = db.Column(
        db.String,
    )

    url = db.Column(
        db.String,
    )

    title = db.Column(
        db.String,
    )

    content = db.Column(
        db.Text,
    )

    team = db.Column(
        db.String,
    )

    categories = db.Column(
        db.String,
    )
    teamID = db.Column(
        db.Integer,
    )

    original_source = db.Column(
        db.String,
    )


def connect_db(app):
    """Connect this database to Flask app"""

    db.app = app
    db.init_app(app)
