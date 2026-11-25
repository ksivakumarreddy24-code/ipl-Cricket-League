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


# E1 - Create organizer
def create_organizer(name, email, password):
    session = Session(engine)
    user_exists = session.query(User).filter_by(email=email).first()
    if user_exists is not None:
        session.close()
        return False

    new_organizer = User(name=name,email=email,password=hash_password(password),role="organizer")
    session.add(new_organizer)
    session.commit()
    response = {
        "id": new_organizer.id,
        "name": new_organizer.name,
        "email": new_organizer.email,
        "role": new_organizer.role
    }
    session.close()
    return response


# E2 - Add player
def add_player(name, country, team, role):
    session = Session(engine)
    new_player = Player(name=name,country=country,team=team,role=role)
    session.add(new_player)
    session.commit()
    response = {
        "id": new_player.id,
        "name": new_player.name,
        "country": new_player.country,
        "team": new_player.team,
        "role": new_player.role
    }
    session.close()
    return response


# E3 - Get all players
def get_all_players():
    session = Session(engine)
    players = session.query(Player).all()
    results = []
    for player in players:
        results.append({
            "id": player.id,
            "name": player.name,
            "country": player.country,
            "team": player.team,
            "role": player.role
        })
    session.close()
    return results


# E4 - Get player by ID
def get_player_by_id(player_id):
    session = Session(engine)
    player = session.query(Player).filter_by(id=player_id).first()
    if player is None:
        session.close()
        return False
    response = {
        "id": player.id,
        "name": player.name,
        "country": player.country,
        "team": player.team,
        "role": player.role
    }
    session.close()
    return response


# E5 - Create tournament
def create_tournament(name, season, start_date, end_date, user_id):
    session = Session(engine)
    new_tournament = Tournament(
        name=name,
        season=season,
        start_date=start_date,
        end_date=end_date,
        created_by=user_id
    )
    session.add(new_tournament)
    session.commit()
    response = {
        "id": new_tournament.id,
        "name": new_tournament.name,
        "season": new_tournament.season,
        "start_date": new_tournament.start_date,
        "end_date": new_tournament.end_date,
        "created_by": new_tournament.created_by
    }
    session.close()
    return response


# E6 - Get All Tournaments
def get_all_tournaments():
    session = Session(engine)
    tournaments = session.query(Tournament).all()
    response = []
    for tournament in tournaments:
        response.append({
            "id": tournament.id,
            "name": tournament.name,
            "season": tournament.season,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
            "created_by": tournament.created_by
        })
    session.close()
    return response


# E7 - Create Fantasy Teams
def create_fantasy_team(user_id, team_name):
    session = Session(engine)
    team = FantasyTeam(user_id=user_id,name=team_name)
    session.add(team)
    session.commit()
    response = {
        "id": team.id,
        "user_id": team.user_id,
        "name": team.name,
        "created_at": team.created_at
    }
    session.close()
    return response


# E8 - Adding A player
def add_player_to_team(user_id, fantasy_team_id, player_id):
    session = Session(engine)
    team = session.query(FantasyTeam).filter_by(id=fantasy_team_id,user_id=user_id).first()
    if team is None:
        session.close()
        return False
    player = session.query(Player).filter_by(id=player_id).first()
    if player is None:
        session.close()
        return False
    player_exists = session.query(FantasyTeamPlayer).filter_by(fantasy_team_id=fantasy_team_id,player_id=player_id).first()
    if player_exists is not None:
        session.close()
        return False
    total_players = session.query(FantasyTeamPlayer).filter_by(fantasy_team_id=fantasy_team_id).count()
    if total_players >= 11:
        session.close()
        return False
    fantasy_player = FantasyTeamPlayer(fantasy_team_id=fantasy_team_id,player_id=player_id)
    session.add(fantasy_player)
    session.commit()
    response = {
        "id": fantasy_player.id,
        "fantasy_team_id": fantasy_player.fantasy_team_id,
        "player_id": fantasy_player.player_id
    }
    session.close()
    return response


# E9 - Remove A player
def remove_player_from_team(user_id, fantasy_team_id, player_id):
    session = Session(engine)
    team = session.query(FantasyTeam).filter_by(id=fantasy_team_id,user_id=user_id).first()
    if team is None:
        session.close()
        return False
    fantasy_player = session.query(FantasyTeamPlayer).filter_by(fantasy_team_id=fantasy_team_id,player_id=player_id).first()
    if fantasy_player is None:
        session.close()
        return False
    session.delete(fantasy_player)
    session.commit()
    session.close()
    return True


# E10 - Get Fantasy teams
def get_user_fantasy_teams(user_id):
    session = Session(engine)
    teams = session.query(FantasyTeam).filter_by(user_id=user_id).all()
    response = []
    for team in teams:
        player_count = session.query(FantasyTeamPlayer).filter_by(fantasy_team_id=team.id).count()
        response.append({
            "id": team.id,
            "name": team.name,
            "players": player_count,
            "created_at": team.created_at
        })
    session.close()
    return response

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

