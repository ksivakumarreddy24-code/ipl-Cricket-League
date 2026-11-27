
# IPL Fantasy Cricket League – Backend

# Team 06 

| Team | Partner 1 | Partner 2 | Partner 3 | Project |
|---|---|---|---|---|
| 04 | aditya | pavan | sivakumar | (https://github.com/ksivakumarreddy24-code/ipl-Cricket-League) |

A Python-based IPL Fantasy Cricket League Backend API built using FastAPI and SQLite.

This application allows users to create fantasy teams, select cricket players, participate in contests, earn fantasy points, and view contest leaderboards.

The system includes authentication, Role-Based Access Control (RBAC), tournament and match management, player statistics, and automatic fantasy point calculation.

---

##  Project Overview

The IPL Fantasy Cricket League provides three types of user roles:

| Role | Responsibilities |
|---|---|
| Admin | Creates and manages organizer accounts |
| Organizer | Manages players, tournaments, matches, contests and player statistics |
| User | Creates fantasy teams, selects players and joins contests |

---

## 1. Who is doing what

Update your own row at every check-in.

| Day | Partner | What will you do? | Completed? | What are you going to work on next? | Stuck on? |
|---|---|---|---|---|---|
| Day 1 | aditya | E1 to E5 endpoints | E1 & E2 | E3 to E6 endpoints | no |
| Day 1 | pavan| Authenticatin endpoints and E6,E7,E8,E9,E10 endpoints | Athentication Endpoints  | E7,E8,E9 Endpoints  | no |
| Day 1 | sivakumar | Defined Endpoints from E11 to E15 | E11, E13 |E14, 15 | No |
| Day 2 | aditya | working on E3,E4,E5, functions| completed | solve the errors|yes  |
| Day 2 | pavan | E8,E9,E10 endpoints  | E8,E9,E10 endpoints  | solvoing the merge errors and checking swager  | yes |
| Day 2 | sivakumar | Defining E14 and E15 | E14 , 15 | Assign Role Based Access | No |
| Day 3 | aditya | solvoing the merge errors and checking swager with team  |done  | prepare for presentation  | no |
| Day 3 | pavan | solvoing the merge errors and checking swager with team  | done | prepare for presentation  |  No  |
| Day 3 | sivakumar |  solvoing the merge errors and checking swager with team  | done |  prepare for presentation | No |

##  Features

- User registration and login
- Secure password hashing using Argon2
- JWT-based authentication with access and refresh tokens
- Role-Based Access Control (RBAC)
- Player management
- Tournament creation and management
- Match scheduling and management
- Fantasy team creation
- Add and remove players from fantasy teams
- Contest creation and participation
- Player match statistics management
- Automatic fantasy point calculation
- Contest leaderboard
- Fantasy points history

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API development |
| SQLite | Database |
| SQLAlchemy | Object Relational Mapping (ORM) |
| Pydantic | Request data validation |
| PyJWT | Token generation and verification |
| Argon2 | Password hashing |
| Docker | Application containerization |
| GitHub Actions | CI/CD automation |
| Pytest | Python testing framework |

---

##  Database Design

The project contains 10 database tables.

| No. | Table | Description |
|---|---|---|
| 1 | Users | Stores user details, passwords and roles |
| 2 | Players | Stores cricket player information |
| 3 | Tournaments | Stores tournament details |
| 4 | Matches | Stores individual matches in tournaments |
| 5 | Fantasy Teams | Stores teams created by users |
| 6 | Fantasy Team Players | Connects fantasy teams with selected players |
| 7 | Contests | Stores contests associated with matches |
| 8 | Contest Entries | Stores fantasy team participation in contests |
| 9 | Player Match Stats | Stores individual player performance statistics |
| 10 | Fantasy Points History | Stores fantasy points earned by contest entries |

### Database Relationships

- One tournament can contain multiple matches.
- A user can create multiple fantasy teams.
- A fantasy team can contain multiple players.
- A player can belong to multiple fantasy teams.
- A match can have multiple contests.
- A contest can have multiple entries.
- Player match statistics are used to calculate fantasy points.
- Fantasy points history maintains the points earned by contest participants.

---

##  Authentication and Authorization

The project uses JWT-based authentication to secure API endpoints.

### Authentication Features

| Feature | Configuration |
|---|---|
| Password Hashing | Argon2 |
| Authentication | JWT |
| Access Token Expiration | 15 Minutes |
| Refresh Token Expiration | 7 Days |
| Authorization | Role-Based Access Control |

### Role Permissions

| Operation | Admin | Organizer | User |
|---|:---:|:---:|:---:|
| Create Organizer | ✅ | ❌ | ❌ |
| Add Players | ❌ | ✅ | ❌ |
| Create Tournament | ❌ | ✅ | ❌ |
| Create Match | ❌ | ✅ | ❌ |
| Create Contest | ❌ | ✅ | ❌ |
| Publish Player Statistics | ❌ | ✅ | ❌ |
| Create Fantasy Team | ❌ | ❌ | ✅ |
| Add/Remove Players | ❌ | ❌ | ✅ |
| Join Contest | ❌ | ❌ | ✅ |
| View Public Data | ✅ | ✅ | ✅ |

---

##  API Endpoints

The application provides the following REST API endpoints.

### 1. Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and generate tokens |
| POST | `/auth/refresh` | Generate a new access token |

### 2. Organizer and Player APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/organizers` | Create an organizer account |
| POST | `/addplayer` | Add a cricket player |
| GET | `/players` | Get all available players |
| GET | `/players/{player_id}` | Get player details by ID |

### 3. Tournament and Match APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tournaments` | Create a tournament |
| GET | `/tournaments` | Get all tournaments |
| POST | `/matches` | Create a match |
| GET | `/matches` | Get all matches |

### 4. Fantasy Team APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/fantasy-team` | Create a fantasy team |
| POST | `/fantasy-team/player` | Add a player to a fantasy team |
| DELETE | `/fantasy-team/player` | Remove a player from a fantasy team |
| GET | `/fantasy-teams` | Get the logged-in user's fantasy teams |

### 5. Contest and Fantasy Points APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/contests` | Create a contest |
| POST | `/contests/{contest_id}/join` | Join a contest |
| POST | `/matches/{match_id}/stats` | Publish player match statistics |
| GET | `/contests/{contest_id}/leaderboard` | Get contest leaderboard |
| GET | `/fantasy-points/history` | Get fantasy points history |

---

##  Fantasy Points System

Fantasy points are calculated based on individual cricket player performances during a match.

| Player Performance | Fantasy Points |
|---|:---:|
| Each Run | +1 |
| Each Four Bonus | +1 |
| Each Six Bonus | +2 |
| Each Wicket | +25 |
| Each Catch | +8 |
| Each Run Out | +12 |
| Each Stumping | +12 |

The total fantasy points earned by players contribute to their respective fantasy team's score.

The contest leaderboard ranks participating fantasy teams based on their calculated points.

---

##  Project Structure

```text
ipl-Cricket-League/
│
├── .github/
│   └── workflows/
│       └── docker.yml
│
├── tests/
│   └── test_*.py
│
├── main.py
├── functions.py
├── iplleague.db
├── requirements.txt
├── Dockerfile
└── README.md
```

### File Descriptions

| File/Folder | Description |
|---|---|
| `.github/workflows/` | GitHub Actions workflow configuration |
| `tests/` | Automated test cases |
| `main.py` | FastAPI application and API endpoints |
| `functions.py` | Database operations and business logic |
| `iplleague.db` | SQLite database |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker image configuration |
| `README.md` | Project documentation |

---

##  Installation and Setup

### Prerequisites

- Python 3.10 or above
- Git
- Docker (Optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/ksivakumarreddy24-code/ipl-Cricket-League.git
```

### Step 2: Navigate to the Project Directory

```bash
cd ipl-Cricket-League
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Windows (Git Bash):**

```bash
source .venv/Scripts/activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```


### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Backend

```bash
uvicorn main:app --reload --port 8001
```

Backend URL:

```text
http://127.0.0.1:8001
```

---

##  Docker Setup and Execution

The project includes a Dockerfile for containerizing the FastAPI backend.

### Build Docker Image

```bash
docker build -t ipl-fantasy-league .
```

### Run Docker Container

```bash
docker run -d -p 8001:8001 --name ipl-fantasy-container ipl-fantasy-league
```

### Check Running Containers

```bash
docker ps
```

### Stop Container

```bash
docker stop ipl-fantasy-container
```

### Start Container

```bash
docker start ipl-fantasy-container
```

### Remove Container

```bash
docker rm ipl-fantasy-container
```

**Note:** For persistent SQLite data, configure a suitable mounted data directory and database URL.

---

##  API Documentation

FastAPI automatically generates interactive API documentation.

After starting the backend, open the following URLs:

### Swagger UI

```text
http://127.0.0.1:8001/docs
```


### OpenAPI JSON

```text
http://127.0.0.1:8001/openapi.json
```

Swagger UI allows developers to:

- Explore all available API endpoints.
- View request and response schemas.
- Test API requests directly from the browser.
- Understand API validation and error responses.

---

##  CI/CD Pipeline

The project uses GitHub Actions to automate the Docker image workflow.

The CI/CD pipeline helps automate:

- Triggering the workflow when changes are pushed to the configured GitHub branch.
- Building the Docker image.
- Publishing the Docker image when configured with the required registry credentials.

Workflow configuration:

```text
.github/workflows/docker.yml
```

---

##  Testing

The project uses Pytest for automated testing.

### Run All Tests

```bash
pytest -v
```

Tests can cover the following modules:

- User registration and authentication.
- JWT token validation.
- Role-Based Access Control.
- Player management.
- Tournament and match management.
- Fantasy team creation and player selection.
- Contest participation.
- Fantasy point calculation.
- Contest leaderboard generation.

---

##  Project Objective

The primary objective of this project is to develop a secure backend system for an IPL Fantasy Cricket League.

This project demonstrates practical implementation of:

- REST API development using FastAPI.
- Relational database design and management.
- SQLAlchemy ORM integration.
- Secure authentication using JWT and Argon2.
- Role-Based Access Control.
- Backend business logic and data validation.
- Automatic fantasy point calculation.
- Docker-based application containerization.
- CI/CD automation using GitHub Actions.
- Backend testing using Pytest.

---





