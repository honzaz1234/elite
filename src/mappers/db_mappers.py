from collections import Counter

import database_creator.database_creator as db
import database_queries.database_query as dq
import mappers.team_mappers as team_map


class GetDBID():


    def __init__(self, session):
        self.session = session


    def get_player_id_team_season_mapper_dict(
            self, selected_seasons: list) -> dict:
        player_dict = self.get_all_player_season_data(selected_seasons)
        player_dict = self.solve_identical_names(player_dict)

        return player_dict


    def get_all_player_season_data(
            self, selected_seasons: list) -> dict:
        query_object = dq.DbDataGetter(session=self.session)
        seasons_filter = [query_object.get_list_filter(
            table_column=db.Season.season,
            values=selected_seasons
            )]                                      
        player_results = query_object.get_db_query_result(
            query_name="nhl_season_players", 
            filters=seasons_filter,
            distinct=True)
        goalkeeper_results = query_object.get_db_query_result(
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
        query_object = dq.DbDataGetter(session=self.session)
        nhl_teams = query_object.get_db_query_result(
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


    def get_elite_nhl_mapper(
            self, selected_seasons: list=None) -> dict:
        query_object = dq.DbDataGetter(session=self.session)
        if selected_seasons:
            seasons_filter = [query_object.get_list_filter(
                table_column=db.Season.season,
                values=selected_seasons
                )]
        else:
              seasons_filter = None                                    
        results = query_object.get_db_query_result(
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
        for season in selected_seasons:
            if season not in season_team_players:
                season_team_players[season] = {}
        return season_team_players