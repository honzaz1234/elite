import database.entry_data.input_data.tables.player as player_table
import database.entry_data.input_data.tables.team as team_table
import database.entry_data.input_data.tables.league as league_table
import database.entry_data.input_data.tables.nationality as nationality_table
import database.entry_data.input_data.tables.stats as stats_table
import database.entry_data.input_data.tables.season as season_table
import database.entry_data.input_data.tables.achievement as achievement_table
import database.entry_data.input_data.tables.achievement_player as achievement_player_table
import database.entry_data.input_data.tables.place as place_table                  


class InputData:

    def __init__(self):
        pass

    def input_player_data(self, dict_info):
        u_id = dict_info["u_id"]
        player_o = player_table.CreatePlayerTableEntry()
        player_id = player_o.check_if_id_exists_in_table_player(u_id)
        if player_id == None:
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
            player_table.db.session.add(player_entry)
            player_table.db.session.commit()
        player_id = player_o.check_if_id_exists_in_table_player(u_id)
        return player_id
    
    def input_nationality_data(self, nationality_name):
        if nationality_name is None:
            return None
        nationality_o = nationality_table.CreateNationalityTableEntry()
        nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        if nationality_id is None:
            nationality_entry= nationality_o.create_nationality_entry(nationality_name=nationality_name)
            nationality_table.db.session.add(nationality_entry)
            nationality_table.db.session.commit()
            nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        return nationality_id
    
    def input_team_data(self, team_name):
        if team_name is None:
            return None
        team_o = team_table.CreateTeamTableEntry()
        team_id = team_o.find_id_in_team_table(team_name=team_name)
        if team_id is None:
            team_entry = team_o.create_team_entry(team_name=team_name)
            team_table.db.session.add(team_entry)
            team_table.db.session.commit()
            team_id = team_o.find_id_in_team_table(team_name=team_name)
        return team_id


    def input_league_data(self, league_name):
        if league_name is None:
            return None
        league_o = league_table.CreateLeagueTableEntry()
        league_id = league_o.find_id_in_league_table(league_name=league_name)
        if league_id is None:
            league_entry = league_o.create_league_entry(league_name=league_name)
            league_table.db.session.add(league_entry)
            league_table.db.session.commit()
            league_id = league_o.find_id_in_league_table(league_name=league_name)
        return league_id
    
    def input_player_stats_data(self, dict_info, season_dict):
        dict_info["team_id"] = self.input_team_data(team_name=dict_info["team_name"])
        dict_info["league_id"] = self.input_league_data(league_name=dict_info["league_name"])
        dict_info["season_id"] = self.input_season_data(season_name=dict_info["season_name"])
        season_o = stats_table.CreateStatsTableEntry()
        if dict_info["is_goalie"] == True:
            stat_id = season_o.find_id_in_goalie_stats_table(dict_info=dict_info)
        else:
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        if stat_id is not None:
            return stat_id
        if dict_info["is_goalie"] == True:
            season_entry = season_o.create_season_goalie_entry(dict_info=dict_info, dict_season=season_dict)
            stats_table.db.session.add(season_entry)
            stats_table.db.session.commit()
            stat_id = season_o.find_id_in_goalie_stats_table( dict_info=dict_info)
        else:
            season_entry = season_o.create_season_player_entry(dict_info=dict_info, dict_season=season_dict)
            stats_table.db.session.add(season_entry)
            stats_table.db.session.commit()
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        return stat_id
    
    def input_achievement_relation(self, player_id, achievement_name, season_name):
        achievement_id = self.input_achievement(achievement_name=achievement_name)
        season_id = self.input_season_data(season_name=season_name)
        achievement_player_o = achievement_player_table.CreateAchievementPlayerTableEntry()
        achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        if achievement_player_id is None:
            achievement_player_entry = achievement_player_o.create_achievement_player_entry(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
            achievement_player_table.db.session.add(achievement_player_entry)
            achievement_player_table.db.session.commit()
            achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        return achievement_player_id

    def input_achievement(self, achievement_name):
        achievement_o = achievement_table.CreateAchievementTableEntry()
        achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        if achievement_id is None:
            achievement_entry = achievement_o.create_achievement_entry(achievement_name=achievement_name)
            achievement_table.db.session.add(achievement_entry)
            achievement_table.db.session.commit()
            achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        return achievement_id

    def input_place_data(self, place_name, region_name, country_name):
        if place_name is None and region_name is None and country_name is None:
            return None
        place_o = place_table.CreatePlaceTableEntry()
        place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        if place_id is None:
            place_entry = place_o.create_place_entry(place_name=place_name, region_name=region_name, country_name=country_name)
            place_table.db.session.add(place_entry)
            place_table.db.session.commit()
            place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        return place_id
    

    def input_season_data(self, season_name):
        season_o = season_table.CreateSeasonTableEntry()
        season_id = season_o.find_id_in_season_table(season_name=season_name)
        if season_id is None:
            season_entry = season_o.create_season_entry(season_name=season_name)
            season_table.db.session.add(season_entry)
            season_table.db.session.commit()
            season_id = season_o.find_id_in_season_table(season_name=season_name)
        return season_id

    
    


