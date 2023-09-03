import update_dict.sections.player_info as player_info
import update_dict.sections.player_stats as player_stats
import update_dict.sections.league_info as league_info
import time


class UpdateDictWraper():

    def __init__(self):
        pass

    def check_goalie(self, dict):
        position = dict["info"]["Position"]
        if position == "G":
            return True
        else:
            return False

    def update_player_dict(self, dict):
        time_s = time.time()
        is_goalie = self.check_goalie(dict)
        info_updater = player_info.UpdatePlayerInfo(is_goalie=is_goalie)
        dict_info = dict["info"]
        dict["info"] = info_updater.update_info_dict(dict_info)
        stats_updater = player_stats.UpdatePlayerStats(is_goalie=is_goalie)
        dict_stats = dict["stats"]
        dict["stats"] = stats_updater.update_stats_dict(dict_stats)
        dict["u_id"] = int(dict["u_id"])
        time_e = time.time()
        print("Update Player Dict Duration: " + str(time_e - time_s))
        return dict

    def update_league_dict(self, dict):
        league_update = league_info.UpdateLeagueDict()
        dict["season_tables"] = league_update._update_standing_dict(
            dict["season_tables"])
        return dict
