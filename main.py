
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import functions

app = FastAPI()

# Allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request models


class OrganizerRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class PlayerRequest(BaseModel):
    name: str
    country: str
    team: str
    role: str


class TournamentRequest(BaseModel):
    name: str
    season: str
    start_date: datetime
    end_date: datetime


class FantasyTeamData(BaseModel):
    team_name: str = Field(min_length=1)

class AddPlayerData(BaseModel):
    fantasy_team_id: int
    player_id: int

class RemovePlayerData(BaseModel):
    fantasy_team_id: int
    player_id: int

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ContestRequest(BaseModel):
    match_id: int
    name: str
    entry_fee: float
    max_entries: int


class JoinContestRequest(BaseModel):
    fantasy_team_id: int


class PlayerStatsRequest(BaseModel):
    player_id: int
    runs: int
    fours: int
    sixes: int
    wickets: int
    catches: int
    run_outs: int
    stumpings: int


class MatchRequest(BaseModel):
    tournament_id: int
    team1: str
    team2: str
    match_date: datetime



def verify_token(token: str, token_type: str):
    verifier = getattr(functions, "verify_token", None)
    if not callable(verifier):
        raise HTTPException(status_code=500, detail="Token verification is unavailable")
    return verifier(token, token_type)


# Get logged-in user's ID
def get_current_user(token: str):
    if not token:
        raise HTTPException(status_code=401,detail="Authentication required")
    user_id = verify_token(token, "access")
    if user_id is False:
        raise HTTPException(status_code=401,detail="Invalid or expired access token")
    return user_id


def check_role(token: str, allowed_roles: list):
    user_id = get_current_user(token)
    role = functions.get_user_role(user_id)
    if role is False:
        raise HTTPException(status_code=401,detail="User not found")
    if role not in allowed_roles:
        raise HTTPException(status_code=403,detail="forbidden")
    return user_id



@app.get("/")
def home():
    return {"message": "IPL Fantasy Cricket League API is running"}


# A1 - Register user
@app.post("/auth/register", status_code=201)
def register(data: RegisterRequest):
    if not data.name.strip() or not data.password.strip():
        raise HTTPException(status_code=422, detail="Name and password cannot be empty")
    result = functions.register_user(data.name, data.email, data.password)
    if result is False:
        raise HTTPException(status_code=409, detail="Email already exists")
    return result



# A2 - Login user
@app.post("/auth/login")
def login(data: LoginRequest):
    result = functions.verify_login(data.email,data.password)
    if result is False:
        raise HTTPException(status_code=401,detail="Incorrect email or password")
    return result


# A3 - Refresh access token
@app.post("/auth/refresh")
def refresh_token(data: RefreshRequest):

    user_id = verify_token(data.refresh_token,"refresh")
    if user_id is False:
        raise HTTPException(status_code=401,detail="Invalid or expired refresh token")
    new_access_token = functions.create_token(user_id,"access")
    return {"access_token": new_access_token,"token_type": "bearer"}


# E1 - Create Organizer
@app.post("/organizers")
def create_organizer(data: OrganizerRequest, token: str = Header(None)):
    check_role(token, [functions.ADMIN])
    result = functions.create_organizer(data.name,data.email,data.password)
    if result is False:
        raise HTTPException(status_code=400,detail="Email already exists")
    return result

# E2 - Add Player
@app.post("/bestplayer")
def add_player(data: PlayerRequest, token: str = Header(None)):
    check_role(token, [functions.ORGANIZER])
    result = functions.add_player(data.name,data.country,data.team,data.role)
    return result

# E3 - Get All Players
@app.get("/players")
def get_all_players():
    return functions.get_all_players()

# E4 - Get Player By ID
@app.get("/players/{player_id}")
def get_player_by_id(player_id: int):
    result = functions.get_player_by_id(player_id)
    if result is False:
        raise HTTPException(status_code=404,detail="Player not found")
    return result

# E5 - Create Tournament
@app.post("/tournaments")
def create_tournament(data: TournamentRequest, token: str = Header(None)):
    check_role(token, [functions.ORGANIZER])
    result = functions.create_tournament(data.name,data.season,data.start_date,data.end_date,1)
    return result

