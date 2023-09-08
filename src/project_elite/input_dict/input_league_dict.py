import database.entry_data.input_data.input_data as input_data

from constants import *

class InputLeagueDict():
    """class used for inputing league information in to the DB"""

    def __init__(self):
        pass

    def input_league_dict(self, league_dict):
        """wraper method for inputing all scraped data from dict to DB"""

        league_id = self.input_league_info_dict(
            info_dict=league_dict[GENERAL_INFO])
        self.input_league_achievements(
            achiev_dict=league_dict[LEAGUE_ACHIEVEMENTS], league_id=league_id)
        self.input_league_standings_dict(
            stat_dict=league_dict[SEASON_STANDINGS],
            league_id=league_id)
        

    def input_league_info_dict(self, info_dict):
        """method for inputing general info abour league in DB"""

        data_input = input_data.InputData()
        league_id = data_input.input_league_data(
            u_id=info_dict[LEAGUE_UID], long_name=info_dict[LONG_NAME])
        return league_id
    
    def input_league_achievements(self, achiev_dict, league_id):
        """method for inputing league achievements into DB"""

        data_input = input_data.InputData()
        for achiev in achiev_dict:
            data_input.input_achievement(achievement_name=achiev, league_id=league_id)    

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
        input_data_o = input_data.InputData()
        input_data_o.input_team_season_data(ts_dict=row_dict)