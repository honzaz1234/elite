import pandas as pd

from sqlalchemy import Table
from sqlalchemy.orm import Session

import database_creator.database_creator as db
import database_queries.database_query as dq

from logger.logging_config import logger


class DbDataGetter():


    def __init__(self, session: Session):
        self.session = session


    def get_all_player_season_data(
            self, selected_seasons: list) -> dict:
        query_object = dq.DbDataGetter(session=self.session)
        seasons_filter = [filter(db.Season.season.in_(selected_seasons))]
        player_results = query_object.get_db_query_result(
            query_name="nhl_season_players", filters=seasons_filter)
        goalkeeper_results = query_object.get_db_query_result(
            query_name="nhl_season_goalies", filters=seasons_filter)
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
    

    def check_match_player_to_id(
            self, db_data: dict, scraped_data: dict) -> dict:
        db_names = [player_dict["player_name"] for player_dict in db_data]
        
        for player_info in scraped_data:
            if player_info[0] not in db_names:
                logger.error("")
