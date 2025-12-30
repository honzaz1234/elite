import unicodedata

from collections import Counter

import hockeydata.database_creator.database_creator as db
import hockeydata.database_queries.database_query as dq
import hockeydata.mappers.team_mappers as team_map


class GetDBID():


    def __init__(self, db_session):
        self.query = dq.DbDataGetter(db_session=db_session)


    def get_player_id_team_season_mapper_dicts(
            self, selected_seasons: list) -> dict:
        player_dict = self.get_all_player_season_data(selected_seasons)
        player_dict = self.solve_identical_names(player_dict)
        normalized_player_dict = self.normalize_player_names(player_dict)

        return player_dict, normalized_player_dict
    

    def normalize_player_names(self, player_dict: dict) -> dict:
        normalized_dict = {}
        for season in player_dict:
            normalized_dict[season] = {}
            for team in player_dict[season]:
                normalized_dict[season][team] = {}
                self.normalize_team_data(
                    team_dict=player_dict[season][team],
                    normalized_dict=normalized_dict[season][team])
        
        return normalized_dict


    def normalize_team_data(
            self, team_dict: dict, normalized_dict: dict) -> dict:
        for type_ in team_dict:
            normalized_dict[type_] = []
            for player_dict in team_dict[type_]:
                updated_player_dict = player_dict.copy()
                updated_player_dict["player_name"] = self.normalize_name(
                    updated_player_dict["player_name"])
                normalized_dict[type_].append(updated_player_dict)  


    def normalize_name(self, name: str) -> str:
        normalized = unicodedata.normalize("NFD", name)
        ascii_name = "".join(c for c in normalized if not unicodedata.combining(c))

        return ascii_name




    def get_all_player_season_data(
            self, selected_seasons: list) -> dict:
        seasons_filter = [self.query._get_list_filter(
            table_column=db.Season.season,
            values=selected_seasons
            )]                                      
        player_results = self.query.get_db_query_result(
            query_name="nhl_season_players", 
            filters=seasons_filter,
            distinct=True)
        goalkeeper_results = self.query.get_db_query_result(
            query_name="nhl_season_goalies", 
            filters=seasons_filter,
            distinct=True)
        results = player_results + goalkeeper_results
        season_team_players: dict[str, dict[str, list[str]]] = {}
        for row in results:
            player_id, player_name, team_id, team_name, team_uid, season = row

            if season not in season_team_players:
                season_team_players[season] = {}

            if team_uid not in season_team_players[season]:
                season_team_players[season][team_uid] = []

            season_team_players[season][team_uid].append(
                {
                    "player_name": player_name, 
                    "player_id": player_id, 
                    "team_id": team_id
                    }
            )
            
        return season_team_players
    

    def get_nhl_team_db_id_mapper(self) -> dict:
        nhl_teams = self.query.get_db_query_result(
            query_name="nhl_season_players", distinct=True)
        team_team_id_mapper = self.create_team_team_id_dict(nhl_teams)
        abb_team_id_mapper = self.create_abb_team_id_mapper_dict(
            team_team_id_mapper)
        
        return abb_team_id_mapper

        
    def create_team_team_id_dict(self, team_rows: list) -> dict:
        team_team_id_mapper = {}
        for tuple_ in team_rows:
            team_team_id_mapper[tuple_[1]] = tuple_[0]
        
        return team_team_id_mapper
    

    def create_abb_team_id_mapper_dict(
            self, team_team_id_mapper: dict) -> dict:
        abb_team_id_mapper = {}
        for team_name in team_team_id_mapper:
            abb = team_map.get_nhl_full_name_from_abbrevation(team_name)
            abb_team_id_mapper[abb] = team_team_id_mapper[team_name]

        return abb_team_id_mapper


    def solve_identical_names(self, season_team_players: dict) -> dict:
        for season in season_team_players:
            for team in season_team_players[season]:
                season_team_players[season][team] = self.solve_same_names_team(
                    season_team_players[season][team])
        
        return season_team_players


    def solve_same_names_team(self, dict_team: dict) -> dict:
        new_team_dict = {}
        player_names = Counter([dict_['player_name'] for dict_ in dict_team])
        duplicates = [
            item for item, count in player_names.items() if count > 1
            ]
        new_team_dict["duplicates"] = [
            dict_ for dict_ in dict_team if dict_["player_name"] in duplicates
            ]
        
        new_team_dict["single"] = [
            dict_ for dict_ in dict_team if dict_["player_name"] not in duplicates
            ]
        
        return new_team_dict     


    def get_nhl_elite_mapper(
            self, selected_seasons: list=None) -> dict:
        if selected_seasons:
            seasons_filter = [self.query._get_list_filter(
                table_column=db.Season.season,
                values=selected_seasons
                )]
        else:
              seasons_filter = None                                    
        results = self.query.get_db_query_result(
            query_name="name_mapper", 
            filters=seasons_filter,
            distinct=True)
        season_team_players: dict[str, dict[str, dict[tuple[str, str], str]]] = {}
        for row in results:
            player_id, elite_name, nhl_name, player_number, team_id, season = row

            if season not in season_team_players:
                season_team_players[season] = {}

            if team_id not in season_team_players[season]:
                season_team_players[season][team_id] = {}

            season_team_players[season][team_id][nhl_name] = {
            "db_name": elite_name, 
            "number": player_number, 
            "player_id": player_id
            }
        if selected_seasons is not None:
            for season in selected_seasons:
                if season not in season_team_players:
                    season_team_players[season] = {}

        return season_team_players
    

    def get_elite_nhl_names(self) -> dict:
        results = self.query.get_db_query_result(
            query_name="nhl_elite_names", 
            distinct=True)
        name_mapper = {}
        for row in results:
            elite_name, nhl_name = row
            name_mapper[nhl_name] = elite_name

        return name_mapper
    

    def get_nhl_elite_stadium_mapper(self) -> dict:
        results = self.query.get_db_query_result(
            query_name="nhl_elite_stadium_mapper", 
            distinct=True)
        stadium_mapper = {}
        for row in results:
            nhl_stadium, elite_stadium = row
            stadium_mapper[nhl_stadium] = elite_stadium

        return stadium_mapper
    

    def get_firstname_mapper(self) -> list:
        results = self.query.get_db_query_result(
            query_name="firstname_mapper", 
            distinct=True)
        firstname_mapper = []
        for row in results:
            name, alternative_name = row
            firstname_mapper.append({name, alternative_name})

        return firstname_mapper
    

    def get_look_ups(self) -> dict:
        table_mapper = {}
        lookup_keys = [
            db.PlayType,
            db.ShotType,
            db.ZoneType,
            db.ShotResult,
            db.PenaltyType,
            db.DeflectionType,
            db.BlockerType,
            db.ChallengeReason,
            db.ChallengeResult,
            db.TimeZone,
            db.PeriodType,
            db.GameStopageType,
            db.Season
            ]
        for table in lookup_keys:
           table_mapper[table] =  self.dictionary_db_table_wrapper(
            table.__tablename__
            )

        return table_mapper
    

    def dictionary_db_table_wrapper(self, table_name: str) -> dict:

        results = self.query.get_db_query_result(
            query_name=table_name
            )
        table_mapper = {}
        for row in results:
            id, type_name = row
            table_mapper[type_name] = id

        return table_mapper