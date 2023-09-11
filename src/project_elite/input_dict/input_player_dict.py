import insert_db.insert_db as insert_db
import database.create_database.database_creator as db
from constants import *

class InputPlayerDict():
    """class containing wraper methods for uploading player dictionary into db
    """


    def __init__(self):
        self.is_goalie = None
        pass

    def set_is_goalie(self, dict):

        """method for establishing if the player is goalie or field player; important because of different statistical categories
        """

        position = dict[GENERAL_INFO][POSITION]
        if position == "G":
            self.is_goalie =  True
        else:
            self.is_goalie = False

    def input_player_dict(self, player_dict):
        """wraper method for inputing player dict into database"""

        self.set_is_goalie(dict=player_dict)
        player_id = self._input_player_info_dict(
            info_dict=player_dict[GENERAL_INFO])
        self._input_relation_dict(info_dict=player_dict[RELATIONS],
                                 player_id=player_id)
        self._input_stats_dict(stat_dict=player_dict[SEASON_STATS],
                              player_id=player_id)
        self._input_achievement_dict(achiev_dict=player_dict[ACHIEVEMENTS],
                                    player_id=player_id)

    def _input_player_info_dict(self, info_dict):
        """method for inserting general info dict into database"""

        player_info = InputPlayerInfo()
        player_id = player_info._input_player(
            info_dict=info_dict)
        player_info._input_draft_dict(draft_dict=info_dict[DRAFTS])
        player_info._input_nationalities(nation_list=info_dict[NATIONALITY])
        return player_id

    def _input_relation_dict(self, relation_dict, player_id):
        """wraper method for upploading relation dict of a player into database
        """

        relation_info = InputRelationDict()
        relation_info._input_relation_dict(
            relation_dict=relation_dict, player_id=player_id)
        
    def _input_stats_dict(self, stat_dict, player_id):
        """wraper method for uploading player stats into database"""

        stats_info = InputStatsDict()
        stats_info._input_stats_dict(stat_dict=stat_dict, 
                                    player_id=player_id,
                                    is_goalie=self.is_goalie)


    def _input_achievement_dict(self, achiev_dict, player_id):
        """wraper method for uploading player achievements into database"""

        achiev_info = InputAchievementDict()
        achiev_info._input_achievements(
            dict_achievements=achiev_dict, player_id=player_id)
        
class InputPlayerInfo():

    """class with methods for uploading information from player info dictionary into db
    """

    def __init__(self):
        self.insert_db = insert_db.DatabasPipeline(db_Session=db.session)
        pass

    def _input_player(self, info_dict):
        """method for puting general info into player DB and the related tables
        """

        player_id = self.insert_db.input_data_in_player_table(
            dict_info=info_dict)
        return player_id

    def _input_draft_dict(self, draft_dict, player_id):
        """method for putting player NHL draft information into table"""

        for draft in draft_dict:
            one_draft = draft_dict[draft]
            self.insert_db._input_player_draft(
                player_id=player_id, draft_dict=one_draft)

    def _input_nationalities(self, nation_list, player_id):
        """method for puting relation between player and his nationalites into DB
        """

        for nation in nation_list:
            self.insert_db._input_player_nation(
                player_id=player_id, nation=nation)


class InputRelationDict():

    """class with methods for uploading relation between player  and other players realted to him into DB
    """

    def __init__(self):
        self.insert_db = insert_db.DatabasPipeline(db_session=db.session)
        pass

    def _input_relation_dict(self, relation_dict, player_id):
        """method for uploading all player relation types into DB"""

        for relation in relation_dict:
            uid_list = relation_dict[relation]
            self._input_relation_type(player_id=player_id,
                                      type_=relation,
                                      list_uid=uid_list)

    def _input_relation_type(self, player_id, type_, list_uid):
            """method for uploading relations of one type into DB"""

            for u_id in list_uid:
                self.insert_db._input_player_relation(
                    player_from_uid=u_id, player_to_id=player_id, relation=type_)

class InputStatsDict():

    """class with methods for uploading information from player season stats dictionary into db
    """

    def __init__(self):
        self.insert_db = insert_db.DatabasPipeline()
        pass

    def _input_stats_dict(self, stat_dict, player_id, is_goalie):
        """method for uploading dict with seasonal stat data of player into DB
        """

        dict_info = {}
        dict_info[IS_GOALIE] = is_goalie
        dict_info[PLAYER_ID] = player_id
        for competititon_type in stat_dict:
            competititon_dict = stat_dict[competititon_type]
            self._input_competititon_type(
                dict_competititon_type=competititon_dict, dict_info=dict_info)

    def _input_competititon_type(self, dict_competititon_type, dict_info):
        """method for uploading dict from one type of table (league/tournament) into DB
        """

        for season_name in dict_competititon_type:
            season_dict = dict_competititon_type[season_name]
            dict_info[SEASON_NAME] = season_name
            self._input_season_dict(season_dict=season_dict, dict_info=dict_info)
    
    def _input_season_dict(self, season_dict, dict_info):
        """method for uploading dict of stats from one season into DB"""

        for league_name in season_dict:
            dict_info[LEAGUE_NAME] = league_name
            league_dict = season_dict[league_name]
            self._input_league_dict(league_dict=league_dict, dict_info=dict_info)

    def _input_league_dict(self, league_dict, dict_info):
        """method for uploading dict of stats from one season and one league into DB
        """

        dict_info[LEAGUE_UID] = league_dict[LEAGUE_UID]
        del league_dict[LEAGUE_UID]
        del league_dict[LEAGUE_URL]
        for team_name in league_dict:
            team_dict = league_dict[team_name]
            self._input_team_dict(team_dict=team_dict, dict_info=dict_info)

    def _input_team_dict(self, team_dict, dict_info):
        """method for uploading dict of stat data from one season one league and one team (one row of table) into DB
        """

        dict_info[TEAM_UID] = team_dict[TEAM_UID]
        del team_dict[TEAM_URL]
        for season_type in [PLAY_OFF, REGULAR_SEASON]:
            if season_type == PLAY_OFF:
                dict_info[REGULAR_SEASON] = False
            else:
                dict_info[REGULAR_SEASON] = True
            season_data_dict = team_dict[season_type]
            self.insert_db._input_player_stats(
                season_dict=season_data_dict)

class InputAchievementDict():

    """class with methods for uploading information from player achievements dictionary into db
    """

    def __init__(self):
        self.insert_db = insert_db.DatabasPipeline(db_session=db.session)
        pass

    def _input_achievements(self, dict_achievements, player_id):
        """method for uploading player achievements from all seasons into DB"""

        for season in dict_achievements:
            season_dict = dict_achievements[season]
            self._input_achievement_season(season_dict=season_dict,
                                            player_id=player_id,
                                            season=season)
                
    def _input_achievement_season(self, season_dict, season, player_id):
        """method for uploading achievements from one season into DB"""
        
        for achiev_name in season_dict:
                self.insert_db._input_achievement_relation(
                    achievement_name=achiev_name, season_name=season, player_id=player_id)

                