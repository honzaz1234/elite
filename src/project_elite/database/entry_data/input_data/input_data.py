import database.entry_data.input_data.tables.player as player
import database.entry_data.input_data.tables.team as team
import database.entry_data.input_data.tables.league as league
import database.entry_data.input_data.tables.nationality as nationality
import database.entry_data.input_data.tables.stats as stats
import database.entry_data.input_data.tables.season as season
import database.entry_data.input_data.tables.achievement as achievement
import database.entry_data.input_data.tables.achievement_player as achievement_player
import database.entry_data.input_data.tables.place as place
import database.entry_data.input_data.tables.stadium as stadium
import database.entry_data.input_data.tables.stadium_team as stadium_team
import database.entry_data.input_data.tables.affiliated_teams as affiliated_teams
import database.entry_data.input_data.tables.retired_number as retired_number
import database.entry_data.input_data.tables.team_name as team_name 
import database.entry_data.input_data.tables.colour as colour    
import database.entry_data.input_data.tables.team_colour as team_colour                  


class InputData:

    def __init__(self):
        pass


    def input_player_uid(self, u_id):
        player_o = player.CreatePlayerTableEntry()
        player_id = player_o.check_if_id_exists_in_table_player(u_id_1=u_id)
        if player_id is None:
            player_entry = player_o.insert_uid_player_entry(u_id_1=u_id)
            player.db.session.add(player_entry)
            player.db.session.commit()
            player_id = player_o.check_if_id_exists_in_table_player(u_id_1=u_id)
        return player_id
    
    def input_team_uid(self, u_id):
        team_o = team.CreateTeamTableEntry()
        team_id = team_o.find_id_in_team_table(u_id_1=u_id)
        if team_id is None:
            team_entry = team_o.insert_uid_team_entry(u_id_1=u_id)
            team.db.session.add(team_entry)
            team.db.session.commit()
            team_id = team_o.find_id_in_team_table(u_id_1=u_id)
        return team_id
    
    def input_league_uid(self, league_uid):
        league_o = league.CreateLeagueTableEntry()
        league_id = league_o.find_id_in_league_table(league_uid=league_uid)
        if league_id is None:
            league_entry = league_o.insert_uid_league_entry(league_uid=league_uid)
            league.db.session.add(league_entry)
            league.db.session.commit()
            league_id = league_o.find_id_in_league_table(league_uid=league_uid)
        return league_id


    def input_player_data(self, dict_info, status):
        u_id = dict_info["u_id"]
        player_o = player.CreatePlayerTableEntry()
        if status == "insert_uid":
            insert_uid_entry = player_o.insert_uid_player_entry(dict_info["u_id"])            
            player.db.session.add(insert_uid_entry)
            player.db.session.commit()
            player_id = player_o.check_if_id_exists_in_table_player(u_id)
            return player_id
        dict_fk = {}
        for key in ["youth_team", "nhl_team_rights", "draft_team"]:
                team_name = dict_info[key]
                team_id = self.input_team_data(team_name=team_name)
                key_id = key + "_id"
                dict_fk[key_id] = team_id
        dict_fk["nation_id"] = self.input_nationality_data(nationality_name=dict_info["nation"])
        dict_fk["place_birth_id"] = self.input_place_data(country_name=dict_info["birth_country"], place_name=dict_info["birth_place"], region_name=dict_info["birth_region"])
        print(dict_info["name"])
        player_entry = player_o.create_player_entry(dictd=dict_info, dict_fkeys=dict_fk)
        player.db.session.add(player_entry)
        player.db.session.commit()
        player_id = player_o.check_if_id_exists_in_table_player(u_id)
        return player_id
    
    def input_nationality_data(self, nationality_name):
        if nationality_name is None:
            return None
        nationality_o = nationality.CreateNationalityTableEntry()
        nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        if nationality_id is None:
            nationality_entry= nationality_o.create_nationality_entry(nationality_name=nationality_name)
            nationality.db.session.add(nationality_entry)
            nationality.db.session.commit()
            nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        return nationality_id
    
    def input_team_data(self, general_info_dict):
        team_o = team.CreateTeamTableEntry()
        place_dict = general_info_dict["place"]
        if place_dict == None:
                place_id = None
        else:
                place_id = self.input_place_data(place_name=place_dict["place"],
                                                         region_name=place_dict["region"],
                                                        country_name=place_dict["country"])
        general_info_dict["place_id"] = place_id
        team_id = team_o.find_id_in_team_table(u_id_1=general_info_dict["u_id"])
        if team_id is None:
            insert_entry = team_o.create_team_entry(gi_dict=general_info_dict)
            team.db.session.add(insert_entry)
            team.db.session.commit()
        else:
            general_info_dict["id"] = team_id
            update_entry = team_o.update_team_entry(gi_dict=general_info_dict)                                          
            team.db.session.execute(update_entry)
        team_id = team_o.find_id_in_team_table(u_id_1=general_info_dict["u_id"])
        return team_id

    def input_league_data(self, league_name):
        if league_name is None:
            return None
        league_o = league.CreateLeagueTableEntry()
        league_id = league_o.find_id_in_league_table(league_name=league_name)
        if league_id is None:
            league_entry = league_o.create_league_entry(league_name=league_name)
            league.db.session.add(league_entry)
            league.db.session.commit()
            league_id = league_o.find_id_in_league_table(league_name=league_name)
        return league_id
    
    def input_player_stats_data(self, dict_info, season_dict):
        dict_info["team_id"] = self.input_team_data(team_name=dict_info["team_name"])
        dict_info["league_id"] = self.input_league_data(league_name=dict_info["league_name"])
        dict_info["season_id"] = self.input_season_data(season_name=dict_info["season_name"])
        season_o = stats.CreateStatsTableEntry()
        if dict_info["is_goalie"] == True:
            stat_id = season_o.find_id_in_goalie_stats_table(dict_info=dict_info)
        else:
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        if stat_id is not None:
            return stat_id
        if dict_info["is_goalie"] == True:
            season_entry = season_o.create_season_goalie_entry(dict_info=dict_info, dict_season=season_dict)
            stats.db.session.add(season_entry)
            stats.db.session.commit()
            stat_id = season_o.find_id_in_goalie_stats_table( dict_info=dict_info)
        else:
            season_entry = season_o.create_season_player_entry(dict_info=dict_info, dict_season=season_dict)
            stats.db.session.add(season_entry)
            stats.db.session.commit()
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        return stat_id
    
    def input_achievement_relation(self, player_id, achievement_name, season_name):
        achievement_id = self.input_achievement(achievement_name=achievement_name)
        season_id = self.input_season_data(season_name=season_name)
        achievement_player_o = achievement_player.CreateAchievementPlayerTableEntry()
        achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        if achievement_player_id is None:
            achievement_player_entry = achievement_player_o.create_achievement_player_entry(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
            achievement_player.db.session.add(achievement_player_entry)
            achievement_player.db.session.commit()
            achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        return achievement_player_id

    def input_achievement(self, achievement_name):
        achievement_o = achievement.CreateAchievementTableEntry()
        achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        if achievement_id is None:
            achievement_entry = achievement_o.create_achievement_entry(achievement_name=achievement_name)
            achievement.db.session.add(achievement_entry)
            achievement.db.session.commit()
            achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        return achievement_id

    def input_place_data(self, place_name, region_name, country_name):
        if place_name is None and region_name is None and country_name is None:
            return None
        place_o = place.CreatePlaceTableEntry()
        place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        if place_id is None:
            place_entry = place_o.create_place_entry(place_name=place_name, region_name=region_name, country_name=country_name)
            place.db.session.add(place_entry)
            place.db.session.commit()
            place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        return place_id
    

    def input_season_data(self, season_name):
        season_o = season.CreateSeasonTableEntry()
        season_id = season_o.find_id_in_season_table(season_name=season_name)
        if season_id is None:
            season_entry = season_o.create_season_entry(season_name=season_name)
            season.db.session.add(season_entry)
            season.db.session.commit()
            season_id = season_o.find_id_in_season_table(season_name=season_name)
        return season_id
    
    def input_stadium_data(self, stadium_dict):
        stadium_o =  stadium.CreateStadiumEntry()
        place_dict = stadium_dict["place"]
        place_id = self.input_place_data(place_name=place_dict["place"],
                                                         region_name=place_dict["region"],
                                                         country_name=place_dict["country"])
        print(place_id)
        stadium_dict["place_id"] = place_id
        stadium_id = stadium_o.find_id_in_stadium_table(stadium_dict=stadium_dict)
        if stadium_id is None:
            stadium_entry = stadium_o.create_stadium_entry(stadium_dict=stadium_dict)
            place.db.session.add(stadium_entry)
            place.db.session.commit()
            stadium_id = stadium_o.find_id_in_stadium_table(stadium_dict=stadium_dict)
        return stadium_id
    
    def input_affiliated_teams(self, main_team, affiliated_team):
        affiliated_team_o = affiliated_teams.CreateAffiliatedTeamsTableEntry()
        a_teams_id = affiliated_team_o.find_id_in_affiliated_teams_table(team_1_id=affiliated_team,
                                                                    team_2_id=main_team)
        if a_teams_id is not None:
            return a_teams_id
        a_teams_id = affiliated_team_o.find_id_in_affiliated_teams_table(team_1_id=main_team,
                                                                    team_2_id=affiliated_team)
        if a_teams_id is not None:
            return a_teams_id        
        affiliated_team_entry = affiliated_team_o.create_affiliated_teams_entry(team_main=main_team, 
                                                                                    team_affiliated=affiliated_team)
        affiliated_teams.db.session.add(affiliated_team_entry)
        affiliated_teams.db.session.commit()
        a_teams_id = affiliated_team_o.find_id_in_affiliated_teams_table(team_1_id=main_team,
                                                                    team_2_id=affiliated_team)
        return a_teams_id
    

    def input_retired_number_data(self, team_id, player_id, number):
        retired_number_o =  retired_number.CreateRetiredNumberTableEntry()
        retired_number_id = retired_number_o.find_id_in_retired_number_table(team_id=team_id,
                                                                             player_id=player_id,
                                                                             number=number)
        if retired_number_id is None:
            retired_number_entry = retired_number_o.create_retired_number_entry(team_id=team_id,
                                                                        player_id=player_id,
                                                                        number=number)
            place.db.session.add(retired_number_entry)
            place.db.session.commit()
            retired_number_id = retired_number_o.find_id_in_retired_number_table(team_id=team_id,
                                                                          player_id=player_id,
                                                                          number=number)
        return retired_number_id
    
    def input_team_name(self, name, min, max, team_id):
        team_name_o = team_name.CreateTeamNameEntry()
        season_id_min = self.input_season_data(season_name=min)
        season_id_max = self.input_season_data(season_name=max)
        team_name_id = team_name_o.find_id_in_team_name_table(team_name=name,
                                                              min=season_id_min,
                                                              max=season_id_max, 
                                                              team_id=team_id)
        if team_name_id is None:
            team_name_entry = team_name_o.create_team_name_entry(team_name=name,
                                                              min=season_id_min,
                                                              max=season_id_max, 
                                                              team_id=team_id)
            team_name.db.session.add(team_name_entry)
            team_name.db.session.commit()
            team_name_id = team_name_o.find_id_in_team_name_table(team_name=name,
                                                              min=season_id_min,
                                                              max=season_id_max, 
                                                              team_id=team_id)
        return team_name_id
    
    
    def input_colour(self, colour_name):
        colour_o = colour.CreateColourTableEntry()
        colour_id = colour_o.find_id_in_colour_table(colour=colour_name)
        if colour_id is None:
            colour_entry = colour_o.create_colour_entry(colour=colour_name)
            colour.db.session.add(colour_entry)
            colour.db.session.commit()
            colour_id = colour_o.find_id_in_colour_table(colour=colour_name)
        return colour_id

    def input_colour_team(self, team_id, colour):
        team_colour_o = team_colour.CreateTeamColourTableEntry()
        colour_id = self.input_colour(colour_name=colour)
        team_colour_id = team_colour_o.find_id_in_team_colour_table(team_id=team_id, colour_id=colour_id)
        if team_colour_id is None:
            team_colour_entry = team_colour_o.create_team_colour_entry(team_id=team_id, colour_id=colour_id)
            team_colour.db.session.add(team_colour_entry)
            team_colour.db.session.commit()
            team_colour_id = team_colour_o.find_id_in_team_colour_table(team_id=team_id, colour_id=colour_id)
        return team_colour_id





            

    

    

    
    


