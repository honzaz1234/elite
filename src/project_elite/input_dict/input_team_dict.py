import database.entry_data.input_data.input_data as input_data

from constants import *

class InputTeamDict():

    """class encapsulating methods for puting team data from dcitionary into DB
    """

    def __init__(self):
        pass

    def input_team_dict(self, team_dict):
        """wraper method for puting team data from dictionary into DB"""

        stadium_id = self.input_stadium_dict(
            stadium_dict=team_dict[STADIUM_INFO])
        team_id = self.input_team_info_dict(
            info_dict=team_dict[GENERAL_INFO], stadium_id=stadium_id)
        self.input_affiliated_teams_list(
            team_list=team_dict[AFFILIATED_TEAMS], team_id=team_id)
        self.input_retired_number_dict(
            ret_num_dict=team_dict[RETIRED_NUMBERS], team_id=team_id)
        self.input_team_titles_dict(
            titles_dict=team_dict[HISTORIC_NAMES], team_id=team_id)
        self.input_color_list(
            colour_list=team_dict[COLOUR_LIST], team_id=team_id)

    def input_stadium_dict(self, stadium_dict):
        """method for puting info of stadium team plays in into DB"""

        data_input = input_data.InputData()
        if (set([value for value in stadium_dict.values() 
                 if type(value) is not dict]) == {None}):
            return None
        stadium_id =  data_input.input_stadium_data(stadium_dict=stadium_dict)
        return stadium_id
    
    def input_team_info_dict(self, info_dict, stadium_id):
        """method for putting general team info into DB"""

        data_input = input_data.InputData()
        info_dict[STADIUM_ID] = stadium_id
        team_id = data_input.input_team_data(general_info_dict=info_dict)
        return team_id
    
    def input_affiliated_teams_list(self, team_list, team_id):
        """method for puting relationship between team and its affiliated teams into DB
        """

        data_input = input_data.InputData()
        for u_id in team_list:
            team_a_id = data_input.input_team_uid(u_id=u_id)
            data_input.input_affiliated_teams(main_team=team_id, affiliated_team=team_a_id)

    def input_retired_number_dict(self, ret_num_dict, team_id):
        """method for puting relationship between players whose number was retired by the team and team into DB
        """

        data_input = input_data.InputData()
        for u_id in ret_num_dict:
            data_input = input_data.InputData()
            retired_number = ret_num_dict[u_id][0]
            player_id = data_input.input_player_uid(u_id=int(u_id))
            data_input.input_retired_number_data(
                player_id=player_id, team_id=team_id, number=retired_number)
    
    def input_team_titles_dict(self, titles_dict, team_id):
        """method for puting names that team carried through history into DB"""

        data_input = input_data.InputData()
        for title in titles_dict:
            min = titles_dict[title]["min"]
            max = titles_dict[title]["max"]
            data_input.input_team_name(name=title, min=min, 
                                         max=max, team_id=team_id)
    def input_color_list(self, colour_list, team_id):
        """method for puting relationship between team colours and team into DB
        """
        
        data_input = input_data.InputData()
        for colour in colour_list:
            data_input.input_colour_team(team_id=team_id, colour=colour)






