import database.create_database.database_creator as db

class CreateStatsTableEntry:



    def __init__(self):
        pass


    def create_season_player_entry(self, dict_season, dict_info):
        season_entry = db.PlayerStats(player_id=dict_info["player_id"], regular_season=dict_info["regular_season"], season_id=dict_info["season_id"], 
                                      league_id=dict_info["league_id"], team_id=dict_info["team_id"],
                                       captaincy = dict_info["leadership"],
                                      games_played=dict_season["gp"], goals=dict_season["g"],
                                      assists=dict_season["a"], total_points=dict_season["tp"],
                                      PM=dict_season["PIM"], plus_minus=dict_season["plus_minus"])
        return season_entry
        
    def create_season_goalie_entry(self, dict_season, dict_info):
        season_entry = db.GoalieStats(player_id=dict_info["player_id"], regular_season=dict_info["regular_season"], 
                                      season_id=dict_info["season_id"], 
                                      league_id=dict_info["league_id"], team_id=dict_info["team_id"],
                                      captaincy = dict_info["leadership"],
                                      games_played=dict_season["gp"], gd=dict_season["gd"],
                                      goal_against_average=dict_season["gaa"], 
                                      save_percentage=dict_season["svp"], goal_against=dict_season["ga"],
                                      shot_saved=dict_season["svs"], shotouts=dict_season["so"],
                                      wins=dict_season["w"], looses=dict_season["l"],
                                      ties=dict_season["t"], toi=dict_season["toi"])
        return season_entry
    


    def find_id_in_player_stats_table(self, dict_info):
        row_data =  db.session.query(db.PlayerStats.id).filter_by(player_id=dict_info["player_id"],  
                                                                regular_season=dict_info["regular_season"], season_id=dict_info["season_id"], 
                                                                league_id=dict_info["league_id"], 
                                                                team_id=dict_info["team_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        

    def find_id_in_goalie_stats_table(self, dict_info):
        row_data =  db.session.query(db.GoalieStats.id).filter_by(player_id=dict_info["player_id"], 
                                                                regular_season=dict_info["regular_season"], season_id=dict_info["season_id"], 
                                                                league_id=dict_info["league_id"], 
                                                                team_id=dict_info["team_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        












