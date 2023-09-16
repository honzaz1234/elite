import hockeydata.insert_db.insert_db as insert_db
import hockeydata.database_creator.database_creator as db

from hockeydata.constants import *

class InputLeagueDict():
    """class used for inputing league information in to the DB"""

    def __init__(self, db_session):
        self.db_session = db_session
        pass

    def input_league_dict(self, league_dict):
        """wraper method for inputing all scraped data from dict to DB"""

        league_id = self.input_league_info_dict(
            info_dict=league_dict)
        self.input_league_achievements(
            achiev_dict=league_dict[LEAGUE_ACHIEVEMENTS], league_id=league_id)
        league_standings = InputLeagueStandings(db_session=self.db_session)
        league_standings.input_league_standings_dict(
            stat_dict=league_dict[SEASON_STANDINGS],
            league_id=league_id)
        

    def input_league_info_dict(self, info_dict):
        """method for inputing general info abour league in DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        league_id = db_pipe._input_data_in_league_table(
            league_uid=info_dict[LEAGUE_UID],long_name=info_dict[LEAGUE_NAME])
        return league_id
    
    def input_league_achievements(self, achiev_dict, league_id):
        """method for inputing league achievements into DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        for achiev in achiev_dict:
            db_pipe._input_achievement(
                achiev=achiev, league_id=league_id)    


class InputLeagueStandings():

    """class grouping methods for inputing league standings into DB"""

    def __init__(self, db_session):
        self.db_session = db_session
        pass

    def input_league_standings_dict(self, stat_dict, league_id):
        """method for inputing season standings dict into DB"""

        for season in stat_dict:
            row_dict = {}
            row_dict[SEASON_NAME] = season
            row_dict[LEAGUE_ID] = league_id
            season_dict = stat_dict[season]
            self.input_season_dict(season_dict=season_dict, row_dict = row_dict)

    def input_season_dict(self, season_dict, row_dict):
        """method for inputing standings from one season into DB"""

        for type in season_dict:
            row_dict[SECTION_TYPE] = type
            type_dict = season_dict[type]
            self.input_type_dict(type_dict=type_dict, row_dict=row_dict)
    
    def input_type_dict(self, type_dict, row_dict):
        """method for inputing one section of season standings into DB"""

        for position in type_dict:
            row_dict[LEAGUE_POSITION] = position
            position_dict = type_dict[position]
            self.input_position_dict(position_dict=position_dict, row_dict=row_dict)

    def input_position_dict(self, position_dict, row_dict):
        """method for inputing one team season standings into DB"""
        
        row_dict[TEAM_UID]  = position_dict[TEAM_UID]
        del position_dict[TEAM_UID]
        del position_dict[TEAM_URL]
        for stat in position_dict:
            row_dict[stat] = position_dict[stat]
        db_pipe = insert_db.DatabasePipeline(db_session=self.db_session)
        db_pipe._input_team_position(dict_=row_dict)