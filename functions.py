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

# E11 - Create contest
def create_contest(match_id, name, entry_fee, max_entries, user_id):
    session = Session(engine)
    match = session.query(Match).filter_by(id=match_id).first()
    if match is None:
        session.close()
        return None

    new_contest = Contest(match_id=match_id,name=name,entry_fee=entry_fee,max_entries=max_entries,created_by=user_id)
    session.add(new_contest)
    session.commit()
    response = {
        "id": new_contest.id,
        "match_id": new_contest.match_id,
        "name": new_contest.name,
        "entry_fee": new_contest.entry_fee,
        "max_entries": new_contest.max_entries,
        "created_by": new_contest.created_by}

    session.close()
    return response

# E12 - Join contest
def join_contest(contest_id, fantasy_team_id, user_id):
    session = Session(engine)
    contest = session.query(Contest).filter_by(id=contest_id).first()
    if contest is None:
        session.close()
        return None
    team = session.query(FantasyTeam).filter_by(id=fantasy_team_id,user_id=user_id).first()
    if team is None:
        session.close()
        return None
    existing_entry = session.query(ContestEntry).filter_by(contest_id=contest_id,fantasy_team_id=fantasy_team_id).first()
    if existing_entry is not None:
        session.close()
        return "already_joined"
    entry_count = session.query(ContestEntry).filter_by(contest_id=contest_id).count()
    if entry_count >= int(contest.maxentries):
        session.close()
        return "contest_full"

    new_entry = ContestEntry(contest_id=contest_id,fantasy_team_id=fantasy_team_id)
    session.add(new_entry)
    session.commit()
    response = {
        "id": new_entry.id,
        "contest_id": new_entry.contest_id,
        "fantasy_team_id": new_entry.fantasy_team_id,
        "joined_at": new_entry.joined_at
    }
    session.close()
    return response