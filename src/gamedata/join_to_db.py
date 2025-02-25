import pandas as pd

from sqlalchemy import Table, TextClause

import database_creator.database_creator as db


class DBJoiner():


    def __init__(self, session):

        self.session = session

    def get_all_player_season_data(
            self, selected_seasons: list) -> dict:
        player_results = self.get_player_season_data(
            table=db.PlayerStats, selected_seasons=selected_seasons)
        goalkeeper_results = self.get_player_season_data(
            table=db.GoalieStats, selected_seasons=selected_seasons)
        results = player_results + goalkeeper_results
        season_team_players: dict[str, dict[str, list[str]]] = {}
        for row in results:
            player_id, player_name, team_id, team_name, season = row

            if season not in season_team_players:
                season_team_players[season] = {}

            if team_name not in season_team_players[season]:
                season_team_players[season][team_name] = []

            season_team_players[season][team_name].append(
                {"player_name": player_name, "player_id": player_id})
            
        return season_team_players
    
    def get_player_season_data(
            self, table: Table, selected_seasons: list) -> list:

        results = self.get_stats_query(
            table=table, selected_seasons=selected_seasons)
        # results = self.session.query.all()
        return results
    
    def get_stats_query(
            self, table: Table, selected_seasons: list) -> list:

        query = (self.session.query(
            table.player_id,
            db.Player.name.label("player_name"),
            table.team_id,
            db.Team.team,
            db.Season.season,
        ).join(db.Player, table.player_id == db.Player.id)
        .join(db.Team, table.team_id == db.Team.id)
        .join(db.Season, table.season_id == db.Season.id)
        .join(db.League, table.league_id == db.League.id)
        .filter(db.Season.season.in_(selected_seasons))
        .filter(db.League.uid == 'nhl')
        .all())

        return query
    
class PlayerShiftUpdater():


    def __init__(self):
        pass


    def 


