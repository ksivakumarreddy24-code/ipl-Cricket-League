from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import functions


class AddPlayerData(BaseModel):
    fantasy_team_id: int
    player_id: int

class RemovePlayerData(BaseModel):
    fantasy_team_id: int
    player_id: int

@app.get("/tournaments")
def get_all_tournaments():
    return functions.get_all_tournaments()

@app.post("/fantasy-team")
def create_fantasy_team(data: FantasyTeamData, token: str = Header(None)):
    user_id = functions.verify_token(token=token, token_type="access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return functions.create_fantasy_team(user_id, data.team_name)

@app.post("/fantasy-team/player")
def add_player(data: AddPlayerData, token: str = Header(None)):
    user_id = functions.verify_token(token=token, token_type="access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    response = functions.add_player_to_team(user_id, data.fantasy_team_id, data.player_id)
    if not response:
        raise HTTPException(status_code=400, detail="Unable to add player.")
    return response
 
@app.delete("/fantasy-team/player")
def remove_player(data: RemovePlayerData, token: str = Header(None)):
    user_id = functions.verify_token(token=token, token_type="access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    response = functions.remove_player_from_team(user_id, data.fantasy_team_id, data.player_id)
    if not response:
        raise HTTPException(status_code=404, detail="Player not found.")
    return {"message": "Player removed successfully"}

@app.get("/fantasy-teams")
def get_my_fantasy_teams(token: str = Header(None)):
    user_id = functions.verify_token(token=token, token_type="access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    return functions.get_user_fantasy_teams(user_id)
