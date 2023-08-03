import database.entry_data.input_data.input_data as input_data

class InputDict():

    def __init__(self):
        pass

    def input_dict(self, dict):
        input_data_o = input_data.InputData()
        dict_info = dict["Info"]
        player_id = input_data_o.input_player_data(dict_info=dict_info)
        dict_stats = dict["Stats"]
        if dict_info["position"] == "G":
            is_goalie = True
        else:
            is_goalie=False
        self.input_stats(player_id=player_id, dict_stats=dict_stats, is_goalie=is_goalie)
        dict_achievements = dict["Achievements"]
        self.input_achievements(dict_achievements=dict_achievements, player_id=player_id)

    def input_stats(self, dict_stats, player_id, is_goalie):
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

                    

                    