# E13 - Publish player statistics
def publish_player_stats(match_id,player_id,runs,fours,sixes,wickets,catches,run_outs,stumpings):
    session = Session(engine)
    match = session.query(Match).filter_by(id=match_id).first()
    if match is None:
        session.close()
        return None
    player = session.query(Player).filter_by(id=player_id).first()
    if player is None:
        session.close()
        return None
    stat = session.query(PlayerMatchStat).filter_by(match_id=match_id,player_id=player_id).first()
    if stat is None:
        stat = PlayerMatchStat(match_id=match_id,player_id=player_id)
        session.add(stat)

    stat.runs = runs
    stat.fours = fours
    stat.sixes = sixes
    stat.wickets = wickets
    stat.catches = catches
    stat.run_outs = run_outs
    stat.stumpings = stumpings

    session.commit()

    contests = session.query(Contest).filter_by(match_id=match_id).all()
    for contest in contests:
        entries = session.query(ContestEntry).filter_by(contest_id=contest.id).all()
        for entry in entries:
            team_players = session.query(FantasyTeamPlayer).filter_by(fantasy_team_id=entry.fantasy_team_id).all()
            total_points = 0
            for item in team_players:
                player_stat = session.query(PlayerMatchStat).filter_by(match_id=match_id,player_id=item.player_id).first()
                if player_stat is not None:
                    points = (
                        player_stat.runs
                        + player_stat.fours
                        + (player_stat.sixes * 2)
                        + (player_stat.wickets * 25)
                        + (player_stat.catches * 8)
                        + (player_stat.run_outs * 12)
                        + (player_stat.stumpings * 12)
                    )
                    total_points += points
            history = session.query(FantasyPointsHistory).filter_by(contest_entry_id=entry.id,match_id=match_id).first()
            if history is None:
                history = FantasyPointsHistory(contest_entry_id=entry.id,match_id=match_id,points=total_points)
                session.add(history)
            else:
                 history.points = total_points #type: ignore
    session.commit()
    response = {
        "message": "Player statistics published successfully",
        "match_id": match_id,
        "player_id": player_id
    }
    session.close()
    return response

# E14 - Get contest leaderboard
def get_leaderboard(contest_id):
    session = Session(engine)
    contest = session.query(Contest).filter_by(id=contest_id).first()
    if contest is None:
        session.close()
        return False
    entries = session.query(ContestEntry).filter_by(contest_id=contest_id).all()
    results = []
    for entry in entries:
        history = session.query(FantasyPointsHistory).filter_by(contest_entry_id=entry.id).all()
        total_points = 0
        for item in history:
            total_points += item.points
        team = session.query(FantasyTeam).filter_by(id=entry.fantasy_team_id).first()
        if team is not None:
            team_name = team.name
        else:
            team_name = "Unknown"
        results.append({
            "fantasy_team_id": entry.fantasy_team_id,
            "team_name": team_name,
            "points": total_points
        })

    def get_points(item):
        return item["points"]

    results.sort(key=get_points, reverse=True)
    for i in range(len(results)):
        results[i]["rank"] = i + 1

    session.close()
    return results

# E15 - Get fantasy points history
def get_fantasy_points_history(user_id):
    session = Session(engine)
    teams = session.query(FantasyTeam).filter_by(user_id=user_id).all()
    results = []
    for team in teams:
        entries = session.query(ContestEntry).filter_by(fantasy_team_id=team.id).all()
        for entry in entries:
            history_records = session.query(FantasyPointsHistory).filter_by(contest_entry_id=entry.id).all()
            contest = session.query(Contest).filter_by(id=entry.contest_id).first()
            if contest is not None:
                contest_name = contest.name
            else:
                contest_name = "Unknown"
            for history in history_records:
                results.append({
                    "fantasy_team_id": team.id,
                    "team_name": team.name,
                    "contest_id": entry.contest_id,
                    "contest_name": contest_name,
                    "match_id": history.match_id,
                    "points": history.points,
                    "created_at": history.created_at
                })
    session.close()
    return results

# E16 - Create Matches
def create_match(tournament_id, team1, team2, match_date):
    session = Session(engine)
    tournament = session.query(Tournament).filter_by(id=tournament_id).first()
    if tournament is None:
        session.close()
        return False
    if team1 == team2:
        session.close()
        return False
    new_match = Match(tournament_id=tournament_id,team1=team1,team2=team2,match_date=match_date)
    session.add(new_match)
    session.commit()
    response = {
        "id": new_match.id,
        "tournament_id": new_match.tournament_id,
        "team1": new_match.team1,
        "team2": new_match.team2,
        "match_date": new_match.match_date,
        "status": new_match.status
    }
    session.close()
    return response

# E17 - get all matches
def get_all_matches():
    session = Session(engine)
    matches = session.query(Match).all()
    response = []
    for match in matches:
        response.append({
            "id": match.id,
            "tournament_id": match.tournament_id,
            "team1": match.team1,
            "team2": match.team2,
            "match_date": match.match_date,
            "status": match.status
        })
    session.close()
    return response

