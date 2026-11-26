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
| Day 1 | Aditya | | | |   |
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

| # | Method + path | Built | Rules checked in /docs | Connected to React | Who |
|---|---|---|---|---|---|
| E1 |  | ✅ | ✅ | ⬜ |  |
| E2 | | ✅ | ✅ | ⬜ |   |
| E3 | | ✅ | ✅ | ⬜ |   |
| E4 |  | ✅ | ✅ | ⬜ |   |
| E5 | | ✅ | ✅ | ⬜ |   |
| E6 | | ✅ | ✅ | ⬜ |   |
| E7 |  | ✅ | ✅ | ⬜ |   |
| E8 |  | ✅ | ✅ | ⬜ |   |
| E9 |  | ✅ | ✅ | ⬜ |   |
| E10 | | ✅ | ✅ | ⬜ |   |
| E11 |  | ✅ | ✅ | ⬜ |  |
| E12 | | ✅ | ✅ | ⬜ |   |
| E13 | | ✅ | ✅ | ⬜ |   |
| E14 |  | ✅ | ✅ | ⬜ |   |
| E15 | | ✅ | ✅ | ⬜ |   |


## File Structure 

```text
ipl/
└── backend/
    ├── __pycache__/
    ├── .venv/
    ├── functions.py
    ├── hostel_laundry.db
    └── main.py
```                
