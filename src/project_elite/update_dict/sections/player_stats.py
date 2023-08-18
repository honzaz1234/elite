import re

class UpdatePlayerStats:
    
    def __init__(self, is_goalie):
        self.is_goalie = is_goalie

    def update_stats_dict(self, dict_stats):
        for competition_type in list(dict_stats.keys()):
            comptetition_dict = dict_stats[competition_type]
            new_competition_dict = self.update_competition_dict(competition_dict=comptetition_dict)
            dict_stats[competition_type] = new_competition_dict
        return dict_stats

    def update_competition_dict(self, competition_dict):
        for year_key in list(competition_dict.keys()):
            year_dict = competition_dict[year_key]
            year_dict_new = self.update_year_dict(year_dict=year_dict)
            competition_dict[year_key] = year_dict_new
        return competition_dict

    def update_year_dict(self, year_dict):
        for league_key in list(year_dict.keys()):
            league_dict = year_dict[league_key]
            new_league_dict = self.update_league_dict(league_dict=league_dict)
            year_dict[league_key] = new_league_dict
        return year_dict
    
    def update_league_dict(self, league_dict):
        if league_dict["url"] is not None:
            league_id = re.findall("league\/(.+)$", league_dict["url"])[0]
        else:
            league_id = None                                               
        league_dict["league_id"] = league_id
        for team_key in list(league_dict.keys()):
            if team_key not in ["url", "league_id"]:
                team_dict = league_dict[team_key]
                new_team_dict = self.update_team_dict(team_dict=team_dict)
                league_dict[team_key] = new_team_dict
        return league_dict
    
    def update_team_dict(self, team_dict):
        team_id = re.findall("team\/([0-9]+)\/", team_dict["url"])[0]
        team_dict["team_id"] = int(team_id)
        if "leadership" in team_dict:
            team_dict["leadership"] = self.update_leadership(team_dict["leadership"])
        for season_type in ["regular_season", "play_off"]:
            if season_type not in team_dict:
                continue
            list_season = team_dict[season_type]
            season_dict = SeasonDict()
            if self.is_goalie == False:
                stat_dict = season_dict.update_season_player(list_season)
            else:
                stat_dict = season_dict.update_season_goalkeeper(list_season)
            team_dict[season_type] = stat_dict
        return team_dict
    
    def update_leadership(self, lead_value):
        new_lead_value = re.findall("[AC]", lead_value)[0]
        return new_lead_value
    

class SeasonDict():

    player_attributes = ["gp", "g", "a", "tp", "PIM", "plus_minus"]
    goalie_attributes = ["gp", "gd", "gaa", "svp", "ga", "svs", "so", "wlt", "toi"]

    def  __init__(self):
        pass

    def update_season_goalkeeper(self, season_list):
        dict_stats = {}
        if set(season_list) == {"-"} or set(season_list) == {""} or set(season_list)== {"-", ""} or set(season_list) == set():
            season_list = [None] * len(SeasonDict.goalie_attributes)
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
                dict_stats[SeasonDict.goalie_attributes[ind]] = season_list[ind]
            elif ind in [2,3]:
                stat = float(season_list[ind])
                dict_stats[SeasonDict.goalie_attributes[ind]] = stat
            else:
                stat = re.sub(" ", "", season_list[ind])
                stat = int(stat)
                dict_stats[SeasonDict.goalie_attributes[ind]] = stat
        return dict_stats
    
    def update_season_player(self, season_list):
        dict_stats = {}
        if set(season_list) == {"-"} or set(season_list) == {""} or set(season_list)== {"-", ""} or set(season_list) == set():
            season_list = [None] * len(SeasonDict.player_attributes)
        for ind in range(len(season_list)):
            if season_list[ind] == "-" or season_list[ind] is None:
                stat = None
            else:
                stat = re.sub(" ", "", season_list[ind])
                stat = int(stat)
            dict_stats[SeasonDict.player_attributes[ind]] = stat
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

  

        

