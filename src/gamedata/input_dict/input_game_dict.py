import hockeydata.insert_db.elite_insert_db as elite_insert_db

from decorators import time_execution
from logger.logging_config import logger
from sqlalchemy.orm import Session


class InputEliteNHLmapper():


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.input_o = elite_insert_db.EliteDatabasePipeline(db_session=self.db_session)


    @time_execution
    def input_elite_nhl_mapper_dict(self, elite_nhl_mapper: dict) -> None:
        """wrapper method for inputting  all scraped data from dict to DB"""
        for season in elite_nhl_mapper:
            self._input_elite_nhl_season_dict(elite_nhl_mapper[season], season)
        logger.info(f"Elite NHL mapper succesfully inputted into db")


    def _input_nhl_elite_season_dict(
            self, season_mapper: dict, season: str) -> None:
        for team_id in season_mapper:
            self._input_nhl_elite_team_mapper(
                season_mapper[team_id], season, team_id)


    def _input_nhl_elite_team_mapper(
            self, team_mapper: dict, season: str, team_id: int) -> None:
        for nhl_name in team_mapper:
            self._input_nhl_elite_player_mapper(
                team_mapper[nhl_name], season, team_id, nhl_name)


    def _input_nhl_elite_player_mapper(
            self, player_mapper: dict, season: str, team_id: int,
              nhl_name: str) -> None:
        input_dict = player_mapper
        input_dict["season"] = season
        input_dict["team_id"] = team_id
        input_dict["nhl_name"] = nhl_name
        self.input_o._input_nhl_elite_player_mapper(input_dict)