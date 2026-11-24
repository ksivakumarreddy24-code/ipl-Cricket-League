
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

# E11 - Create contest
@app.post("/contests", status_code=201)
def create_contest(data: ContestRequest, token: str = Header(None)):
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
    user_id = get_current_user(token)
    result = functions.get_fantasy_points_history(user_id)
    return result