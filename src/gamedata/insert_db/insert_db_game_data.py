import database_creator.database_creator as db
import database_insert.db_insert as db_insert

from hockeydata.constants import *
from logger.logging_config import logger
from sqlalchemy import update
from sqlalchemy.orm import Session


class GameDataEliteDatabasePipeline():
    """class containing methods used for inserting data in DB"""


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.db_method = db_insert.DatabaseMethods(self.db_session)
        self.query = db_insert.Query(db_session=self.db_session)    


    def _input_nhl_elite_player_mapper(self, dict_: dict) -> None:
            season_id = self.db_method._input_unique_data(
                    table=db.Season, season=dict_[SEASON_NAME])
            mapper_id = self.db_method._input_unique_data(
                table=db.NHLEliteNameMapper,
                nhl_name=dict_["nhl_name"],
                elite_name=dict_["db_name"],
                player_number = dict_["number"],
                team_id = dict_["team_id"],
                season_id = season_id,
                )
            
            return mapper_id