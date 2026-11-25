import os
from datetime import datetime, timedelta,timezone
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine #pyright: ignore
from sqlalchemy.orm import Session, declarative_base #pyright: ignore
import jwt #pyright: ignore
from argon2 import PasswordHasher #pyright: ignore
from argon2.exceptions import VerifyMismatchError #pyright: ignore

ph = PasswordHasher()

DB_URL = os.getenv("DB_URL", "sqlite:///./iplleague.db")
engine = create_engine(DB_URL)
Base = declarative_base()

ACCESS_TOKEN_EXPIRY = 15  # minutes
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60  # minutes

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

# tables

# 1.users table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 2.players table
class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    team = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 3.Tournaments table
class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    season = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))

# 4. Matches table
class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    team1 = Column(String, nullable=False)
    team2 = Column(String, nullable=False)
    match_date = Column(DateTime, nullable=False)
    status = Column(String, default="upcoming")

# 5. Fantasy teams table
class FantasyTeam(Base):
    __tablename__ = "fantasy_teams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 6. Fantasy team players table
class FantasyTeamPlayer(Base):
    __tablename__ = "fantasy_team_players"
    id = Column(Integer, primary_key=True, index=True)
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))

# 7. Contests table
class Contest(Base):
    __tablename__ = "contests"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    name = Column(String, nullable=False)
    entry_fee = Column(Integer, default=0)
    max_entries = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))

# 8. Contest entries table
class ContestEntry(Base):
    __tablename__ = "contest_entries"
    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"))
    fantasy_team_id = Column(Integer, ForeignKey("fantasy_teams.id"))
    joined_at = Column(DateTime, default=datetime.now)

# 9. Player match statistics table
class PlayerMatchStat(Base):
    __tablename__ = "player_match_stats"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    runs = Column(Integer, default=0)
    fours = Column(Integer, default=0)
    sixes = Column(Integer, default=0)
    wickets = Column(Integer, default=0)
    catches = Column(Integer, default=0)
    run_outs = Column(Integer, default=0)
    stumpings = Column(Integer, default=0)

# 10. Fantasy points history table
class FantasyPointsHistory(Base):
    __tablename__ = "fantasy_points_history"
    id = Column(Integer, primary_key=True, index=True)
    contest_entry_id = Column(Integer, ForeignKey("contest_entries.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)


# Register user
# Hash a password before storing it.
def hash_password(password):
    return ph.hash(password)


def verify_password(password, hashed_password):
    try:
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False


# Register user
def register_user(username, email, password):

    session = Session(engine)

    user_exists = session.query(User).filter_by(email=email).first()

    if user_exists is not None:
        session.close()
        return False

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role="user"
    )

    session.add(new_user)
    session.commit()

    response = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

    session.close()
    return response

# Create a signed access or refresh token.
def create_token(user_id, token_type):
    expiry_minutes = (
        ACCESS_TOKEN_EXPIRY if token_type == "access" else REFRESH_TOKEN_EXPIRY
    )
    payload = {
        "user_id": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Verify login
def verify_login(email, password):

    session = Session(engine)

    user = session.query(User).filter_by(email=email).first()

    if user is None:
        session.close()
        return False

    if verify_password(password, user.hashed_password) is False:
        session.close()
        return False

    user_id = user.id
    session.close()

    access_token = create_token(user_id, "access")
    refresh_token = create_token(user_id, "refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# E1 - Create an organizer account
def create_organizer_account(username, email, password):
    session = Session(engine)
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user is not None:
        session.close()
        return False
    existing_username = session.query(User).filter_by(username=username).first()
    if existing_username is not None:
        session.close()
        return False
    new_user = User(username=username,email=email,password=ph.hash(password),role="organizer")
    session.add(new_user)
    session.commit()

    response = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }
    session.close()
    return response


# E2 - Add a cricket player to the platform
def add_cricket_player(name, team, role):
    session = Session(engine)
    new_player = Player(name=name,team=team,role=role)
    session.add(new_player)
    session.commit()
    response = {
        "id": new_player.id,
        "name": new_player.name,
        "team": new_player.team,
        "role": new_player.role
    }

    session.close()
    return response


# E3 - Get all available cricket players
def get_all_cricket_players():
    session = Session(engine)
    players = session.query(Player).all()
    results = []
    for player in players:
        results.append({
            "id": player.id,
            "name": player.name,
            "team": player.team,
            "role": player.role
        })
    session.close()
    return results


# E4 - Get details of a particular player
def get_player_details(player_id):
    session = Session(engine)
    player = session.query(Player).filter_by(id=player_id).first()
    if player is None:
        session.close()
        return None
    response = {
        "id": player.id,
        "name": player.name,
        "team": player.team,
        "role": player.role
    }
    session.close()
    return response


# E5 - Create a cricket tournament
def create_tournament(name, start_date, end_date):
    session = Session(engine)
    new_tournament = Tournament(name=name,start_date=start_date,end_date=end_date,status="Upcoming")
    session.add(new_tournament)
    session.commit()
    response = {
        "id": new_tournament.id,
        "name": new_tournament.name,
        "start_date": new_tournament.start_date,
        "end_date": new_tournament.end_date,
        "status": new_tournament.status
    }
    session.close()
    return response


# Get user role
def get_user_role(user_id):
    session = Session(engine)
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        session.close()
        return None
    role = user.role
    session.close()
    return role


