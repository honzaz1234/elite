import hockeydata.database_creator.database_creator as db
from sqlalchemy import update
from hockeydata.constants import *


class DatabasePipeline():


    def __init__(self, db_session):
        self.db_session = db_session
        pass


    def input_data_in_player_table(self, dict_info):
        database_method = DatabaseMethods(db_session=self.db_session)
        query_object = Query(db_session=self.db_session)
        nr_team_id = database_method._input_uid(
            table=db.Team, uid_val=dict_info[NHL_RIGHTS_UID], 
            uid=dict_info[NHL_RIGHTS_UID], team=None, long_name=None, active=None, founded=None, place_id=None, stadium_id=None
            )
        place_dict = dict_info[PLACE_DICT]
        place_birth_id = database_method._input_unique_data(
            table=db.Place, country_s=place_dict[COUNTRY],
            place = place_dict[PLACE], region=place_dict[REGION])
        player_id = query_object._find_id_in_table(
            table=db.Player, uid=dict_info[PLAYER_UID])
        if player_id == None:
            player_id = database_method._input_data(
                table=db.Player, name=dict_info[PLAYER_NAME],
                uid=dict_info[PLAYER_UID], position=dict_info[POSITION],
                active=dict_info[ACTIVE], age=dict_info[AGE], 
                shoots=dict_info[SHOOTS], catches=dict_info[CATCHES], 
                contract=dict_info[CONTRACT_END], cap_hit=dict_info[CAP_HIT], 
                signed_nhl=dict_info[SIGNED_NHL], date_birth=dict_info[BIRTH_DATE], drafted=dict_info[DRAFTED], 
                height=dict_info[HEIGHT], weight=dict_info[WEIGHT], 
                nhl_rights_id=nr_team_id, place_birth_id=place_birth_id)
        else:
            database_method._update_data(
                table=db.Player, where_col=db.Player.uid,
                where_val=dict_info[PLAYER_UID],
                name=dict_info[PLAYER_NAME], uid=dict_info[PLAYER_UID], position=dict_info[POSITION], active=dict_info[ACTIVE], age=dict_info[AGE], shoots=dict_info[SHOOTS],
                catches=dict_info[CATCHES], contract=dict_info[CONTRACT_END], cap_hit=dict_info[CAP_HIT], signed_nhl=dict_info[SIGNED_NHL], date_birth=dict_info[BIRTH_DATE], drafted=dict_info[DRAFTED], 
                height=dict_info[HEIGHT], weight=dict_info[WEIGHT], 
                nhl_rights_id=nr_team_id, place_birth_id=place_birth_id)
        return player_id
    
    def input_data_in_team_table(self, dict_info, stadium_id):
        database_method = DatabaseMethods(db_session=self.db_session)
        query_object = Query(db_session=self.db_session)
        place_dict = dict_info[PLACE_DICT]
        if place_dict == None:
            place_id = None
        else:
            place_id = database_method._input_unique_data(
                table=db.Place, place=place_dict[PLACE],
                region=place_dict[REGION], 
                country_s=place_dict[COUNTRY])
        team_id = query_object._find_id_in_table(
            table=db.Team, uid=dict_info[TEAM_UID])
        if team_id == None:
            team_id = database_method._input_unique_data(
            table=db.Team, uid=dict_info[TEAM_UID],
            team=dict_info[SHORT_NAME],
            long_name=dict_info[LONG_NAME],
            active=dict_info[ACTIVE],
            place_id=place_id,
            founded=dict_info[YEAR_FOUNDED],
            stadium_id=stadium_id)
        else:
            database_method._update_data(
                table=db.Team,
                where_col=db.Team.uid,
                where_val = dict_info[TEAM_UID],
                uid=dict_info[TEAM_UID],
                team=dict_info[SHORT_NAME],
                long_name=dict_info[LONG_NAME],
                active=dict_info[ACTIVE],
                place_id=place_id,
                founded=dict_info[YEAR_FOUNDED],
                stadium_id=stadium_id)
        return team_id
    
    def _input_data_in_league_table(self, league_uid, long_name):
        query_object = Query(db_session=self.db_session)
        database_method = DatabaseMethods(db_session=self.db_session)
        league_id = query_object._find_id_in_table(
            table=db.League, league_uid=league_uid)
        if league_id is None:
            league_id = database_method._input_unique_data(
                long_name=long_name, league_uid=league_uid)
        else:
            database_method._update_data(
                table=db.League, where_col=db.League.uid, where_val=league_uid,
                long_name=long_name)
        return league_id
    
    def _input_achievement(self, achiev, league_id):
        query_object = Query(db_session=self.db_session)
        database_method = DatabaseMethods(db_session=self.db_session)
        achiev_id = query_object._find_id_in_table(
            table=db.Achievement, achievement=achiev)
        if achiev_id is None:
            database_method._input_unique_data(
                table=db.Achievement, achievement=achiev,
                league_id=league_id)
        else:
            database_method._update_data(
                table=db.Achievement, where_col=db.Achievement.uid, 
                where_val=achiev, league_id=league_id)
        return achiev_id


    def _input_achievement_relation(self, player_id, achiev, season):
        database_method = DatabaseMethods(db_session=self.db_session)
        achiev_id = database_method._input_uid(
            table=db.Achievement, uid_val=achiev, uid=achiev, league_id=None)
        season_id = database_method._input_unique_data(
            table=db.Season, season=season)
        relation_id = database_method._input_unique_data(
            table=db.PlayerAchievement, season_id=season_id,
            achievement_id=achiev_id, player_id=player_id)
        return relation_id
    

    def _input_player_stats(self, dict_stats):
        database_method = DatabaseMethods(db_session=self.db_session)
        team_id = database_method._input_uid(
            table=db.Team, uid_val=dict_stats[TEAM_UID], 
            uid=dict_stats[TEAM_UID], team=None, long_name=None, active=None, founded=None, place_id=None, stadium_id=None
            )
        league_id = database_method._input_uid(
            table=db.League, uid_val=dict_stats[LEAGUE_UID], league=None,
            uid=dict_stats[LEAGUE_UID]
            )
        season_id = database_method._input_unique_data(
            table=db.Season, season=dict_stats[SEASON_NAME]
            )
        stat_id = database_method._input_unique_data
        if dict_stats[IS_GOALIE] == False:
            stat_id = database_method._input_unique_data(
                table=db.PlayerStats,
                player_id=dict_stats[PLAYER_ID],
                regular_season=dict_stats[REGULAR_SEASON],
                season_id=season_id,
                league_id=league_id,
                team_id=team_id,
                captaincy=dict_stats[LEADERSHIP],
                games_played=dict_stats[GP],
                goals=dict_stats[G],
                assists=dict_stats[A],
                total_points=dict_stats[TOTAL_POINTS],
                PM=dict_stats[PIM],
                plus_minus=dict_stats[PLUS_MINUS]
                )
        else:
            stat_id = database_method._input_unique_data(
                table=db.GoalieStats,
                player_id=dict_stats[PLAYER_ID],
                regular_season=dict_stats[REGULAR_SEASON],
                season_id=season_id,
                league_id=league_id,
                team_id=team_id,
                captaincy=dict_stats[LEADERSHIP],
                games_played=dict_stats[GP], 
                gd=dict_stats[GD],
                goal_against_average=dict_stats[GAA], 
                save_percentage=dict_stats[SVP], 
                goal_against=dict_stats[GA],
                shot_saved=dict_stats[SVS], 
                shotouts=dict_stats[SO],
                wins=dict_stats[W], 
                looses=dict_stats[L],
                ties=dict_stats[T], 
                toi=dict_stats[TOI]
                )
            return stat_id
    
    def _input_stadium_data(self, stadium_dict):
        database_method = DatabaseMethods(db_session=self.db_session)
        if stadium_dict[ARENA_NAME] is None:
            return None
        dict_place = stadium_dict[PLACE_DICT]
        place_id = database_method._input_unique_data(
            table=db.Place, 
            place=dict_place[PLACE],
            region=dict_place[REGION],
            country_s=dict_place[COUNTRY]
            )
        stadium_id = database_method._input_unique_data(
            table=db.Stadium, 
            stadium=stadium_dict[ARENA_NAME],
            capacity=stadium_dict[CAPACITY],
            construction_year=stadium_dict[CONSTRUCTION_YEAR],
            place_id=place_id
            )
        return stadium_id

    def _input_affiliated_teams(self, team_id, team_aff_uid):
        database_method = DatabaseMethods(db_session=self.db_session)
        if team_id is None or team_aff_uid is None:
            return None
        team_aff_id = database_method._input_uid(
            table=db.Team, uid_val=team_aff_uid, uid=team_aff_uid, team=None, long_name=None, active=None, founded=None, place_id=None, stadium_id=None)
        query =  Query(db_session=self.db_session)
        relation_id = query._find_id_in_table(
            table=db.AffiliatedTeam, 
            team_1_id=team_id,
            team_2_id=team_aff_id)
        if relation_id is not None:
            return relation_id
        relation_id = query._find_id_in_table(
            table=db.AffiliatedTeam, 
            team_1_id=team_aff_id,
            team_2_id=team_id)
        if relation_id is not None:
            return relation_id
        relation_id = database_method._input_unique_data(
            table=db.AffiliatedTeam, 
            team_1_id=team_id,
            team_2_id=team_aff_id)
        return relation_id
    
    def _input_colour_team(self, team_id, colour):
        if team_id is None or colour is None:
            return None
        database_method = DatabaseMethods(db_session=self.db_session)
        colour_id = database_method._input_unique_data(
            table=db.Colour, colour_name=colour
            )
        relation_id = database_method._input_unique_data(
            table=db.TeamColour,
            team_id=team_id, colour_id=colour_id
            )
        return relation_id
    
    def _input_player_draft(self, draft_dict, player_id):
        if player_id is None:
            return None
        database_method = DatabaseMethods(db_session=self.db_session)
        team_id = database_method._input_uid(
            table=db.Team, uid_val=draft_dict[TEAM_UID], 
            uid=draft_dict[TEAM_UID], team=None, long_name=None,
            active=None, place_id=None, founded=None, stadium_id=None
            )
        draft_id = database_method._input_unique_data(
            table=db.PlayerDraft,
            player_id=player_id,
            team_id=team_id,
            draft_round=draft_dict[DRAFT_ROUND],
            draft_year=draft_dict[DRAFT_YEAR],
            draft_position=draft_dict[DRAFT_POSITION]
            )
        return draft_id
    
    def _input_player_nation(self, player_id, nationality):
        database_method = DatabaseMethods(db_session=self.db_session)
        nation_id = database_method._input_unique_data(
            table=db.Nationality,
            nationality=nationality)
        relation_id=database_method._input_unique_data(
            table=db.PlayerNationality,
            player_id=player_id,
            nationality_id=nation_id)
        return relation_id
    
    def _input_player_relation(self, player_from_uid, player_to_id, relation):
        database_method = DatabaseMethods(db_session=self.db_session)
        player_from_id = database_method._input_uid(
            table=db.Player, uid_val=player_from_uid, name=None, uid=player_from_uid, position=None, active=None, age=None, shoots=None, catches=None, contract=None, cap_hit=None, signed_nhl=None, date_birth=None, drafted=None, 
            height=None, weight=None, nhl_rights_id=None, place_birth_id=None
            )
        relation_id=database_method._input_unique_data(
            table=db.Relation,
            relation=relation)
        table_relation_id = database_method._input_unique_data(
            table=db.PlayerRelation, player_from_id=player_from_id,
            player_to_id=player_to_id, relation_id=relation_id 
        )
        return table_relation_id
    
    def _input_retired_number_relation(self, team_id, player_uid, number):
        database_method = DatabaseMethods(db_session=self.db_session)
        player_id = database_method._input_uid(
            table=db.Player, uid_val=player_uid, name=None, uid=player_uid, position=None, active=None, age=None, shoots=None, catches=None, contract=None, cap_hit=None, signed_nhl=None, date_birth=None, drafted=None, height=None, weight=None, nhl_rights_id=None, place_birth_id=None 
            )
        relation_id = database_method._input_unique_data(
            table=db.RetiredNumber, team_id=team_id, 
            player_id=player_id, number=number)
        return relation_id
    

    def _input_team_name(self, name, min, max, team_id):
        database_method = DatabaseMethods(db_session=self.db_session)
        teamname_id = database_method._input_unique_data(
            table=db.TeamName, team_name=name, year_from=min, year_to=max, 
            team_id=team_id)
        return teamname_id
                                                         


