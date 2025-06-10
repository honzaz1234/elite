import gamedata.insert_db.insert_db_game_data as insert_db
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
        self.input_o = insert_db.GameDataDB(
            self.db_session)


    @time_execution
    def input_all_mappers(
            self, elite_nhl_mapper: dict, stadium_mapper: dict) -> None:
        self._input_elite_nhl_mapper_dict(elite_nhl_mapper)
        self._input_stadium_mapper(stadium_mapper)
        self.db_session.commit()


    def _input_elite_nhl_mapper_dict(self, elite_nhl_mapper: dict) -> None:
        """wrapper method for inputting  all scraped data from dict to DB"""
        db_nhl_elite_mapper = self.mappers_o.get_elite_nhl_mapper()
        elite_nhl_mapper = dict_diff_unique(
            elite_nhl_mapper, db_nhl_elite_mapper)
        for season in elite_nhl_mapper:
            self._input_nhl_elite_season_dict(elite_nhl_mapper[season], season)
        logger.info("Elite NHL mapper succesfully inputted into db")


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


    def _input_stadium_mapper(self, stadium_mapper):
        db_stadium_mapper = self.mappers_o.get_nhl_elite_stadium_mapper()
        stadium_mapper = dict_diff_unique(
            stadium_mapper, db_stadium_mapper)
        for stadium in stadium_mapper:
            self._input_mapped_stadium_into_db(
                stadium, stadium_mapper[stadium])
        logger.info("Stadium mapper succesfully inputted into db")


    def _input_mapped_stadium_into_db(
            self, nhl_name: str, elite_name: str) -> None:
        self.input_o._input_stadium_mapper(nhl_name, elite_name)


class InputGameInfo():


    def __init__(
            self,  db_session: Session, player_mapper: dict, 
            stadium_mapper: dict):
        self.db_session = db_session
        self.input_o = insert_db.GameDataDB(
            self.db_session)
        self.mappers_o = db_mapper.GetDBID(self.db_session)
        self.input_gi = InputGeneralInfo(
            self.db_session, self.input_o, stadium_mapper)
        self.input_shifts = InputShifts(
            self.db_session, player_mapper)
        self.input_PBP = InputPBP(
            self.db_session, player_mapper)

    @time_execution
    def input_game_dict(self, game: dict) -> None:

        match_id = self.input_gi._input_general_info(game)
        self.input_shifts._input_shifts(
            game["shifts"], game["HT"], game["VT"], match_id)
        self.input_PBP._input_PBP(game["PBP"], match_id)
        self.db_session.commit()


    def _input_general_info(self, game: dict) -> int:
        match_id = self.input_gi._input_general_info(game)

        return match_id
    

class InputGeneralInfo():


    def __init__(self, db_session: Session, 
                 input_o: insert_db.GameDataDB, 
                 stadium_mapper: dict):
        self.db_session = db_session
        self.input_o = input_o
        self.stadium_mapper = stadium_mapper


    @time_execution
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
                               "in the DB. Input stadium ID manually: ")
            stadium_elite = self.input_o._get_stadium_name(stadium_id)
            if stadium_elite is None:
                raise 
            self.stadium_mapper[stadium] = stadium_elite
            logger.info(
                "Stadium %s was added to the stadium mapper with value %s", stadium, stadium_elite
                )

        return stadium_id

    
    def _get_general_info_input_dict(self, game: dict, stadium_id: int):
        input_dict = {}
        input_dict["stadium_id"] = stadium_id
        input_dict["match_id"] = game["match_id"]
        input_dict["HT"] = game["HT"]
        input_dict["VT"] = game["VT"]
        input_dict["date"] = game["date"]
        input_dict["time"] = game["start_time_UTC"]
        input_dict["attendance"] = game["attendance"]

        return input_dict
    
    
class InputShifts():


    def __init__(self, db_session: Session, player_mapper: dict):
        self.db_session = db_session
        self.player_mapper = player_mapper
        self.input_o = insert_db.GameDataDB(db_session)

    
    @time_execution
    def _input_shifts(
            self, shifts: dict, HT_id: int, VT_id: int, match_id :int) -> None:
        ids = {"TH": HT_id, "TV": VT_id}
        for team_type in ids:
            self._input_team_shifts(
                shifts[team_type], ids[team_type], match_id)


    def _input_team_shifts(
            self, shifts: list, team_id: int, match_id: int) -> None:
        for player_info in shifts:
            self._input_player_shifts(
                player_info, shifts[player_info], team_id, match_id)
            

    def _input_player_shifts(
            self, player_info: tuple, shifts: list, team_id: int, 
            match_id: int) -> None:
        player_id = self.player_mapper[team_id][player_info]
        for shift in shifts:
            self._input_shift(shift, player_id, team_id, match_id)

    
    def _input_shift(
            self, shift: dict, player_id: int, team_id: int, 
            match_id: int) -> None:
        self.input_o._input_shift(shift, player_id, team_id, match_id)



class InputPBP():


    def __init__(
            self, db_session: Session, player_mapper: dict):
        self.db_session = db_session
        self.player_mapper = player_mapper
        self.input_pbp = insert_db.PBPDB(db_session)
        self.input_o = insert_db.GameDataDB(db_session)


    @time_execution
    def _input_PBP(self, plays: list, match_id) -> None:
        for play in plays:
            play_id = self.input_o._input_play(play, match_id)
            try:
                self._input_poi(play_id, play["poi"])
            except Exception as e:
                print(e)
                print(play)
                raise e


    def _input_poi(self, play_id: int, shifts: dict) -> None:
        if "poi" in shifts.get("error", {}):
            for team_id, error_data in shifts["error"].items():
                poi = error_data.get("poi")
                error_type = error_data.get("error_type")
                self.input_pbp._input_broken_poi(
                    play_id, team_id, poi, error_type)
            for team_id in shifts:
                if team_id == "error":
                    continue
                self._input_team_poi(play_id, shifts[team_id], team_id)


    def _input_team_poi(
            self, play_id: int, team_shifts: list, team_id: int) -> None:
        for player_id in team_shifts:
            self.input_pbp._input_poi(play_id, player_id, team_id)
























    