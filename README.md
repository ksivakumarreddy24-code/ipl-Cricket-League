# Ipl

| Team | Partner 1 | Partner 2 | Partner 3| Project | Branch |
|---|---|---|---|---|---|
|  | Aditya | sivakumar | pavan|[Hostel-Laundry-machines]() | `IPL` |


# Backend Setup and Execution

Open a terminal and navigate to the backend folder.

cd backend

### Create Virtual Environment

python -m venv venv

### Activate Virtual Environment

Windows:

venv\Scripts\activate

### Install libraries
pip install fastapi
            pydantic 
            sqlalchemy 
            pyjwt 
            argon2-cffi 
            uvicorn

### Install Dependencies

pip install -r requirements.txt

### Run Backend

uvicorn main:app --reload --port 8001

Backend URL:

http://127.0.0.1:8001



## 8. Docker Setup and Execution

### Build Docker Image

docker build -t project-name .

### Run Docker Container

docker run -d -p 8001:8001 --name project-container project-name

### Check Running Containers

docker ps

### Stop Container

docker stop project-container

### start container

docker start project-container

### Remove Container

docker rm project-container

API Documentation:

http://127.0.0.1:8001/docs

##  API Requirements

The application must provide APIs for the following. Fill in the API contract for each row.


## 1. Who is doing what

Update your own row at every check-in.

| Day | Partner | What will you do? | Completed? | What are you going to work on next? | Stuck on? |
|---|---|---|---|---|---|
| Day 1 | Aditya |  | | |   |
| Day 1 | sivakumar |  | | | |
| Day 1 | Pavan  |  |  |  |  |
| Day 2 | sivakumar |  |  | |  |
| Day 2 | Aditya | | | | |
| Day 2 | Pavan  |  | |  ||
| Day 3 | sivakumar | |  |  | |
| Day 3 | Aditya | | |  | |
| Day 3 | Pavan  | |  |  |  |

## 2. Endpoint tracker

Fill in the method and path from your PRD's endpoint table. Status: ✅ done · 🟡 in progress · ⬜ not started

| # | Method + path | Built | Rules checked in /docs | Who |
|---|---|---|---|---|---|
| E1 | post/organizers | ✅ | ✅ | Aditya |
| E2 | post/players | ✅ | ✅ | Aditya |
| E3 | get("/players | ✅ | ✅ | Aditya  |
| E4 | get/players/{player_id} | ✅ | ✅ | Aditya  |
| E5 | post/tournaments | ✅ | ✅ | Aditya |
| E6 | get/tournaments | ✅ | ✅ | pavan |
| E7 | post/fantasy-team | ✅ | ✅ | pavan  |
| E8 | post/fantasy-team/player | ✅ | ✅ | pavan |
| E9 | delete/fantasy-team/player | ✅ | ✅ | pavan  |
| E10 | get/fantasy-teams | ✅ | ✅ | pavan |
| E11 | post/contests | ✅ | ✅ |  sivakumar |
| E12 | post/contests/{contest_id}/join | ✅ | ✅ |  sivakumar  |
| E13 | post/matches/{match_id}/stats | ✅ | ✅ | sivakumar  |
| E14 | get/contests/{contest_id}/leaderboard | ✅ | ✅ | sivakumar   |
| E15 | get/fantasy-points/history | ✅ | ✅ |  sivakumar  |

## Datebase Tables

| # | Table | Columns |
| --- | --- | --- |
| 1 | User |`id,name,email,password,role,created_at` |
| 2 | player |`id,name,country,team,role,created_at`  |
| 3 | Tournament | `id,name,season,start_date,end_date,created_by`|
| 4 | Match | `id,tournament_id,team1,team2,match_date`, |
| 5 | FantasyTeam| `id,user_id,name,created_at` |
| 6 | FantasyTeamPlayer | `id,fantasy_team_id` |
| 7 | Contest | `id,match_id,naem,entry_fee,max_entries,created_by`|
| 8 | ContestEntry | `id,contest_id,fantasy_team_id,joined_at` |
| 9 | PlayerMatchStat | `id,match_id,player_id,runs,fours,sixes,wickets,catches,run_outs,stumpings` |
| 10 | FantasyPointsHistory | `id,contest_entry_id,match_id,points,created_at` |




                   
