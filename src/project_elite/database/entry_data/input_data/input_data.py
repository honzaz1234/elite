import database.entry_data.input_data.tables.tables as tables_o
              
class InputData:

    def __init__(self):
        pass


    def input_player_uid(self, u_id):
        player_o = tables_o.CreatePlayerTableEntry()
        player_id = player_o.check_if_id_exists_in_table_player(u_id_1=u_id)
        if player_id is None:
            player_entry = player_o.insert_uid_player_entry(u_id_1=u_id)
            tables_o.db.session.add(player_entry)
            tables_o.db.session.commit()
            player_id = player_o.check_if_id_exists_in_table_player(u_id_1=u_id)
        return player_id
    
    def input_team_uid(self, u_id):
        team_o = tables_o.CreateTeamTableEntry()
        team_id = team_o.find_id_in_team_table(u_id_1=u_id)
        if team_id is None:
            team_entry = team_o.insert_uid_team_entry(u_id_1=u_id)
            tables_o.db.session.add(team_entry)
            tables_o.db.session.commit()
            team_id = team_o.find_id_in_team_table(u_id_1=u_id)
        return team_id
    
    def input_league_uid(self, league_uid):
        league_o = tables_o.CreateLeagueTableEntry()
        league_id = league_o.find_id_in_league_table(league_uid=league_uid)
        if league_id is None:
            league_entry = league_o.insert_uid_league_entry(league_uid=league_uid)
            tables_o.db.session.add(league_entry)
            tables_o.db.session.commit()
            league_id = league_o.find_id_in_league_table(league_uid=league_uid)
        return league_id


    def input_player_data(self, dict_info, status):
        u_id = dict_info["u_id"]
        player_o = tables_o.CreatePlayerTableEntry()
        if status == "insert_uid":
            insert_uid_entry = player_o.insert_uid_player_entry(dict_info["u_id"])            
            tables_o.db.session.add(insert_uid_entry)
            tables_o.db.session.commit()
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
        tables_o.db.session.add(player_entry)
        tables_o.db.session.commit()
        player_id = player_o.check_if_id_exists_in_table_player(u_id)
        return player_id
    
    def input_nationality_data(self, nationality_name):
        if nationality_name is None:
            return None
        nationality_o = tables_o.CreateNationalityTableEntry()
        nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        if nationality_id is None:
            nationality_entry= nationality_o.create_nationality_entry(nationality_name=nationality_name)
            tables_o.db.session.add(nationality_entry)
            tables_o.db.session.commit()
            nationality_id = nationality_o.find_id_in_nationality_table(nationality_name=nationality_name)
        return nationality_id
    
    def input_team_data(self, general_info_dict):
        team_o = tables_o.CreateTeamTableEntry()
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
            tables_o.db.session.add(insert_entry)
            tables_o.db.session.commit()
            team_id = team_o.find_id_in_team_table(u_id_1=general_info_dict["u_id"])
        else:
            general_info_dict["id"] = team_id
            update_entry = team_o.update_team_entry(gi_dict=general_info_dict)                                          
            tables_o.db.session.execute(update_entry)
            tables_o.db.session.commit()
        return team_id

    def input_league_data(self, u_id, long_name):
        league_o = tables_o.CreateLeagueTableEntry()
        league_id = league_o.find_id_in_league_table(league_uid=u_id)
        if league_id is None:
            league_entry = league_o.create_league_entry(league_uid=u_id, long_name=long_name)
            tables_o.db.session.add(league_entry)
            tables_o.db.session.commit()
            league_id = league_o.find_id_in_league_table(league_uid=u_id)
        else:
            update_entry = league_o.update_league_entry(league_uid=u_id, long_name=long_name)
            tables_o.db.session.execute(update_entry)
            tables_o.db.session.commit()
        return league_id
    
    def input_player_stats_data(self, dict_info, season_dict):
        dict_info["team_id"] = self.input_team_data(team_name=dict_info["team_name"])
        dict_info["league_id"] = self.input_league_data(league_name=dict_info["league_name"])
        dict_info["season_id"] = self.input_season_data(season_name=dict_info["season_name"])
        season_o = tables_o.CreateStatsTableEntry()
        if dict_info["is_goalie"] == True:
            stat_id = season_o.find_id_in_goalie_stats_table(dict_info=dict_info)
        else:
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        if stat_id is not None:
            return stat_id
        if dict_info["is_goalie"] == True:
            season_entry = season_o.create_season_goalie_entry(dict_info=dict_info, dict_season=season_dict)
            tables_o.db.session.add(season_entry)
            tables_o.db.session.commit()
            stat_id = season_o.find_id_in_goalie_stats_table( dict_info=dict_info)
        else:
            season_entry = season_o.create_season_player_entry(dict_info=dict_info, dict_season=season_dict)
            tables_o.db.session.add(season_entry)
            tables_o.db.session.commit()
            stat_id = season_o.find_id_in_player_stats_table(dict_info=dict_info)
        return stat_id
    
    def input_achievement_relation(self, player_id, achievement_name, season_name):
        achievement_id = self.input_achievement(achievement_name=achievement_name)
        season_id = self.input_season_data(season_name=season_name)
        achievement_player_o = tables_o.CreateAchievementPlayerTableEntry()
        achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        if achievement_player_id is None:
            achievement_player_entry = achievement_player_o.create_achievement_player_entry(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
            tables_o.db.session.add(achievement_player_entry)
            tables_o.db.session.commit()
            achievement_player_id = achievement_player_o.find_id_in_achievement_player_table(player_id=player_id, 
                                                                                          achievement_id=achievement_id, season_id=season_id)
        return achievement_player_id

    def input_achievement(self, achievement_name, league_id):
        achievement_o = tables_o.CreateAchievementTableEntry()
        achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        if achievement_id is None:
            achievement_entry = achievement_o.create_achievement_entry(achievement_name=achievement_name, league_id=league_id)
            tables_o.db.session.add(achievement_entry)
            tables_o.db.session.commit()
            achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        else:
            update_entry = achievement_o.update_achievement_entry(achievement_name=achievement_name, league_id=league_id)
            tables_o.db.session.execute(update_entry)
            tables_o.db.session.commit()
            achievement_id = achievement_o.find_id_in_achievement_table(achievement_name=achievement_name)
        return achievement_id

    def input_place_data(self, place_name, region_name, country_name):
        if place_name is None and region_name is None and country_name is None:
            return None
        place_o = tables_o.CreatePlaceTableEntry()
        place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        if place_id is None:
            place_entry = place_o.create_place_entry(place_name=place_name, region_name=region_name, country_name=country_name)
            tables_o.db.session.add(place_entry)
            tables_o.db.session.commit()
            place_id = place_o.find_id_in_place_table(place_name=place_name, region_name=region_name, country_name=country_name)
        return place_id
    

    def input_season_data(self, season_name):
        season_o = tables_o.CreateSeasonTableEntry()
        season_id = season_o.find_id_in_season_table(season_name=season_name)
        if season_id is None:
            season_entry = season_o.create_season_entry(season_name=season_name)
            tables_o.db.session.add(season_entry)
            tables_o.db.session.commit()
            season_id = season_o.find_id_in_season_table(season_name=season_name)
        return season_id
    
    def input_stadium_data(self, stadium_dict):
        stadium_o =  tables_o.CreateStadiumEntry()
        place_dict = stadium_dict["place"]
        place_id = self.input_place_data(place_name=place_dict["place"],
                                                         region_name=place_dict["region"],
                                                         country_name=place_dict["country"])
        print(place_id)
        stadium_dict["place_id"] = place_id
        stadium_id = stadium_o.find_id_in_stadium_table(stadium_dict=stadium_dict)
        if stadium_id is None:
            stadium_entry = stadium_o.create_stadium_entry(stadium_dict=stadium_dict)
            tables_o.db.session.add(stadium_entry)
            tables_o.db.session.commit()
            stadium_id = stadium_o.find_id_in_stadium_table(stadium_dict=stadium_dict)
        return stadium_id
    
    def input_affiliated_teams(self, main_team, affiliated_team):
        affiliated_team_o = tables_o.CreateAffiliatedTeamsTableEntry()
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
        tables_o.db.session.add(affiliated_team_entry)
        tables_o.db.session.commit()
        a_teams_id = affiliated_team_o.find_id_in_affiliated_teams_table(team_1_id=main_team,
                                                                    team_2_id=affiliated_team)
        return a_teams_id
    

    def input_retired_number_data(self, team_id, player_id, number):
        retired_number_o =  tables_o.CreateRetiredNumberTableEntry()
        retired_number_id = retired_number_o.find_id_in_retired_number_table(team_id=team_id,
                                                                             player_id=player_id,
                                                                             number=number)
        if retired_number_id is None:
            retired_number_entry = retired_number_o.create_retired_number_entry(team_id=team_id,
                                                                        player_id=player_id,
                                                                        number=number)
            tables_o.db.session.add(retired_number_entry)
            tables_o.db.session.commit()
            retired_number_id = retired_number_o.find_id_in_retired_number_table(team_id=team_id,
                                                                          player_id=player_id,
                                                                          number=number)
        return retired_number_id
    
    def input_team_name(self, name, min, max, team_id):
        team_name_o = tables_o.CreateTeamNameEntry()
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
            tables_o.db.session.add(team_name_entry)
            tables_o.db.session.commit()
            team_name_id = team_name_o.find_id_in_team_name_table(team_name=name,
                                                              min=season_id_min,
                                                              max=season_id_max, 
                                                              team_id=team_id)
        return team_name_id
    
    
    def input_colour(self, colour_name):
        colour_o = tables_o.CreateColourTableEntry()
        colour_id = colour_o.find_id_in_colour_table(colour=colour_name)
        if colour_id is None:
            colour_entry = colour_o.create_colour_entry(colour=colour_name)
            tables_o.db.session.add(colour_entry)
            tables_o.db.session.commit()
            colour_id = colour_o.find_id_in_colour_table(colour=colour_name)
        return colour_id

    def input_colour_team(self, team_id, colour):
        team_colour_o = tables_o.CreateTeamColourTableEntry()
        colour_id = self.input_colour(colour_name=colour)
        team_colour_id = team_colour_o.find_id_in_team_colour_table(team_id=team_id, colour_id=colour_id)
        if team_colour_id is None:
            team_colour_entry = team_colour_o.create_team_colour_entry(team_id=team_id, colour_id=colour_id)
            tables_o.db.session.add(team_colour_entry)
            tables_o.db.session.commit()
            team_colour_id = team_colour_o.find_id_in_team_colour_table(team_id=team_id, colour_id=colour_id)
        return team_colour_id
    
    def input_division_id(self, division, league_id):
        division_o = tables_o.CreateDivisionEntry()
        division_id = division_o.find_id_in_division_table(division=division)
        if division_id is None:
            division_entry = division_o.create_division_entry(division=division)
            tables_o.db.session.add(division_entry)
            tables_o.db.session.commit()
            division_id = division_o.find_id_in_division_table(division=division)
        return division_id
    
    def input_postseason_type_id(self, postseason_type):
        postseason_type_o = tables_o.CreatePostSeasonTypeEntry()
        postseason_type_id = postseason_type_o.find_id_in_postseason_type_table(postseason_type=postseason_type)
        if postseason_type_id is None:
            postseason_type_entry = postseason_type_o.create_postseason_type_entry(postseason_type=postseason_type)
            tables_o.db.session.add(postseason_type_entry)
            tables_o.db.session.commit()
            postseason_type_id = postseason_type_o.find_id_in_postseason_type_table(postseason_type=postseason_type)
        return postseason_type_id


    def input_team_season_data(self, ts_dict):
        team_season_o = tables_o.CreateTeamSeasonEntry()
        ts_dict["season_id"] = self.input_season_data(season_name=ts_dict["season"])
        ts_dict["division_id"] = self.input_division_id(division=ts_dict["type"], 
                                                        league_id=ts_dict["league_id"])
        ts_dict["postseason_type_id"] = self.input_postseason_type_id(postseason_type=ts_dict["postseason"])
        team_season_id = team_season_o.find_id_in_team_season_table(ts_dict=ts_dict)
        if team_season_id is None:
            team_season_entry = team_season_o.create_team_season_entry(ts_dict=ts_dict)
            tables_o.db.session.add(team_season_entry)
            tables_o.db.session.commit()
            team_season_id = team_season_o.find_id_in_team_season_table(ts_dict=ts_dict)
        return team_season_id







            

    

    

    
    


