from datetime import date
from fastapi import FastAPI, HTTPException, Header,datetime
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
    
class OrganizerRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class CricketPlayerRequest(BaseModel):
    name: str
    team: str
    role: str


class TournamentRequest(BaseModel):
    name: str
    start_date: date
    end_date: date


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


# E6 - Create an organizer account
@app.post("/organizers", status_code=201)
def create_organizer(data: OrganizerRequest, token: str = Header(None)):
    user_id = get_current_user(token)
    check_role(user_id, "admin")

    if not data.username.strip() or not data.password.strip():
        raise HTTPException(status_code=422, detail="Username and password cannot be empty")

    result = functions.create_organizer_account(data.username, data.email, data.password)

    if result == False:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    return result


# E7 - Add a cricket player to the platform
@app.post("/players", status_code=201)
def add_cricket_player(data: CricketPlayerRequest, token: str = Header(None)):
    user_id = get_current_user(token)
    check_role(user_id, "organizer")

    if not data.name.strip() or not data.team.strip() or not data.role.strip():
        raise HTTPException(status_code=422, detail="Player details cannot be empty")

    result = functions.add_cricket_player(data.name, data.team, data.role)

    return result


# E8 - Get all available cricket players
@app.get("/players")
def get_all_cricket_players():
    result = functions.get_all_cricket_players()
    return result


# E9 - Get details of a particular player
@app.get("/players/{player_id}")
def get_player_details(player_id: int):
    result = functions.get_player_details(player_id)

    if result == None:
        raise HTTPException(status_code=404, detail="Player not found")

    return result


# E10 - Create a cricket tournament
@app.post("/tournaments", status_code=201)
def create_tournament(data: TournamentRequest, token: str = Header(None)):
    user_id = get_current_user(token)
    check_role(user_id, "organizer")

    if not data.name.strip():
        raise HTTPException(status_code=422, detail="Tournament name cannot be empty")

    if data.end_date < data.start_date:
        raise HTTPException(status_code=422, detail="End date cannot be before start date")

    result = functions.create_tournament(data.name, data.start_date, data.end_date)

    return result

def check_role(user_id: int, required_role: str):
    role = functions.get_user_role(user_id)

    if role is None:
        raise HTTPException(status_code=404, detail="User not found")

    if role.lower() != required_role.lower():
        raise HTTPException(status_code=403, detail="Access denied")

    return True



