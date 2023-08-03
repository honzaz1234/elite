import update_dict.sections.player_info as player_info
import update_dict.sections.player_stats as player_stats
import update_dict.sections.league_info as league_info


class UpdateDictWraper():

    def __init__(self):
        pass

    def check_goalie(self, dict):
        position = dict["Info"]["Position"]
        if position == "G":
            return True
        else:
            return False

    def update_player_dict(self, dict):
        is_goalie = self.check_goalie(dict)
        info_updater = player_info.UpdatePlayerInfo(is_goalie=is_goalie)
        dict_info = dict["Info"]
        dict["Info"] = info_updater.update_info_wraper(dict_info)
        stats_updater = player_stats.UpdatePlayerStats(is_goalie=is_goalie)
        dict_stats = dict["Stats"]
        dict["Stats"] = stats_updater.update_stats_wraper(dict_stats)
        return dict
    
    def update_league_dict(self, dict):
        league_update = league_info.UpdateLeagueDict()
        dict["season_tables"] = league_update._update_standing_dict(dict["season_tables"])
        return dict





    

