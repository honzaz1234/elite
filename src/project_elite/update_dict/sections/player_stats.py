import re

class UpdatePlayerStats:
    
    def __init__(self, is_goalie):
        self.is_goalie = is_goalie

    def update_stats_wraper(self, dict_stats):
        for competition_type in dict_stats:
            for year_key in dict_stats[competition_type]:
                for league_key in dict_stats[competition_type][year_key]:
                    for team_key in dict_stats[competition_type][year_key][league_key]:
                        if team_key == "url":
                            continue
                        for type_key in ["regular_season", "play_off"]:
                            if type_key not in dict_stats[competition_type][year_key][league_key][team_key]:
                                continue
                            list_season = dict_stats[competition_type][year_key][league_key][team_key][type_key]
                            if self.is_goalie == False:
                                stat_dict = self.update_season_player(list_season)
                            else:
                                stat_dict = self.update_season_goalkeeper(list_season)
                            dict_stats[competition_type][year_key][league_key][team_key][type_key] = stat_dict   
                        if "leadership" in dict_stats[competition_type][year_key][league_key][team_key]:
                            dict_stats[competition_type][year_key][league_key][team_key]["leadership"] = self.update_leadership(dict_stats[competition_type][year_key][league_key][team_key]["leadership"])
                        else:
                            dict_stats[competition_type][year_key][league_key][team_key]["leadership"] = None
        return dict_stats

    def update_season_goalkeeper(self, season_list):
        list_stat_names = ["gp", "gd", "gaa", "svp", "ga", "svs", "so", "wlt", "toi"]
        dict_stats = {}
        if set(season_list) == {"-"} or set(season_list) == {""} or set(season_list)== {"-", ""} or set(season_list) == set():
            season_list = [None] * len(list_stat_names)
        else:
            for ind in range(len(season_list)):
                season_list[ind] = season_list[ind].replace(" ", "")
                if season_list[ind] in ["-", ""]:
                    season_list[ind] = None
        for ind in range(len(season_list)):
            if ind == 7:
                dic_wlt = self._win_looses_ties_to_dict(season_list[ind])
                dict_stats = {**dict_stats, **dic_wlt}
            elif season_list[ind] == None:
                dict_stats[list_stat_names[ind]] = season_list[ind]
            elif ind in [2,3]:
                stat = float(season_list[ind])
                dict_stats[list_stat_names[ind]] = stat
            else:
                stat = re.sub(" ", "", season_list[ind])
                stat = int(stat)
                dict_stats[list_stat_names[ind]] = stat
        return dict_stats
    
    def update_season_player(self, season_list):
        list_stat_names = ["gp", "g", "a", "tp", "PIM", "plus_minus"]
        dict_stats = {}
        if set(season_list) == {"-"} or set(season_list) == {""} or set(season_list)== {"-", ""} or set(season_list) == set():
            season_list = [None] * len(list_stat_names)
        for ind in range(len(season_list)):
            if season_list[ind] == "-" or season_list[ind] is None:
                stat = None
            else:
                stat = re.sub(" ", "", season_list[ind])
                stat = int(stat)
            dict_stats[list_stat_names[ind]] = stat
        return dict_stats 

    def _win_looses_ties_to_dict(self, stat_string):
        if stat_string == "-" or stat_string is None:
            return {"w": None, "l": None, "t": None}
        dic_stat = {}
        stat_names = ["w", "l", "t"]
        stat_list = stat_string.split("-")
        for ind in range(len(stat_names)):
            dic_stat[stat_names[ind]] = int(stat_list[ind])
        return dic_stat

    def update_leadership(self, lead_value):
        new_lead_value = re.findall("[AC]", lead_value)[0]
        return new_lead_value
  

        

