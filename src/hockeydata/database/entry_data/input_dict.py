import database.entry_data.input_data.input_data as input_data
import time

from constants import *

class InputPlayerDict():

    def __init__(self, is_goalie):
        self.is_goalie = is_goalie
        pass

    def input_player_dict(self, player_dict):
        player_id = self.input_player_info_dict(
            info_dict=player_dict[GENERAL_INFO])
        self.input_relation_dict(info_dict=player_dict[RELATIONS],
                                 player_id=player_id)
        self.input_stats_dict(stat_dict=player_dict[SEASON_STATS],
                              player_id=player_id)
        self.input_achievement_dict(achiev_dict=player_dict[ACHIEVEMENTS],
                                    player_id=player_id)

    def input_player_info_dict(self, info_dict):
        player_info = InputPlayerInfo()
        player_id = player_info.input_player(
            info_dict=info_dict)
        player_info.input_draft_dict(draft_dict=info_dict[DRAFTS])
        player_info.input_nationalities(nation_list=info_dict[NATIONALITY])
        return player_id


    def input_relation_dict(self, relation_dict, player_id):
        relation_info = InputRelationDict()
        relation_info.input_relation_dict(
            relation_dict=relation_dict, player_id=player_id)
        
    def input_stats_dict(self, stat_dict, player_id):
        stats_info = InputStatsDict()
        stats_info.input_stats_dict(stat_dict=stat_dict, 
                                    player_id=player_id,
                                    is_goalie=self.is_goalie)


    def input_achievement_dict(self, achiev_dict, player_id):
        achiev_info = InputAchievementDict()
        achiev_info.input_achievements(
            dict_achievements=achiev_dict, player_id=player_id)
        
class InputPlayerInfo():


    def __init__(self):
        self.input_data = input_data.InputData()
        pass

    def input_player(self, info_dict):
        player_id = self.input_data.input_player_data(dict_info=info_dict)
        return player_id

    def input_draft_dict(self, draft_dict, player_id):
        for draft in draft_dict:
            one_draft = draft_dict[draft]
            self.input_data.input_player_draft(player_id=player_id, draft_dict=one_draft)

    def input_nationalities(self, nation_list, player_id):
        for nation in nation_list:
            self.input_data.input_player_nation(player_id=player_id, nation=nation)


class InputRelationDict():

    def __init__(self):
        self.input_data = input_data.InputData()
        pass

    def input_relation_dict(self, relation_dict, player_id):
        for relation in relation_dict:
            relation_list = relation_dict[relation]
            for u_id in relation_list:
                self.input_data.input_player_relation(player_from_uid=u_id, player_to_id=player_id, relation=relation)


class InputStatsDict():

    def __init__(self):
        self.input_data = input_data.InputData()
        pass

    def input_stats_dict(self, stat_dict, player_id, is_goalie):
        dict_info = {}
        dict_info[IS_GOALIE] = is_goalie
        dict_info[PLAYER_ID] = player_id
        for competititon_type in stat_dict:
            competititon_dict = stat_dict[competititon_type]
            self.input_competititon_type(
                dict_competititon_type=competititon_dict, dict_info=dict_info)

    def input_competititon_type(self, dict_competititon_type, dict_info):
        for season_name in dict_competititon_type:
            season_dict = dict_competititon_type[season_name]
            dict_info[SEASON_NAME] = season_name
            self.input_season_dict(season_dict=season_dict, dict_info=dict_info)
    
    def input_season_dict(self, season_dict, dict_info):
        for league_name in season_dict:
            dict_info["league_name"] = league_name
            league_dict = season_dict[league_name]
            self.input_league_dict(league_dict=league_dict, dict_info=dict_info)

    def input_league_dict(self, league_dict, dict_info):
        dict_info[LEAGUE_UID] = league_dict[LEAGUE_UID]
        del league_dict[LEAGUE_UID]
        del league_dict[LEAGUE_URL]
        for team_name in league_dict:
            team_dict = league_dict[team_name]
            self.input_team_dict(team_dict=team_dict, dict_info=dict_info)

    def input_team_dict(self, team_dict, dict_info):
        dict_info[TEAM_UID] = team_dict[TEAM_UID]
        del team_dict[TEAM_URL]
        for season_type in [PLAY_OFF, REGULAR_SEASON]:
            if season_type == PLAY_OFF:
                dict_info[REGULAR_SEASON] = False
            else:
                dict_info[REGULAR_SEASON] = True
            season_data_dict = team_dict[season_type]
            self.input_data.input_player_stats_data(
                season_dict=season_data_dict, dict_info=dict_info)

class InputAchievementDict():

    def __init__(self):
        self.input_data = input_data.InputData()
        pass

    def input_achievements(self, dict_achievements, player_id):
        for season in dict_achievements:
            dict_achiev_season = dict_achievements[season]
            for achievement_name in dict_achiev_season:
                self.input_data.input_achievement_relation(
                    achievement_name=achievement_name, season_name=season, player_id=player_id)
                    
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
 
    

        
        

        






                    

                    
