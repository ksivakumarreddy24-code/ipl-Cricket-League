
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

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

class RegisterRequest(BaseModel):
    username: str
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
    
class FantasyTeamRequest(BaseModel):
    tournament_id: int
    name: str


class AddPlayerRequest(BaseModel):
    player_id: int


class PlayerStatsRequest(BaseModel):
    player_id: int
    runs: int
    fours: int
    sixes: int
    wickets: int
    catches: int
    run_outs: int
    stumpings: int


# Resolve the verifier dynamically so module type checkers do not require a
# statically declared attribute on the functions module.
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


@app.get("/")
def home():
    return {"message": "IPL Fantasy Cricket League API is running"}


# A1 - Register user
@app.post("/auth/register", status_code=201)
def register(data: RegisterRequest):
    if not data.username.strip() or not data.password.strip():
        raise HTTPException(status_code=422,detail="Username and password cannot be empty")
    result = functions.register_user(data.username,data.email,data.password)
    if result is False:
        raise HTTPException(status_code=409,detail="Email already exists")
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


# E6 - Get all tournaments
@app.get("/tournaments")
def get_all_tournaments():
    result = functions.get_all_tournaments()
    return result

# E7 - Create a fantasy team
@app.post("/fantasy-teams", status_code=201)
def create_fantasy_team(data: FantasyTeamRequest, token: str = Header(None)):
    user_id = get_current_user(token)

    if not data.name.strip():
        raise HTTPException(status_code=422, detail="Team name cannot be empty")

    result = functions.create_fantasy_team(user_id, data.tournament_id, data.name)

    if result == None:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return result

# E8 - Add a player to a fantasy team
@app.post("/fantasy-teams/{team_id}/players", status_code=201)
def add_player_to_fantasy_team(team_id: int, data: AddPlayerRequest, token: str = Header(None)):
    user_id = get_current_user(token)

    result = functions.add_player_to_fantasy_team(team_id, data.player_id, user_id)

    if result == "team_not_found":
        raise HTTPException(status_code=404, detail="Fantasy team not found")

    if result == "player_not_found":
        raise HTTPException(status_code=404, detail="Player not found")

    if result == "already_added":
        raise HTTPException(status_code=409, detail="Player already added to fantasy team")

    return result

# E9 - Remove a player from a fantasy team
@app.delete("/fantasy-teams/{team_id}/players/{player_id}")
def remove_player_from_fantasy_team(team_id: int, player_id: int, token: str = Header(None)):
    user_id = get_current_user(token)

    result = functions.remove_player_from_fantasy_team(team_id, player_id, user_id)

    if result == "team_not_found":
        raise HTTPException(status_code=404, detail="Fantasy team not found")

    if result == "player_not_found":
        raise HTTPException(status_code=404, detail="Player not found in fantasy team")

    return result

# E10 - Get logged-in user's fantasy teams
@app.get("/fantasy-teams/my-teams")
def get_my_fantasy_teams(token: str = Header(None)):
    user_id = get_current_user(token)

    result = functions.get_my_fantasy_teams(user_id)

    return result

