import database.entry_data.input_data.input_data as input_data

class InputPlayerDict():

    def __init__(self):
        pass

    def input_player_dict(self, dict):
        input_data_o = input_data.InputData()
        dict_info = dict["info"]
        player_id = input_data_o.input_player_data(dict_info=dict_info)
        dict_stats = dict["stats"]
        if dict_info["position"] == "G":
            is_goalie = True
        else:
            is_goalie=False
        self.input_stats_dict(player_id=player_id, dict_stats=dict_stats, is_goalie=is_goalie)
        dict_achievements = dict["Achievements"]
        self.input_achievements(dict_achievements=dict_achievements, player_id=player_id)

    def input_stats_dict(self, stat_dict, player_id, is_goalie):
        dict_info = {}
        dict_info["is_goalie"] = is_goalie
        dict_info["player_id"] = player_id
        for competititon_type in stat_dict:
            competititon_dict = stat_dict[competititon_type]
            self.input_competititon_type(dict_competititon_type=competititon_dict, dict_info=dict_info)

    def input_competititon_type(self, dict_competititon_type, dict_info):
        for season_name in dict_competititon_type:
            season_dict = dict_competititon_type[season_name]
            dict_info["season_name"] = season_name
            self.input_season_dict(season_dict=season_dict, dict_info=dict_info)
    
    def input_season_dict(self, season_dict, dict_info):
        for league_name in season_dict:
            dict_info["league_name"] = league_name
            league_dict = season_dict[league_dict]
            self.input_league_dict(league_dict=league_dict, dict_info=dict_info)

    def input_league_dict(self, league_dict, dict_info):
        dict_info["league_id"] = league_dict["league_id"]
        del league_dict["league_id"]
        for team_name in league_dict:
            dict_info["team_name"] = team_name
            team_dict = league_dict[team_name]
            self.input_team_dict(team_dict=team_dict, dict_info=dict_info)

    def input_team_dict(self, team_dict, dict_info):
        dict_info["leadership"] = team_dict["leadership"]
        dict_info["team_id"] = team_dict["team_id"]
        dict_info["team_name"] = team_dict["team_name"]
        for season_type in ["play_off", "regular_season"]:
            if season_type == "play_off":
                dict_info["regular_season"] = False
            else:
                dict_info["regular_season"] = True
            season_data_dict = team_dict[season_type]
            input_data_o = input_data.InputData()
            input_data_o.input_player_stats_data(season_dict=season_data_dict, dict_info=dict_info)

    def input_stats_2(self, dict_stats, player_id, is_goalie):
        input_data_o = input_data.InputData()
        dict_info={}
        dict_info["is_goalie"] = is_goalie
        dict_info["player_id"] = player_id
        for competetition_type in dict_stats:
            for season_name in dict_stats[competetition_type]:
                dict_info["season_name"] = season_name
                season_dict = dict_stats[competetition_type][season_name]
                for league_name in season_dict:
                    dict_info["league_name"] = league_name
                    league_dict = dict_stats[competetition_type][season_name][league_name]
                    for team_name in league_dict:
                        dict_info["team_name"] = team_name
                        team_dict = league_dict[team_name]
                        dict_info["leadership"] = team_dict["leadership"]
                        del team_dict["leadership"]
                        for season_type in team_dict:
                            if season_type == "play_off":
                                dict_info["regular_season"] = False
                            else:
                                dict_info["regular_season"] = True
                            season_data_dict = team_dict[season_type]
                            season_id = input_data_o.input_player_stats_data(season_dict=season_data_dict, dict_info=dict_info)
                    
    def input_achievements(self, dict_achievements, player_id):
        input_data_o = input_data.InputData()
        for season in dict_achievements:
            dict_achiev_season = dict_achievements[season]
            for achievement_name in dict_achiev_season:
                achievement_player_id = input_data_o.input_achievement_relation(achievement_name=achievement_name, season_name=season, player_id=player_id)



class InputTeamDict():


    def __init__(self):
        pass

    def input_team_dict(self, team_dict):
        input_data_o = input_data.InputData()
        gi_dict = team_dict["general_info"]
        if set(stadium_dict.values()) != {None}:
            stadium_id = input_data_o.input_stadium_data(stadium_dict=stadium_dict)
        else:
            stadium_id = None
        gi_dict["stadium_id"] = stadium_id
        team_id = input_data_o.input_team(general_info_dict=gi_dict)
        stadium_dict = team_dict["stadium_info"]
        affiliated_teams_dict = team_dict["affiliated_teams"]
        for u_id in affiliated_teams_dict:
            team_a_id = input_data_o.input_team()
            input_data_o.input_affiliated_teams(team_id=team_id, team_affiliated_id=team_a_id)
        retired_numbers_dict = team_dict["retired_numbers"]
        for u_id in retired_numbers_dict:
            player_id = input_data_o.input_player()
            input_data_o.input_retired_number()

        






                    

                    