class DatabaseMethods():

    def __init__(self, db_session):
        self.db_session = db_session
        pass

    def _input_data(self, table, **kwargs):
        query_object = Query(db_session=self.db_session)
        query_insert = query_object._create_table_entry(
                table=table, **kwargs)
        self.db_session.add(query_insert)
        self.db_session.commit()
        id = query_insert.id
        return id
    
    def _input_unique_data(self, table, **kwargs):
        query_object = Query(db_session=self.db_session)
        id = query_object._find_id_in_table(table=table, **kwargs)
        if id is None:
            id = self._input_data(table=table, **kwargs)
        return id
    

    def _update_data(self, table, where_col, where_val, **kwargs):
        query_object = Query(db_session=self.db_session)
        update_query = query_object._update_entry(
            table=table, where_col=where_col, where_val=where_val, **kwargs)
        self.db_session.execute(update_query)
        self.db_session.commit()

    def _input_uid(self, table, uid_val, **kwargs):
        query_object = Query(db_session=self.db_session)
        id = query_object._find_id_in_table(table=table, uid=uid_val)
        if id is None:
            id = self._input_unique_data(table=table, **kwargs)
        return id
        


class Query():


    def __init__(self, db_session):
        self.db_session = db_session
        

    def _create_table_entry(self, table, **kwargs):
        entry = table(**kwargs)
        return entry
    
    def _find_id_in_table(self, table, **kwargs):
        row_data = self.db_session.query(table.id).filter_by(**kwargs).first()
        if row_data is None:
            return None
        else: 
            return row_data.id
        
    def _update_entry(self, table, where_col, where_val, **kwargs):
        update_query = (update(table)
                       .where(where_col == where_val)
                       .values(**kwargs))
        return update_query

