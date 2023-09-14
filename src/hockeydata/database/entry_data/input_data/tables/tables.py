import database.create_database.database_creator as db
from sqlalchemy import update

class CreateAchievementPlayerTableEntry:

    def __init__(self):
        pass


    def create_achievement_player_entry(self, achievement_id, player_id, season_id):
        achievement_entry = db.PlayerAchievement(player_id=player_id, achievement_id=achievement_id, season_id=season_id)
        return achievement_entry

    def find_id_in_achievement_player_table(self, achievement_id, player_id, season_id):
        row_data =  db.session.query(db.PlayerAchievement.id).filter_by(player_id=player_id, achievement_id=achievement_id, season_id=season_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
class CreateAchievementTableEntry:

    def __init__(self):
        pass

    def create_achievement_entry(self, achievement_name, league_id=None):
        achievement_entry = db.Achievement(achievement=achievement_name, league_id=league_id)
        return achievement_entry

    def find_id_in_achievement_table(self, achievement_name):
        row_data =  db.session.query(db.Achievement.id).filter_by(achievement=achievement_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
    def update_achievement_entry(self, achievement_name, league_id):
        update_query = update(db.Achievement).where(db.Achievement.achievement == achievement_name).values(league_id=league_id)
        return update_query

class CreateAffiliatedTeamsTableEntry:

    def __init__(self):
        pass

    def create_affiliated_teams_entry(self, team_main, team_affiliated):
        affiliated_teams_entry = db.AffiliatedTeam(team_1_id=team_main, team_2_id=team_affiliated)
        return affiliated_teams_entry
    
    def find_id_in_affiliated_teams_table(self, team_1_id, team_2_id):
        row_data =  db.session.query(db.AffiliatedTeam.id).filter_by(team_1_id=team_1_id, 
                                                                     team_2_id=team_2_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id

class CreateColourTableEntry:

    def __init__(self):
        pass

    def create_colour_entry(self, colour):
        colour_entry = db.Colour(colour=colour)
        return colour_entry

    def find_id_in_colour_table(self, colour):
        row_data =  db.session.query(db.Colour.id).filter_by(colour=colour).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
class CreateLeagueTableEntry:

    def __init__(self):
        pass

    def find_id_in_league_table(self, league_uid):
        row_data =  db.session.query(db.League.id).filter_by(league_elite=league_uid).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
    def create_league_entry(self, league_uid, long_name):
        league_entry = db.League(league_elite=league_uid, league=long_name)
        return league_entry
    
    def update_league_entry(self, league_uid, long_name):
        update_query = update(db.League).where(db.League.league_elite == league_uid).values(league=long_name)
        return update_query
    
    def insert_uid_league_entry(self, league_uid):
         team_entry = db.League(league_elite = league_uid, league=None)
         return team_entry

class CreateNationalityTableEntry:

    def __init__(self):
        pass

    def create_nationality_entry(self, nationality_name):
        nationality_entry = db.Nationality(nationality=nationality_name)
        return nationality_entry

    def find_id_in_nationality_table(self, nationality_name):
        row_data =  db.session.query(db.Nationality.id).filter_by(nationality=nationality_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id

class CreatePlaceTableEntry:

    def __init__(self):
        pass

    def create_place_entry(self, place_name, region_name, country_name):
        place_entry = db.Place(place=place_name, region=region_name, country_s=country_name)
        return place_entry

    def find_id_in_place_table(self, place_name, region_name, country_name):
        row_data =  db.session.query(db.Place.id).filter_by(place=place_name, region=region_name, country_s=country_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
class CreatePlayerTableEntry:

    def __init__(self):
        pass

    def create_player_entry(self, dictd, dict_fkeys):
        player_entry = db.Player(name = dictd["name"],
                                 u_id = dictd["u_id"],
                                 position = dictd["position"], 
                                 active = dictd["active"],
                                 age = dictd["age"],
                                 shoots = dictd["shoots"],
                                 catches = dictd["catches"],
                                 contract = dictd["contract"],
                                 cap_hit= dictd["cap_hit"],
                                 signed_nhl = dictd["signed_nhl"],
                                 date_birth = dictd["date_birth"],
                                 drafted = dictd["drafted"],
                                 height = dictd["height"],
                                 weight = dictd["weight"],
                                 nhl_rights_id = dict_fkeys["nhl_team_rights_id"],
                                 place_birth_id = dict_fkeys["place_birth_id"]
                                 )
        return player_entry
        
    def check_if_id_exists_in_table_player(self, u_id_1):
        row_data = db.session.query(db.Player.id).filter_by(u_id = u_id_1).first()
        if row_data is None:
            return None
        else:
            return row_data.id
    def update_player_entry_2(self, dictd, dict_fkeys):
        update_query = db.Player(
                                id = dictd["id"],
                                name = dictd["name"],
                                 position = dictd["position"], 
                                 active = dictd["active"],
                                 age = dictd["age"],
                                 shoots = dictd["shoots"],
                                 catches = dictd["catches"],
                                 contract = dictd["contract"],
                                 cap_hit= dictd["cap_hit"],
                                 signed_nhl = dictd["signed_nhl"],
                                 date_birth = dictd["date_birth"],
                                 drafted = dictd["drafted"],
                                 height = dictd["height"],
                                 weight = dictd["weight"],
                                 nhl_rights_id = dict_fkeys["nhl_team_rights_id"],
                                 place_birth_id = dict_fkeys["place_birth_id"])
        return update_query
        
    def update_player_entry(self, dictd, dict_fkeys):
        update_query = update(db.Player).where(db.Player.u_id == dictd["u_id"]).values(
            name = dictd["name"],
                                 position = dictd["position"], 
                                 active = dictd["active"],
                                 age = dictd["age"],
                                 shoots = dictd["shoots"],
                                 catches = dictd["catches"],
                                 contract = dictd["contract"],
                                 cap_hit= dictd["cap_hit"],
                                 signed_nhl = dictd["signed_nhl"],
                                 date_birth = dictd["date_birth"],
                                 drafted = dictd["drafted"],
                                 height = dictd["height"],
                                 weight = dictd["weight"],
                                 nhl_rights_id = dict_fkeys["nhl_team_rights_id"],
                                 place_birth_id = dict_fkeys["place_birth_id"])
        return update_query
    
    def insert_uid_player_entry(self, u_id_1):
         player_entry = db.Player(u_id = u_id_1,
                                  name=None, 
                                position = None, 
                                 active = None,
                                 age = None,
                                 shoots = None,
                                 catches = None,
                                 contract = None,
                                 cap_hit= None,
                                 signed_nhl = None,
                                 date_birth = None,
                                 drafted = None,
                                 height = None,
                                 weight = None,
                                 nhl_rights_id = None,
                                 place_birth_id = None)
         return player_entry
    
class CreateRetiredNumberTableEntry:

    def __init__(self):
        pass

    def create_retired_number_entry(self, team_id, player_id, number):
        retired_number_entry = db.RetiredNumber(team_id=team_id, player_id=player_id, 
                                                number=number)
        return retired_number_entry
    
    def find_id_in_retired_number_table(self, team_id, player_id, number):
        row_data =  db.session.query(db.RetiredNumber.id).filter_by(team_id=team_id, 
                                                                     player_id=player_id,
                                                                     number=number).first()
        if row_data is None:
            return None
        else:
            return row_data.id 

class CreateSeasonTableEntry:

    def __init__(self):
        pass

    def create_season_entry(self, season_name):
        season_query = db.Season(season=season_name)
        return season_query
    
    def find_id_in_season_table(self, season_name):
        row_data = db.session.query(db.Season.id).filter_by(season=season_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id        

class CreateStadiumEntry():

    def __init__(self):
        pass

    def create_stadium_entry(self, stadium_dict):
        stadium_entry = db.Stadium(stadium=stadium_dict["arena_name"],
                                   capacity=stadium_dict["capacity"],
                                   construction_year=stadium_dict["construction_year"],
                                   place_id=stadium_dict["place_id"])
        return stadium_entry
    
    def find_id_in_stadium_table(self, stadium_dict):
        row_data = db.session.query(db.Stadium.id).filter_by(stadium=stadium_dict["arena_name"],
                                                            capacity=stadium_dict["capacity"],
                                                            construction_year=stadium_dict["construction_year"],
                                                            place_id=stadium_dict["place_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id      

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

class CreateTeamColourTableEntry:

    def __init__(self):
        pass

    def create_team_colour_entry(self, team_id, colour_id):
        team_colour_entry = db.TeamColour(team_id=team_id, colour_id=colour_id)
        return team_colour_entry

    def find_id_in_team_colour_table(self, team_id, colour_id):
        row_data =  db.session.query(db.TeamColour.id).filter_by(team_id=team_id, colour_id=colour_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id

class CreateTeamNameEntry():

    def __init__(self):
        pass

    def create_team_name_entry(self, team_name, min, max, team_id):
        team_name_entry = db.TeamName(team_name=team_name,
                                   year_from=min,
                                   year_to=max,
                                   team_id=team_id)
        return team_name_entry
    
    def find_id_in_team_name_table(self, team_name, min, max, team_id):
        row_data = db.session.query(db.TeamName.id).filter_by(team_name=team_name,
                                   year_from=min,
                                   year_to=max,
                                   team_id=team_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id    

class CreateTeamSeasonEntry():

    def __init__(self):
        pass

    def create_team_season_entry(self, ts_dict):
        team_season_entry = db.TeamSeason(position=ts_dict["position"],
                                          league_id=ts_dict["league_id"],
                                          team_id = ts_dict["team_id"],
                                          division_id=ts_dict["division_id"],
                                          conference_id=None,
                                          season_id=ts_dict["season_id"],
                                          gp=ts_dict["gp"],
                                          w=ts_dict["w"],
                                          t=ts_dict["t"],
                                          l=ts_dict["l"],
                                          otw=ts_dict["otw"],
                                          otl=ts_dict["otl"],
                                          gf=ts_dict["gf"],
                                          ga=ts_dict["ga"],
                                          plus_minus=ts_dict["plus_minus"],
                                          tp=ts_dict["tp"],
                                          postseason_type_id=ts_dict["postseason_type_id"])
        return team_season_entry

    def find_id_in_team_season_table(self, ts_dict):
        row_data = db.session.query(db.TeamSeason.id).filter_by(position=ts_dict["position"],
                                                                league_id=ts_dict["league_id"],
                                                                team_id = ts_dict["team_id"],
                                                                division_id=ts_dict["division_id"],
                                                                conference_id=None,
                                                                season_id=ts_dict["season_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id   

class CreateTeamTableEntry():

    def __init__(self):
        pass

    def create_team_entry(self, gi_dict):
        team_entry = db.Team(u_id=gi_dict["u_id"], 
                             team = gi_dict["short_name"],
                              long_name = gi_dict["full_name"],
                              active=gi_dict["active"],
                               place_id = gi_dict["place_id"], 
                               founded=gi_dict["founded"],
                               stadium_id=gi_dict["stadium_id"])
        return team_entry
    
    def update_team_entry(self, gi_dict):
        update_query = update(db.Team).where(db.Team.u_id == gi_dict["u_id"]).values(team = gi_dict["short_name"],
                                                                                    long_name = gi_dict["full_name"],
                                                                                    active=gi_dict["active"],
                                                                                    place_id = gi_dict["place_id"], 
                                                                                    founded=gi_dict["founded"],
                                                                                    stadium_id=gi_dict["stadium_id"])
        return update_query
            
    def find_id_in_team_table(self, u_id_1):
        row_data =  db.session.query(db.Team.id).filter_by(u_id=u_id_1).first()
        if row_data is None:
            return None
        else:
            return row_data.id
    
    def find_id_in_team_table_long(self, gi_dict):
        row_data =  db.session.query(db.Team.id).filter_by(u_id=gi_dict["u_id"], 
                             team = gi_dict["short_name"],
                              long_name = gi_dict["full_name"],
                              active=gi_dict["active"],
                               place_id = gi_dict["place_id"], 
                               founded=gi_dict["founded"],
                               stadium_id=gi_dict["stadium_id"]).first()
        print(row_data)
        if row_data is None:
            return None
        else:
            return row_data.id
                
    def insert_uid_team_entry(self, u_id_1):
         team_entry = db.Team(u_id = u_id_1, 
                              team = None,
                              long_name = None,
                              active=None,
                               place_id = None, 
                               founded=None,
                               stadium_id=None)
         return team_entry
    

class CreateDivisionEntry():

    def __init__(self):
        pass

    def create_division_entry(self, division):
        division_query = db.Divison(division=division)
        return division_query
    
    def find_id_in_division_table(self, division):
        row_data = db.session.query(db.Divison.id).filter_by(division=division).first()
        if row_data is None:
            return None
        else:
            return row_data.id 

class CreatePostSeasonTypeEntry():

    def __init__(self):
        pass

    def create_postseason_type_entry(self, postseason_type):
        postseason_type_query = db.PostseasonType(postseason_type=postseason_type)
        return postseason_type_query
    
    def find_id_in_postseason_type_table(self, postseason_type):
        row_data = db.session.query(db.PostseasonType.id).filter_by(postseason_type=postseason_type).first()
        if row_data is None:
            return None
        else:
            return row_data.id 
        

class CreatePlayerDraftEntry():
    
    def __init__(self):
        pass

    def create_player_draft_entry(self, player_id, team_id, draft_round, draft_position, draft_year):
        player_draft_entry = db.PlayerDraft(player_id=player_id, team_id=team_id, draft_round=draft_round,
                                            draft_position=draft_position, draft_year=draft_year)
        return  player_draft_entry
    
    def find_id_in_player_draft_table(self, player_id,  team_id, draft_round, draft_position, draft_year):
        row_data = db.session.query(db.PlayerDraft.id).filter_by(player_id=player_id,
                                                                    team_id=team_id,
                                                                    draft_round=draft_round,
                                                                    draft_position=draft_position,
                                                                    draft_year=draft_year).first()
        if row_data is None:
            return None
        else:
            return row_data.id     

class CreatePlayerNationalityEntry():

    def __init__(self):
        pass

    def create_nationality_player_entry(self, player_id, nationality_id):
        nationality_player_entry = db.PlayerNationality(player_id=player_id, nationality_id=nationality_id)
        return nationality_player_entry
    
    def find_id_in_nationality_player_table(self, player_id, nationality_id):
        row_data =  db.session.query(db.PlayerNationality.id).filter_by(player_id=player_id, 
                                                                        nationality_id=nationality_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id    
        

class CreateRelationEntry():

    def __init__(self):
        pass

    def create_relation_entry(self, relation):
        realtion_entry = db.Relation(relation=relation)
        return realtion_entry
    
    def find_id_in_relation_table(self, relation):
        row_data = db.session.query(db.Relation.id).filter_by(relation=relation).first()
        if row_data is None:
            return None
        else:
            return row_data.id   
          
class CreatePlayerRelationEntry():

    def __init__(self):
        pass

    def create_relation_player_entry(self, player_from_id, player_to_id, relation_id):
        relation_player_entry = db.PlayerRelation(player_from_id=player_from_id, player_to_id=player_to_id, relation_id=relation_id)
        return relation_player_entry
    
    def find_id_in_relation_player_table(self, player_from_id, player_to_id, relation_id):
        row_data =  db.session.query(db.PlayerRelation.id).filter_by(player_from_id=player_from_id, 
                                                                     player_to_id=player_to_id, 
                                                                     relation_id=relation_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id   

        

        

    

        

        
