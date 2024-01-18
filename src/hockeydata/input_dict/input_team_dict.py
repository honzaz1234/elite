import hockeydata.insert_db.insert_db as insert_db
from hockeydata.constants import *
from sqlalchemy.orm import Session


class InputTeamDict():

    """class encapsulating methods for putting  team data from dcitionary into DB
    """

    def __init__(self, session_db: Session):
        self.session_db=session_db
        pass

    def input_team_dict(self, team_dict: dict):
        """wrapper method for putting  team data from dictionary into DB"""

        stadium_id = self._input_stadium_dict(
            stadium_dict=team_dict[STADIUM_INFO])
        team_id = self._input_team_info_dict(
            info_dict=team_dict[GENERAL_INFO], stadium_id=stadium_id)
        self._input_affiliated_teams_list(
            team_list=team_dict[AFFILIATED_TEAMS], team_id=team_id)
        self._input_retired_number_dict(
            ret_num_dict=team_dict[RETIRED_NUMBERS], team_id=team_id)
        self._input_team_titles_dict(
            titles_dict=team_dict[HISTORIC_NAMES], team_id=team_id)

    def _input_stadium_dict(self, stadium_dict: dict) -> int:
        """method for putting  info of stadium team plays in into DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        if (set([value for value in stadium_dict.values() 
                 if type(value) is not dict]) == {None}):
            return None
        stadium_id =  db_pipe._input_stadium_data(stadium_dict=stadium_dict)
        return stadium_id
    
    def _input_team_info_dict(self, info_dict: dict, stadium_id: int) -> int:
        """method for putting general team info into DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        info_dict[STADIUM_ID] = stadium_id
        team_id = db_pipe.input_data_in_team_table(dict_info=info_dict, 
                                                   stadium_id=stadium_id)
        self._input_color_list(colour_list=info_dict[COLOUR_LIST], 
                               team_id=team_id)
        return team_id
    
    def _input_color_list(self, colour_list: list, team_id: int):
        """method for putting  relationship between team colours and team into DB
        """
        
        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        for colour in colour_list:
            db_pipe._input_colour_team(team_id=team_id, colour=colour)
    
    def _input_affiliated_teams_list(self, team_list: list, team_id: int):
        """method for putting  relationship between team and its affiliated teams into DB
        """

        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        for uid in team_list:
            db_pipe._input_affiliated_teams(team_id=team_id, team_aff_uid=uid)

    def _input_retired_number_dict(self, ret_num_dict: dict, team_id: int):
        """method for putting  relationship between players whose number was retired by the team and team into DB
        """

        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        for uid in ret_num_dict:
            retired_number = ret_num_dict[uid][0]
            db_pipe._input_retired_number_relation(player_uid=uid, 
                                                   team_id=team_id, number=retired_number)
    
    def _input_team_titles_dict(self, titles_dict: dict, team_id: int):
        """method for putting  names that team carried through history into DB"""

        db_pipe = insert_db.DatabasePipeline(db_session=self.session_db)
        for title in titles_dict:
            min = titles_dict[title]["min"]
            max = titles_dict[title]["max"]
            db_pipe._input_team_name(name=title, 
                                     min=min, 
                                     max=max, 
                                     team_id=team_id)
            






