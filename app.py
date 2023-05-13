import os
import requests
from flask import Flask, render_template, request, flash, url_for, redirect, session, g, abort, jsonify

from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, UserEditForm, LoginForm
from models import db, connect_db, User, Player, Roster, News
from ignore import playerInfo, playerFantasyProjections, news_info, rookies


CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///ffwebsite'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
debug = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        add_user_to_g()
        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            add_user_to_g()
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")

########### Homepage and Error page ###########


@app.route('/')
def homepage():
    """Show homepage with most recent news stories"""
    news = News.query.all()
    player = Player.query.all()
    user = g.user
    return render_template('home.html', news=news, player=player, user=user)


@app.route('/user/edit', methods=["GET", "POST"])
def user_edit():
    """Show user edit page"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data

            db.session.commit()
            return redirect("/")

        flash("Wrong password, please try again.", 'danger')

    return render_template('edit.html', form=form, user_id=user.id)


@app.route('/user/<int:user_id>/roster')
def user_roster(user_id):
    """Show user created roster"""

    if not g.user:
        flash('Access Unauthorized', 'danger')
        return redirect('/')
    user = User.query.get_or_404(user_id)
    players = user.roster

    return render_template("roster.html", user=user, players=players)


@app.route('/user/roster/<int:player_id>', methods=['POST'])
def add_player_to_roster(player_id):
    """Add player to User Roster"""
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    player = Player.query.get(player_id)
    g.user.roster.append(player)
    db.session.commit()

    return redirect(url_for('user_roster'))


@app.route('/remove_player_from_roster/<int:player_id>')
def remove_player_from_roster(player_id):
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    user = g.user
    player = Player.query.get(player_id)
    user.roster.remove(player)
    db.session.commit()
    return redirect(url_for('user_roster', user=user))


@app.route('/player_search', methods=["Get"])
def player_search():
    name = request.args.get('name')
    players = Player.query.filter(Player.name.ilike(f'%{name}%')).all()
    return render_template('player_info.html', players=players)


@app.route('/player/<int:id>')
def show_player(id):
    """Show player info"""

    player = Player.query.get_or_404(id)
    user = g.user
    return render_template('player.html', player=player, user=user)


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


def fetch_and_store_players():
    with app.app_context():
        res = requests.get(playerInfo)
        player_data = res.json()
        players = []
        offense = ['TE', 'WR', 'QB', 'K', 'RB']
        for player in player_data:
            if player['Position'] in offense:
                playerID = player['PlayerID']
                name = player['Name']
                position = player['Position']
                team = player['Team']
                byeweek = player['ByeWeek']
                age = player['Age']
                number = player['Number']
                birthday = player['BirthDateString']
                experience = player['ExperienceString']
                height = player['Height']
                weight = player['Weight']
                photo = player['PhotoUrl']
                teamID = player['TeamID']
                yahoo = player['YahooPlayerID']
                opponent = player['UpcomingGameOpponent']
                status = player['Status']

                player_obj = Player(
                    playerID=playerID,
                    name=name,
                    position=position,
                    team=team,
                    byeweek=byeweek,
                    age=age,
                    number=number,
                    birthday=birthday,
                    experience=experience,
                    height=height,
                    weight=weight,
                    photo=photo,
                    teamID=teamID,
                    yahoo=yahoo,
                    opponent=opponent,
                    status=status)
                players.append(player_obj)

        db.session.add_all(players)
        db.session.commit()


def get_rookies():
    with app.app_context():
        res = requests.get(rookies)
        rookie_data = res.json()
        players = []
        offense = ['TE', 'WR', 'QB', 'K', 'RB']
        for player in rookie_data:
            if player['Position'] in offense:
                playerID = player['PlayerID']
                name = player['Name']
                position = player['Position']
                team = player['Team']
                byeweek = player['ByeWeek']
                age = player['Age']
                number = player['Number']
                birthday = player['BirthDateString']
                experience = player['ExperienceString']
                height = player['Height']
                weight = player['Weight']
                photo = player['PhotoUrl']
                teamID = player['TeamID']
                yahoo = player['YahooPlayerID']
                opponent = player['UpcomingGameOpponent']
                status = player['Status']

                player_obj = Player(
                    playerID=playerID,
                    name=name,
                    position=position,
                    team=team,
                    byeweek=byeweek,
                    age=age,
                    number=number,
                    birthday=birthday,
                    experience=experience,
                    height=height,
                    weight=weight,
                    photo=photo,
                    teamID=teamID,
                    yahoo=yahoo,
                    opponent=opponent,
                    status=status)
                players.append(player_obj)

        db.session.add_all(players)
        db.session.commit()


def update_players():
    with app.app_context():
        res = requests.get(playerFantasyProjections)
        player_data = res.json()
        for player in player_data:
            playerID = player['PlayerID']
            existing_player = Player.query.filter_by(playerID=playerID).first()
            if existing_player:
                existing_player.adp = player['AverageDraftPosition']
                existing_player.adpRookie = player['AverageDraftPositionRookie']
                existing_player.adpPPR = player['AverageDraftPositionPPR']
                existing_player.adpDynasty = player['AverageDraftPositionDynasty']
                existing_player.adp2QB = player['AverageDraftPosition2QB']
                existing_player.projFantasyPoints = player['FantasyPoints']
                existing_player.projFantasyPointsPPR = player['FantasyPointsPPR']
                db.session.add(existing_player)
                db.session.commit()


def get_news():
    with app.app_context():
        res = requests.get(news_info)
        news_data = res.json()
        news = []
        for article in news_data:
            newsID = article['NewsID']
            source = article['Source']
            time_ago = article['TimeAgo']
            url = article['Url']
            title = article['Title']
            content = article['Content']
            team = article['Team']
            teamID = article['TeamID']
            categories = article['Categories']
            original_source = article['OriginalSource']

            news_obj = News(
                newsID=newsID,
                source=source,
                time_ago=time_ago,
                url=url,
                title=title,
                content=content,
                team=team,
                teamID=teamID,
                categories=categories,
                original_source=original_source)
            news.append(news_obj)

        db.session.add_all(news)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        fetch_and_store_players()
        get_rookies()
        update_players()
        get_news()
