import database.entry_data.input_data.input_data as input_data
import time

class InputPlayerDict():

    def __init__(self):
        pass

    def input_player_dict(self, dict):
        time_s = time.time()
        input_data_o = input_data.InputData()
        dict_info = dict["info"]
        dict_info["u_id"] = dict["u_id"]
        time_s_p = time.time()
        player_id = input_data_o.input_player_data(dict_info=dict_info)
        time_e_p = time.time()
        print("Input Data in Player Table: " + str(time_e_p-time_s_p))
        draft_dict = dict["info"]["draft_info"]
        time_s_d = time.time()
        for draft in draft_dict:
            one_draft = draft_dict[draft]
            input_data_o.input_player_draft(player_id=player_id, draft_dict=one_draft)
        time_e_d = time.time()
        print("Input Data in Draft Table: " + str(time_e_d-time_s_d))
        dict_stats = dict["stats"]
        if dict_info["position"] == "G":
            is_goalie = True
        else:
            is_goalie=False
        time_s_s = time.time()
        self.input_stats_dict(player_id=player_id, stat_dict=dict_stats, is_goalie=is_goalie)
        time_s_e = time.time()
        print("Input Data in Stat Table: " + str(time_s_e-time_s_s))
        dict_achievements = dict["achievements"]
        time_s_a = time.time()
        self.input_achievements(dict_achievements=dict_achievements, player_id=player_id)
        time_s_e = time.time()
        print("Input Data in achievement Table: " + str(time_s_e-time_s_a))
        time_e = time.time()
        print("Input Data Database: " + str(time_e-time_s))

    def input_stats_dict(self, stat_dict, player_id, is_goalie):
        dict_info = {}
        dict_info["is_goalie"] = is_goalie
        dict_info["player_id"] = player_id
        for competititon_type in stat_dict:
            time_s = time.time()
            competititon_dict = stat_dict[competititon_type]
            self.input_competititon_type(dict_competititon_type=competititon_dict, dict_info=dict_info)
            time_e = time.time()
            print("Input Type in DB: "+ str(time_e-time_s))

    def input_competititon_type(self, dict_competititon_type, dict_info):
        for season_name in dict_competititon_type:
            time_s_s = time.time()
            season_dict = dict_competititon_type[season_name]
            dict_info["season_name"] = season_name
            self.input_season_dict(season_dict=season_dict, dict_info=dict_info)
            time_e_s = time.time()
            print("Input Season in DB: "+ str(time_e_s-time_s_s))
    
    def input_season_dict(self, season_dict, dict_info):
        for league_name in season_dict:
            time_s_l = time.time()
            dict_info["league_name"] = league_name
            league_dict = season_dict[league_name]
            self.input_league_dict(league_dict=league_dict, dict_info=dict_info)
            time_e_l = time.time()
            print("Input League in DB: "+ str(time_e_l-time_s_l))

    def input_league_dict(self, league_dict, dict_info):
        dict_info["league_uid"] = league_dict["league_id"]
        del league_dict["league_id"]
        del league_dict["url"]
        for team_name in league_dict:
            time_s_t = time.time()
            team_dict = league_dict[team_name]
            self.input_team_dict(team_dict=team_dict, dict_info=dict_info)
            time_e_t = time.time()
            print("Input Team in DB: "+ str(time_e_t-time_s_t))

    def input_team_dict(self, team_dict, dict_info):
        if "leadership" in team_dict:
            dict_info["leadership"] = team_dict["leadership"]
        else:
            dict_info["leadership"] = None
        dict_info["team_uid"] = team_dict["team_id"]
        del team_dict["url"]
        for season_type in ["play_off", "regular_season"]:
            if season_type == "play_off":
                dict_info["regular_season"] = False
            else:
                dict_info["regular_season"] = True
            season_data_dict = team_dict[season_type]
            input_data_o = input_data.InputData()
            t_s_e = time.time()
            input_data_o.input_player_stats_data(season_dict=season_data_dict, dict_info=dict_info)
            time_e_e = time.time()
            print("Input 1 entry in DB: " + str(time_e_e-t_s_e))
                    
    def input_achievements(self, dict_achievements, player_id):
        input_data_o = input_data.InputData()
        for season in dict_achievements:
            dict_achiev_season = dict_achievements[season]
            for achievement_name in dict_achiev_season:
                input_data_o.input_achievement_relation(achievement_name=achievement_name, season_name=season, player_id=player_id)


