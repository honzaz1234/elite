import gamedata.insert_db.insert_db_game_data as gamedata_insert_db
import mappers.db_mappers as db_mapper

from common_functions import dict_diff_unique
from decorators import time_execution
import mappers.db_mappers as db_mapper
from logger.logging_config import logger
from sqlalchemy.orm import Session

from constants import * 


class InputEliteNHLmapper():


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.mappers_o = db_mapper.GetDBID(self.db_session)
        self.input_o = gamedata_insert_db.GameDataDB(
            self.db_session)


    @time_execution
    def input_elite_nhl_mapper_dict(self, elite_nhl_mapper: dict) -> None:
        """wrapper method for inputting  all scraped data from dict to DB"""
        db_nhl_elite_mapper = self.mappers_o.get_elite_nhl_mapper()
        elite_nhl_mapper = dict_diff_unique(
            elite_nhl_mapper, db_nhl_elite_mapper)
        for season in elite_nhl_mapper:
            self._input_nhl_elite_season_dict(elite_nhl_mapper[season], season)
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
        input_dict[SEASON_NAME] = season
        input_dict["team_id"] = team_id
        input_dict["nhl_name"] = nhl_name
        self.input_o._input_nhl_elite_player_mapper(input_dict)


class InputGameInfo():


    def __init__(self,  db_session: Session):
        self.db_session = db_session
        self.input_o = gamedata_insert_db.GameDataDB(
            self.db_session)
        self.mappers_o = db_mapper.GetDBID(self.db_session)
        self.stadium_mapper = self.mappers_o.get_nhl_elite_stadium_mapper()
        self.input_gi = InputGeneralInfo(
            self.db_session, self.input_o, self.stadium_mapper)



    def input_game_dict(self, game: dict) -> None:

        match_id = self._input_general_info(game)

    def _input_general_info(self, game: dict) -> int:
        match_id = self.input_gi._input_general_info(game)

        return match_id
    

    def _get_general_info_input_dict(game: dict, stadium_id: int):
        input_dict = {}
        input_dict["stadium_id"] = stadium_id
        input_dict["HT"] = game["HT"]
        input_dict["VT"] = game["HT"]
        input_dict["date"] = game["date"]
        input_dict["time"] = game["time"]
        input_dict["attendance"] = game["attendance"]

        return input_dict
    

class InputGeneralInfo():


    def __init__(self, db_session: Session, 
                 input_o: gamedata_insert_db.GameDataDB, 
                 stadium_mapper: dict):
        self.db_session = db_session
        self.input_o = input_o
        self.stadium_mapper = stadium_mapper


    def _input_general_info(self, game):
        stadium_id = self._get_stadium_id(game["stadium"])
        input_dict = self._get_general_info_input_dict(game, stadium_id)
        match_id = self.input_o._input_general_info(input_dict)

        return match_id

    
    def _get_stadium_id(self, stadium: str) -> int:
        if stadium in self.stadium_mapper:
            stadium = self.stadium_mapper[stadium]
        stadium_id = self.input_o._get_stadium_id(stadium)
        if stadium_id is None:
            stadium_id = input(f"Stadium under name {stadium} does not exist "
                               "in the DB. Input stadium ID manually")
            stadium_elite = self.input_o._get_stadium_name(stadium_id)
            self.stadium_mapper[stadium] = stadium_elite
            logger.info(f"Stadium {stadium} was added to the stadium mapper"
                        f" with value {stadium_elite}")

        return stadium_id

    
    def _get_general_info_input_dict(game: dict, stadium_id: int):
        input_dict = {}
        input_dict["stadium_id"] = stadium_id
        input_dict["HT"] = game["HT"]
        input_dict["VT"] = game["HT"]
        input_dict["date"] = game["date"]
        input_dict["time"] = game["time"]
        input_dict["attendance"] = game["attendance"]

        return input_dict
    
    
class InputShifts():


    def __init__(self, db_session: Session, 
                 input_o: gamedata_insert_db.GameDataDB):
        self.db_session = db_session
        self.input_o = input_o

    
    def _input_shifts(self, )


    