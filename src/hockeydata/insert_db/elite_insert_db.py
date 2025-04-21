import database_creator.database_creator as db
import database_insert.db_insert as db_insert

from hockeydata.constants import *
from logger.logging_config import logger
from sqlalchemy import update
from sqlalchemy.orm import Session


class EliteDatabasePipeline():
    """class containing methods used for inserting data in DB"""


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.db_method = db_insert.DatabaseMethods(self.db_session)
        self.query = db_insert.Query(db_session=self.db_session)


    def input_data_in_player_table(self, dict_info: dict) -> int:
        """"inputs data into table players
            values in the table depend on the tables players, 
            nationalities and places
        """

        logger.debug(f"Input of player info dict {dict_info}"
                     f" into table {db.Player.__tablename__} started")
        nr_team_id = self.db_method._input_uid(
            table=db.Team, uid_val=dict_info[NHL_RIGHTS_UID], 
            uid=dict_info[NHL_RIGHTS_UID], team=None, long_name=None, active=None, founded=None, place_id=None, stadium_id=None)
        place_dict = dict_info[PLACE_DICT]
        place_birth_id = self.db_method._input_unique_data_NA_excluded(
            table=db.Place, non_condition=place_dict[PLACE], country_s=place_dict[COUNTRY], place=place_dict[PLACE], region=place_dict[REGION])
        player_id = self.query._find_id_in_table(
            table=db.Player, uid=dict_info[PLAYER_UID])
        if player_id == None:
            player_id = self.db_method._input_data(
                table=db.Player, name=dict_info[PLAYER_NAME],
                uid=dict_info[PLAYER_UID], position=dict_info[POSITION],
                active=dict_info[ACTIVE], age=dict_info[AGE], 
                shoots=dict_info[SHOOTS], catches=dict_info[CATCHES], 
                contract=dict_info[CONTRACT_END], cap_hit=dict_info[CAP_HIT], 
                signed_nhl=dict_info[SIGNED_NHL], date_birth=dict_info[BIRTH_DATE], drafted=dict_info[DRAFTED], 
                height=dict_info[HEIGHT], weight=dict_info[WEIGHT], 
                nhl_rights_id=nr_team_id, place_birth_id=place_birth_id)
        else:
            self.db_method._update_data(
                table=db.Player, where_col=db.Player.uid,
                where_val=dict_info[PLAYER_UID],
                name=dict_info[PLAYER_NAME], uid=dict_info[PLAYER_UID], position=dict_info[POSITION], active=dict_info[ACTIVE], age=dict_info[AGE], shoots=dict_info[SHOOTS],
                catches=dict_info[CATCHES], contract=dict_info[CONTRACT_END], cap_hit=dict_info[CAP_HIT], signed_nhl=dict_info[SIGNED_NHL], date_birth=dict_info[BIRTH_DATE], drafted=dict_info[DRAFTED], 
                height=dict_info[HEIGHT], weight=dict_info[WEIGHT], 
                nhl_rights_id=nr_team_id, place_birth_id=place_birth_id)
        logger.debug(f"Input of player info dict {dict_info} "
                     f"into table {db.Player.__tablename__} finished, "
                     f"new entry added at index {player_id}")
        return player_id
    
    def input_data_in_team_table(
            self, dict_info: dict, stadium_id: int
            ) -> int:
        """inputs info about team in teams table
            values in the table depend on tables places and stadiums
            id of stadium from table stadiums must be known beforehand
        """
        
        logger.debug(f"Input of team info dict {dict_info}"
                     f" into table {db.Team.__tablename__} started")
        place_dict = dict_info[PLACE_DICT]
        if place_dict == None:
            place_id = None
        else:
            place_id = self.db_method._input_unique_data_NA_excluded(
                table=db.Place, place=place_dict[PLACE],
                non_condition=place_dict[PLACE],
                region=place_dict[REGION], 
                country_s=place_dict[COUNTRY])
        team_id = self.query._find_id_in_table(
            table=db.Team, uid=dict_info[TEAM_UID])
        if team_id == None:
            team_id = self.db_method._input_unique_data(
            table=db.Team,
            uid=dict_info[TEAM_UID],
            team=dict_info[SHORT_NAME],
            long_name=dict_info[LONG_NAME],
            active=dict_info[ACTIVE],
            place_id=place_id,
            founded=dict_info[YEAR_FOUNDED],
            stadium_id=stadium_id)
        else:
            self.db_method._update_data(
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
        logger.debug(f"Input of team info dict {dict_info}"
                     f" into table {db.Team.__tablename__} finished, new "
                     f"entry added at index {team_id}")
        return team_id
    
    def _input_data_in_league_table(
            self, league_uid: int, long_name: str
            ) -> int:
        """inputs league info (uid and name) in leagues table"""

        logger.debug(f"Input of league_uid {league_uid} and name {long_name}"
                     f" into table {db.League.__tablename__} started")
        league_id = self.query._find_id_in_table(table=db.League,
                                                    uid=league_uid)
        if league_id is None:
            league_id = self.db_method._input_unique_data(
                table=db.League,
                league=long_name, 
                uid=league_uid)
        else:
            self.db_method._update_data(table=db.League, 
                                         where_col=db.League.uid, where_val=league_uid,
                                         league=long_name)
        logger.debug(f"Input of league_uid {league_uid} and name {long_name}"
                     f" into table {db.League.__tablename__} finished, "
                     f" new entry added at index {league_id}")
        return league_id
    
    def _input_achievement(self, achiev: str, league_id: int) -> int:
        """inputs table achievement into table achievements based on
           its name which serves as its unique identificator and league_id
           values in the table depend on table leagues
        """

        logger.debug(f"Input of achievement {achiev} with index {league_id}"
                     f" from table {db.League.__tablename__} into table"
                     f" {db.Achievement.__tablename__} started")
        achiev_id = self.query._find_id_in_table(
            table=db.Achievement, uid=achiev)
        if achiev_id is None:
            achiev_id = self.db_method._input_unique_data_NA_excluded(
                table=db.Achievement, non_condition=achiev, 
                uid=achiev, league_id=league_id)
        else:
            self.db_method._update_data(
                table=db.Achievement, where_col=db.Achievement.uid, 
                where_val=achiev, league_id=league_id)
        logger.debug(f"Input of achievement {achiev} with index {league_id}"
                     f" from table {db.League.__tablename__} into table"
                     f" {db.Achievement.__tablename__} finished, new entry"
                     f" added at index {achiev_id}")
        return achiev_id

    def _input_achievement_relation(
            self, player_id: int, achiev: str, season: str
            ) -> int:
        """input relation between player, achievement and year it was achieved 
           into table players achievements
           values in the table depend on tables players, achievements and seasons
           Parameters: player_id - id of player from table players
                       aciev - achievement name which also serves as its unique indentificator
                       season - season string
        """

        logger.debug(f"Input of player achievement relation {achiev} and"
                     f" index {player_id} from {db.Player.__tablename__}"
                     f" table into table {db.PlayerAchievement.__tablename__}" f" started")
        achiev_id = self.db_method._input_uid(
            table=db.Achievement, uid_val=achiev, uid=achiev, league_id=None)
        season_id = self.db_method._input_unique_data(
            table=db.Season, season=season)
        relation_id = self.db_method._input_unique_data(
            table=db.PlayerAchievement, season_id=season_id, achievement_id=achiev_id, player_id=player_id)
        logger.debug(f"Input of player achievement relation {achiev} and"
                     f" index from {db.Player.__tablename__} table into"
                     f" table {db.PlayerAchievement.__tablename__} finished, "
                     f"new entry added at index {relation_id}")
        return relation_id
    
    def _input_player_stats(self, dict_stats: dict) -> int:
        """inputs one season statistics for player into table player_statistics
           values in the table depend on tables players, teams, league and
           seasons
           team_id is attained based on uid of team, 
           season based on season string
           league id based on uid of league
           player_id must be already included in dictionary dict_stats 
           input is dictionary with information on indiviual statistics, info
           on if the player is goalie or field player and if the statistics are from regular season or play off
        """

        team_id = self.db_method._input_uid(
            table=db.Team, uid_val=dict_stats[TEAM_UID], 
            uid=dict_stats[TEAM_UID], team=None, long_name=None, active=None, founded=None, place_id=None, stadium_id=None)
        league_id = self.db_method._input_uid(
            table=db.League, uid_val=dict_stats[LEAGUE_UID], league=None,
            uid=dict_stats[LEAGUE_UID])
        season_id = self.db_method._input_unique_data(
            table=db.Season, season=dict_stats[SEASON_NAME])
        if dict_stats[IS_GOALIE] == False:
            logger.debug(f"Input of skater stats dict {dict_stats}"
                         f" into table {db.PlayerStats.__tablename__} started")
            stat_id = self.db_method._input_unique_data(
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
                plus_minus=dict_stats[PLUS_MINUS])
            logger.debug(f"Input of skater stats dict {dict_stats}"
                         f" into table {db.PlayerStats.__tablename__}"
                         f" finished, new entry added at index {stat_id}")
        else:
            logger.debug(f"Input of goalie stats dict {dict_stats}"
                         f" into table {db.GoalieStats.__tablename__} started")
            stat_id = self.db_method._input_unique_data(
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
                toi=dict_stats[TOI])
            logger.debug(f"Input of goalie stats dict {dict_stats}"
                         f" into table {db.GoalieStats.__tablename__}"
                         f" finished, new entry added at index {stat_id}")
            return stat_id
    
    def _input_stadium_data(self, stadium_dict: dict) -> int:
        """inputs data into stadium into stadiums table,
           values in the table depend on the table places
           parameter is dict containg: stadium name, its capacity,
           town in  which it is located and year of construction
        """
        
        logger.debug(f"Input of stadium dict {stadium_dict}"
                     f" into table {db.Stadium.__tablename__} started")
        if stadium_dict[ARENA_NAME] is None:
            return None
        dict_place = stadium_dict[PLACE_DICT]
        if set(dict_place.values()) != {None}:
            place_id = self.db_method._input_unique_data_NA_excluded(
                table=db.Place, 
                non_condition=dict_place[PLACE],
                place=dict_place[PLACE],
                region=dict_place[REGION],
                country_s=dict_place[COUNTRY])
        else:
            place_id = None
        stadium_id = self.db_method._input_unique_data_NA_excluded(
            table=db.Stadium, 
            non_condition=stadium_dict[ARENA_NAME],
            stadium=stadium_dict[ARENA_NAME],
            capacity=stadium_dict[CAPACITY],
            construction_year=stadium_dict[CONSTRUCTION_YEAR],
            place_id=place_id)
        logger.debug(f"Input of stadium dict {stadium_dict}"
                     f" into table {db.Stadium.__tablename__} finished,"
                     f" new entry added at index {stadium_id}")
        return stadium_id

    def _input_affiliated_teams(self, team_id: int, team_aff_uid: int) -> int:
        """inputs relation between affiliated teams in table affiliated_teams
        parameters are id of team from table teams and uid of its affiliated team
        values in the table depend on the values from table teams
        in case the entry was already inputted in table in reverse:
        (team connected to team_id was inputted as affiliated team of team with uid team_aff_uid) 
        new entry is not inputted into table 
        """

        logger.debug(f"Input of affiliated team combination for team with"
                     f" index {team_id} from table {db.Team.__tablename__}"
                     f" and affiliated team with uid {team_aff_uid} into table"
                     f" {db.AffiliatedTeam} started")
        if team_id is None or team_aff_uid is None:
            return None
        team_aff_id = self.db_method._input_uid(table=db.Team,
                                                  uid_val=team_aff_uid, uid=team_aff_uid, 
                                                  team=None, 
                                                  long_name=None, 
                                                  active=None, 
                                                  founded=None, 
                                                  place_id=None, stadium_id=None)
        relation_id = self.query._find_id_in_table(table=db.AffiliatedTeam, 
                                              team_1_id=team_id,team_2_id=team_aff_id)
        if relation_id is not None:
            return relation_id
        relation_id = self.query._find_id_in_table(table=db.AffiliatedTeam, 
                                              team_1_id=team_aff_id,team_2_id=team_id)
        if relation_id is not None:
            return relation_id
        relation_id = self.db_method._input_unique_data(
            table=db.AffiliatedTeam, 
            team_1_id=team_id,
            team_2_id=team_aff_id)
        logger.debug(f"Input of affiliated team combination for team with"
                     f" index {team_id} from table {db.Team.__tablename__}"
                     f" and affiliated team with uid {team_aff_uid} into table"
                     f" {db.AffiliatedTeam} finished, new entry added at"
                     f" index {relation_id}")
        return relation_id
    
    def _input_colour_team(self, team_id: int, colour: str) -> int:
        """inputs relation between team and its colours into table team_colours
        values in the table depend on the values from table teams and colours
           parameters are: team_id - id of team from table teams
                           colour - string with colour name
        """

        logger.debug(f"Input of team colour {colour} and id from table"
                     f" {db.Team.__tablename__} {team_id} into table"
                     f" {db.TeamColour} started")
        if team_id is None or colour is None:
            return None
        colour_id = self.db_method._input_unique_data_NA_excluded(
            table=db.Colour, non_condition=colour, colour=colour)
        relation_id = self.db_method._input_unique_data(
            table=db.TeamColour, team_id=team_id, colour_id=colour_id)
        logger.debug(f"Input of team colour {colour} and id from table"
                     f" {db.Team.__tablename__} {team_id} into table"
                     f" {db.TeamColour.__tablename__} finished, "
                     f" new entry added at index {relation_id}")
        return relation_id
    
    def _input_player_draft(self, draft_dict: dict, player_id: int) -> int:
        """inputs draft information regarding one player into drafts;
           currently only for NHL draft info
           values depend on table players and teams (team that drafted player)
           parameters of method are following:
           player_id - id of player from table players
           draft_dict - dict with info about in which round on which position, in which year and by which team was player drafted
        """

        logger.debug(f"Input of draft dict {draft_dict} for player at"
                     f" index {player_id} at {db.PlayerDraft.__tablename__}"
                     f" table started")
        if player_id is None:
            return None
        team_id = self.db_method._input_uid(
            table=db.Team, uid_val=draft_dict[TEAM_UID], 
            uid=draft_dict[TEAM_UID], team=None, long_name=None,
            active=None, place_id=None, founded=None, stadium_id=None)
        draft_id = self.db_method._input_unique_data(
            table=db.PlayerDraft,
            player_id=player_id,
            team_id=team_id,
            draft_round=draft_dict[DRAFT_ROUND],
            draft_year=draft_dict[DRAFT_YEAR],
            draft_position=draft_dict[DRAFT_POSITION])
        logger.debug(f"Input of draft dict {draft_dict} for player at"
                     f" index {player_id} at players table finished, row"
                     f" added at index {draft_id} in the"
                     f" {db.PlayerDraft.__tablename__} table")
        return draft_id
    
    def _input_player_nation(self, player_id: int, nationality: str) -> int:
        """inputs relation between player and his nationality
           separate table is needed because for some players more than one nationality can be listed, values depend on values from tables players and nationality, inputs into method are the following:
           player_id - id of player from table players
           nationality - country code of nation
        """
        
        logger.debug(f"Input nationality of player at index {player_id}"
                     f" at players table and nationality {nationality}"
                     f" into table {db.PlayerNationality.__tablename__}"
                     f" started")
        if nationality is None:
            return None
        nation_id = self.db_method._input_unique_data(
            table=db.Nationality,
            nationality=nationality)
        relation_id=self.db_method._input_unique_data(
            table=db.PlayerNationality,
            player_id=player_id,
            nationality_id=nation_id)
        logger.debug(f"Input nationality of player at index {player_id}"
                     f" in {db.Player.__tablename__} table and nationality"
                     f" {nationality} into table"
                     f" {db.PlayerNationality.__tablename__}  finished")
        return relation_id
    
    def _input_player_relation(
            self, player_from_uid: int, player_to_id: int, relation: str
            ) -> int:
        """inputs one relation between players into table player_relations
           the values in the table are dependent on the tables players and relations in which different types of relation are listed
           inputs in the method are following:
           for example relation: grandfather (uid: 123) of player with uid 456
           player_from_uid = 123, player_to_id=456, and relation='grandfather'
        """

        logger.debug(f"Input of player's relation of player with"
                     f" uid {player_from_uid} with player at index"
                     f" {player_to_id} in {db.Player.__tablename__} table"
                     f" and type of relation {relation} into table"
                     f"{db.PlayerRelation.__tablename__}  started")
        player_from_id = self.db_method._input_uid(
            table=db.Player, uid_val=player_from_uid, name=None, uid=player_from_uid, position=None, active=None, age=None, shoots=None, catches=None, contract=None, cap_hit=None, signed_nhl=None, date_birth=None, drafted=None, 
            height=None, weight=None, nhl_rights_id=None, place_birth_id=None)
        relation_id = self.db_method._input_unique_data(
            table=db.Relation, relation=relation)
        table_relation_id = self.db_method._input_unique_data(
            table=db.PlayerRelation, player_from_id=player_from_id,
            player_to_id=player_to_id, relation_id=relation_id)
        logger.debug(f"Input of player's relation of player with"
                     f" uid {player_from_uid} with player at index"
                     f" {player_to_id} in {db.Player.__tablename__} table"
                     f" and type of relation {relation} into table"
                     f"{db.PlayerRelation.__tablename__}  finished, "
                     f"index of new entry is {table_relation_id}")
        return table_relation_id
    
    def _input_retired_number_relation(
            self, team_id: int, player_uid: int, number: int
            ) -> int:
        """inputs one team retired number, team and player relation     
           in table retired_numbers, values in the table are connected to tables teams and players so it is necessary to find id 
           of player with player_uid from table players and id,
           id of team for which the number was retired must be then be known beforehand
        """
        
        logger.debug(f"Input of retired number relation with number {number}"
                     f" for player uid {player_uid} and id from"
                     f" {db.Team.__tablename__} table {team_id} into table"
                     f" {db.RetiredNumber.__tablename__} started")
        player_id = self.db_method._input_uid(table=db.Player,
                                                uid_val=player_uid, 
                                                name=None, 
                                                uid=player_uid, 
                                                position=None, 
                                                active=None, 
                                                age=None, 
                                                shoots=None, 
                                                catches=None, 
                                                contract=None, 
                                                cap_hit=None, 
                                                signed_nhl=None, date_birth=None, 
                                                drafted=None, 
                                                height=None, 
                                                weight=None, nhl_rights_id=None, place_birth_id=None)
        relation_id = self.db_method._input_unique_data(
            table=db.RetiredNumber, team_id=team_id, 
            player_id=player_id, number=number)
        logger.debug(f"Input of retired number relation with number {number}"
                     f" for player uid {player_uid} and id from"
                     f" {db.Team.__tablename__} table {team_id} into table"
                     f" {db.RetiredNumber.__tablename__} finished, index of"
                     f" new entry is {relation_id}")
        return relation_id
    
    def _input_team_name(
            self, name: str, min: int, max: int, team_id: int
            ) -> int:
        """inputs one historic name of team with range of seasons in which 
           it was in table team_names, values in the table are connected to tables seasons and teams so the values from these table related to the entry in team_names table are attained first based on:
           min - season from which the name was in use
           max - season to which the name was in use
           name - name of the team in the range of the seasons
           team_id is then id of team for which the historic name is saved
           from table teams
        """
        logger.debug(f"Input of team name {name} with season range {min}"
                     f" {max} into table {db.TeamName.__tablename__} started")
        season_min_id = self.db_method._input_unique_data(table=db.Season,
                                                            season=min)
        season_max_id = self.db_method._input_unique_data(table=db.Season,
                                                            season=max)
        team_name_id = self.db_method._input_unique_data(
            table=db.TeamName, team_name=name, year_from=season_min_id, year_to=season_max_id, team_id=team_id)
        logger.debug(f"Input of team name {name} with season range {min}"
                     f" {max} into table {db.TeamName.__tablename__} finished"
                     f", id of entry is {team_name_id}")
        return team_name_id
    
    def _input_team_position(self, dict_: dict) -> int:
        """inputs team position in table with season standings
           table is connected to table teams, postseason_types,
           divisions and seasons, so the values from these table related to
           the entry in season standings table must be attained at first 
        """
        logger.debug(f"Input of team position with dict {dict_}"
                     f" into table {db.TeamSeason.__tablename__} started")
        team_id = self.db_method._input_uid(table=db.Team, 
                                             uid_val=dict_[TEAM_UID],
                                             uid=dict_[TEAM_UID], 
                                             team=None, 
                                             long_name=None, 
                                             active=None, 
                                             founded=None, 
                                             place_id=None, 
                                             stadium_id=None)
        division_id = self.db_method._input_unique_data_NA_excluded(
            table=db.Divison, non_condition=dict_[SECTION_TYPE], 
            division=dict_[SECTION_TYPE])
        season_id = self.db_method._input_unique_data(
            table=db.Season, season=dict_[SEASON_NAME])
        postseason_type_id = self.db_method._input_unique_data_NA_excluded(
            table=db.PostseasonType, non_condition=dict_[POSTSEASON],postseason_type=dict_[POSTSEASON])
        position_id = self.db_method._input_unique_data(
            table=db.TeamSeason, 
            position=dict_[LEAGUE_POSITION], 
            league_id=dict_[LEAGUE_ID], 
            team_id=team_id, 
            division_id=division_id,
            conference_id=None, 
            season_id=season_id,
            gp=dict_[GP],
            w=dict_[W],
            t=dict_[T], 
            l=dict_[L], 
            otw=dict_[OTW],
            otl=dict_[OTL], 
            gf=dict_[GOALS_FOR], 
            ga=dict_[GOALS_AGAINST],
            plus_minus=dict_[PLUS_MINUS], 
            tp=dict_[TOTAL_POINTS], 
            postseason_type_id=postseason_type_id)
        logger.debug(f"Input of team position with dict {dict_}"
                     f" into table {db.TeamSeason.__tablename__} finished,"
                     f" index of entry is {position_id}")
        return position_id
    
    def _input_nhl_elite_player_mapper(self, dict_: dict) -> None:
        season_id = self.db_method._input_unique_data(
                table=db.Season, season=dict_[SEASON_NAME])
        mapper_id = self.db_method._input_unique_data(
            table=db.NHLEliteNameMapper,
            nhl_name=dict_["nhl_name"],
            elite_name=dict_["db_name"],
            player_number = dict_["number"],
            team_id = dict_["team_id"],
            season_id = season_id,
            )
         
        return mapper_id