class InputTeamDict():

    def __init__(self):
        pass

    def input_team_dict(self, team_dict):
        input_data_o = input_data.InputData()
        gi_dict = team_dict["general_info"]
        stadium_dict = team_dict["stadium_info"]
        if set([value for value in stadium_dict.values() if type(value) is not dict]) != {None}:
            stadium_id = input_data_o.input_stadium_data(stadium_dict=stadium_dict)
        else:
            stadium_id = None
        gi_dict["stadium_id"] = stadium_id
        team_id = input_data_o.input_team_data(general_info_dict=gi_dict)
        affiliated_teams_dict = team_dict["affiliated_teams"]
        for u_id in affiliated_teams_dict:
            team_a_id = input_data_o.input_team_uid(u_id=u_id)
            input_data_o.input_affiliated_teams(main_team=team_id, affiliated_team=team_a_id)
        retired_numbers_dict = team_dict["retired_numbers"]
        for u_id in retired_numbers_dict:
            retired_number = retired_numbers_dict[u_id][0]
            player_id = input_data_o.input_player_uid(u_id=int(u_id))
            input_data_o.input_retired_number_data(player_id=player_id, team_id=team_id, 
                                                   number=retired_number)
        titles_dict = team_dict["titles"]
        for title in titles_dict:
            min = titles_dict[title]["min"]
            max = titles_dict[title]["max"]
            input_data_o.input_team_name(name=title, min=min, 
                                         max=max, team_id=team_id)
        colour_list = team_dict["colour_list"]
        for colour in colour_list:
            input_data_o.input_colour_team(team_id=team_id, colour=colour)

class InputLeagueDict():

    def __init__(self):
        pass

    def input_league_dict(self, league_dict):
        input_data_o = input_data.InputData()
        league_id = input_data_o.input_league_data(u_id=league_dict["u_id"], 
                                                   long_name=league_dict["long_name"])
        achiev_dict =  league_dict["achievements_names"]
        for achiev in achiev_dict:
            input_data_o.input_achievement(achievement_name=achiev, league_id=league_id)
        stat_dict = league_dict["season_tables"]
        self.input_league_standings_dict(stat_dict=stat_dict, league_id=league_id)

    def input_league_standings_dict(self, stat_dict, league_id):
        for season in stat_dict:
            row_dict = {}
            row_dict["season"] = season
            row_dict["league_id"] = league_id
            season_dict = stat_dict[season]
            self.input_season_dict(season_dict=season_dict, row_dict = row_dict)

    def input_season_dict(self, season_dict, row_dict):
        for type in season_dict:
            row_dict["type"] = type
            type_dict = season_dict[type]
            self.input_type_dict(type_dict=type_dict, row_dict=row_dict)
    
    def input_type_dict(self, type_dict, row_dict):
        for position in type_dict:
            row_dict["position"] = position
            position_dict = type_dict[position]
            self.input_position_dict(position_dict=position_dict, row_dict=row_dict)

    def input_position_dict(self, position_dict, row_dict):
        row_dict["team_id"]  = position_dict["u_id"]
        del position_dict["u_id"]
        del position_dict["url"]
        for stat in position_dict:
            row_dict[stat] = position_dict[stat]
        input_data_o = input_data.InputData()
        input_data_o.input_team_season_data(ts_dict=row_dict)
 
    

        
        

        






                    

                    
