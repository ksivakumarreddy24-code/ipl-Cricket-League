from sqlalchemy.orm import Session
from functions import engine, Tournament, FantasyTeam, FantasyTeamPlayer, Player

# E6
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


# E7
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

# E8
def add_player_to_team(user_id, fantasy_team_id, player_id):
    session = Session(engine)
    team = session.query(FantasyTeam).filter_by(
        id=fantasy_team_id,
        user_id=user_id
    ).first()

    if team is None:
        session.close()
        return False

    player = session.query(Player).filter_by(id=player_id).first()

    if player is None:
        session.close()
        return False

    player_exists = session.query(FantasyTeamPlayer).filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id
    ).first()

    if player_exists is not None:
        session.close()
        return False

    total_players = session.query(FantasyTeamPlayer).filter_by(
        fantasy_team_id=fantasy_team_id
    ).count()

    if total_players >= 11:
        session.close()
        return False

    fantasy_player = FantasyTeamPlayer(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id
    )

    session.add(fantasy_player)
    session.commit()

    response = {
        "id": fantasy_player.id,
        "fantasy_team_id": fantasy_player.fantasy_team_id,
        "player_id": fantasy_player.player_id
    }

    session.close()
    return response


# E9
def remove_player_from_team(user_id, fantasy_team_id, player_id):
    session = Session(engine)

    team = session.query(FantasyTeam).filter_by(
        id=fantasy_team_id,
        user_id=user_id
    ).first()

    if team is None:
        session.close()
        return False

    fantasy_player = session.query(FantasyTeamPlayer).filter_by(
        fantasy_team_id=fantasy_team_id,
        player_id=player_id
    ).first()

    if fantasy_player is None:
        session.close()
        return False

    session.delete(fantasy_player)
    session.commit()

    session.close()
    return True


# E10
def get_user_fantasy_teams(user_id):
    session = Session(engine)

    teams = session.query(FantasyTeam).filter_by(
        user_id=user_id
    ).all()

    response = []

    for team in teams:
        player_count = session.query(FantasyTeamPlayer).filter_by(
            fantasy_team_id=team.id
        ).count()

        response.append({
            "id": team.id,
            "name": team.name,
            "players": player_count,
            "created_at": team.created_at
        })

    session.close()
    return response