# E6 - Get all Tournaments
@app.get("/tournaments")
def get_all_tournaments():
    return functions.get_all_tournaments()

# E7 - create teams
@app.post("/fantasy-team")
def create_fantasy_team(data: FantasyTeamData, token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return functions.create_fantasy_team(user_id, data.team_name)

# E8 - adding a players
@app.post("/fantasy-team/player")
def add_player_to_fantasy_team(data: AddPlayerData, token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    response = functions.add_player_to_team(user_id, data.fantasy_team_id, data.player_id)
    if not response:
        raise HTTPException(status_code=400, detail="Unable to add player.")
    return response

# E9 - remove a player
@app.delete("/fantasy-team/player")
def remove_player(data: RemovePlayerData, token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    response = functions.remove_player_from_team(user_id, data.fantasy_team_id, data.player_id)
    if not response:
        raise HTTPException(status_code=404, detail="Player not found.")
    return {"message": "Player removed successfully"}

# E10 - get teams
@app.get("/fantasy-teams")
def get_my_fantasy_teams(token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return functions.get_user_fantasy_teams(user_id)

# E11 - Create contest
@app.post("/contests", status_code=201)
def create_contest(data: ContestRequest, token: str = Header(None)):
    check_role(token, [functions.ORGANIZER])
    user_id = get_current_user(token)
    if not data.name.strip():
        raise HTTPException(status_code=422, detail="Contest name cannot be empty")
    if data.entry_fee < 0 or data.max_entries <= 0:
        raise HTTPException(status_code=422, detail="Invalid contest values")
    result = functions.create_contest(data.match_id,data.name,data.entry_fee,data.max_entries,user_id)
    if result == None:
        raise HTTPException(status_code=404, detail="Match not found")
    return result

# E12 - Join contest
@app.post("/contests/{contest_id}/join", status_code=201)
def join_contest(contest_id: int,data: JoinContestRequest,token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = get_current_user(token)
    result = functions.join_contest(contest_id,data.fantasy_team_id,user_id)
    if result == None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if result == None:
        raise HTTPException(status_code=404, detail="Fantasy team not found")
    if result == "already_joined":
        raise HTTPException(status_code=409, detail="Fantasy team already joined")
    if result == "contest_full":
        raise HTTPException(status_code=400, detail="Contest is full")
    return result

# E13 - Publish player statistics
@app.post("/matches/{match_id}/stats")
def publish_stats(match_id: int,data: PlayerStatsRequest,token: str = Header(None)):
    check_role(token, [functions.ORGANIZER])
    user_id = get_current_user(token)
    stats = [data.runs,data.fours,data.sixes,data.wickets,data.catches,data.run_outs,data.stumpings]
    if any(value < 0 for value in stats):
        raise HTTPException(status_code=422,detail="Statistics cannot be negative")
    result = functions.publish_player_stats(match_id,data.player_id,data.runs,data.fours,data.sixes,data.wickets,data.catches,data.run_outs,data.stumpings)
    if result == None:
        raise HTTPException(status_code=404, detail="Match not found")
    if result == None:
        raise HTTPException(status_code=404, detail="Player not found")
    return result

# E14 - Get contest leaderboard
@app.get("/contests/{contest_id}/leaderboard")
def get_contest_leaderboard(contest_id: int):
    result = functions.get_leaderboard(contest_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Contest not found")
    return result

# E15 - Get fantasy points history
@app.get("/fantasy-points/history")
def get_points_history(token: str = Header(None)):
    check_role(token, [functions.USER])
    user_id = get_current_user(token)
    result = functions.get_fantasy_points_history(user_id)
    return result

# E16 - Post Matches
@app.post("/matches")
def create_match(data: MatchRequest, token: str = Header(None)):
    check_role(token, [functions.ORGANIZER])
    result = functions.create_match(data.tournament_id,data.team1,data.team2,data.match_date)
    if result is False:
        raise HTTPException(status_code=400,detail="Invalid tournament or teams")
    return result

# E17 - Get all Matches
@app.get("/matches")
def get_all_matches():
    return functions.get_all_matches()