from collections import Counter

import database_creator.database_creator as db
import database_queries.database_query as dq


class PlayerNameChecker():


    def __init__(self, session):
        self.session = session


    def get_player_team_season_dict(self, selected_seasons: list) -> dict:
        player_dict = self.get_all_player_season_data(selected_seasons)
        player_dict = self.solve_identical_names(player_dict)

        return player_dict


    def get_all_player_season_data(
            self, selected_seasons: list) -> list:
        query_object = dq.DbDataGetter(session=self.session)
        seasons_filter = query_object.get_list_filter(
            table_column=db.Season.season,
            values=selected_seasons
            )                                          
        player_results = query_object.get_db_query_result(
            query_name="nhl_season_players", filters=seasons_filter)
        goalkeeper_results = query_object.get_db_query_result(
            query_name="nhl_season_goalies", filters=seasons_filter)
        results = player_results + goalkeeper_results
        season_team_players: dict[str, dict[str, list[str]]] = {}
        for row in results:
            player_id, player_name, team_id, team_name, season = row

            if season not in season_team_players:
                season_team_players[season] = {}

            if team_name not in season_team_players[season]:
                season_team_players[season][team_name] = []

            season_team_players[season][team_name].append(
                {
                    "player_name": player_name, 
                    "player_id": player_id, 
                    "team_id": team_id
                    }
            )
            
        return season_team_players
    

    def get_all_nhl_teams_uids(self) -> dict:

        query_object = dq.DbDataGetter(session=self.session)
        nhl_teams = query_object.get_db_query_result(
            query_name="nhl_season_players")
        



    

    def solve_identical_names(self, season_team_players: dict) -> dict:
        for season in season_team_players:
            for team in season_team_players[season]:
                season_team_players[season][team] = self.solve_same_names_team(
                    season_team_players[season][team])
        
        return season_team_players


    def solve_same_names_team(dict_team: dict) -> dict:
        new_team_dict = {}
        player_names = Counter([dict_['player_name'] for dict_ in dict_team])
        duplicates = [
            item for item, count in player_names.items() if count > 1
            ]
        new_team_dict["duplicates"] = [
            dict_ for dict_ in dict_team if dict_["player_name"] in duplicates
            ]
        
        new_team_dict["single"] = [
            dict_ for dict_ in dict_team if dict_["player_name"] in duplicates
            ]
        
        return new_team_dict      