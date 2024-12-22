import hockeydata.insert_db.insert_db as insert_db
from hockeydata.constants import *
from sqlalchemy.orm import Session


class InputLeagueDict():

    """class used for inputting  league information in to the DB"""

    def __init__(self, session_db: Session):
        self.db_session = session_db

    def input_league_dict(self, league_dict: dict):
        """wrapper method for inputting  all scraped data from dict to DB"""

        league_id = self._input_league_info_dict(
            info_dict=league_dict)
        self._input_league_achievements(
            achiev_dict=league_dict[LEAGUE_ACHIEVEMENTS], league_id=league_id)
        league_standings = InputLeagueStandings(db_session=self.db_session)
        league_standings._input_league_standings_dict(
            stat_dict=league_dict[SEASON_STANDINGS],
            league_id=league_id)
        
    def _input_league_info_dict(self, info_dict: dict) -> int:
        """method for inputting  general info abour league in DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        league_id = db_pipe._input_data_in_league_table(
            league_uid=info_dict[LEAGUE_UID], long_name=info_dict[LEAGUE_NAME])
        return league_id
    
    def _input_league_achievements(self, achiev_dict: dict, league_id: int):
        """method for inputting  league achievements into DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        for achiev in achiev_dict:
            db_pipe._input_achievement(achiev=achiev, 
                                       league_id=league_id)    


class InputLeagueStandings():

    """class grouping methods for inputting  league standings into DB"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        pass

    def _input_league_standings_dict(self, stat_dict: dict, league_id: int):
        """method for inputting  season standings dict into DB"""

        for season in stat_dict:
            row_dict = {}
            row_dict[SEASON_NAME] = season
            row_dict[LEAGUE_ID] = league_id
            season_dict = stat_dict[season]
            self._input_season_dict(season_dict=season_dict, 
                                    row_dict=row_dict)

    def _input_season_dict(self, season_dict: dict, row_dict: dict):
        """method for inputting  standings from one season into DB"""

        for type in season_dict:
            row_dict[SECTION_TYPE] = type
            type_dict = season_dict[type]
            self._input_type_dict(type_dict=type_dict, row_dict=row_dict)
    
    def _input_type_dict(self, type_dict: dict, row_dict: dict):
        """method for inputting  one section of season standings into DB"""

        for position in type_dict:
            row_dict[LEAGUE_POSITION] = position
            position_dict = type_dict[position]
            self._input_position_dict(
                position_dict=position_dict, row_dict=row_dict)

    def _input_position_dict(self, position_dict: dict, row_dict: dict):
        """method for inputting  one team season standings into DB"""
        
        row_dict[TEAM_UID]  = position_dict[TEAM_UID]
        del position_dict[TEAM_UID]
        del position_dict[TEAM_URL]
        for stat in position_dict:
            row_dict[stat] = position_dict[stat]
        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        db_pipe._input_team_position(dict_=row_dict)