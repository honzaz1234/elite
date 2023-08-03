import database.create_database.database_creator as db

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
                                 draft_round = dictd["draft_round"],
                                 draft_position = dictd["draft_position"],
                                 draft_year = dictd["draft_year"],
                                 height = dictd["height"],
                                 weight = dictd["weight"],
                                 youth_team_id = dict_fkeys["youth_team_id"],
                                 nhl_rights_id = dict_fkeys["nhl_team_rights_id"],
                                 draft_team_id = dict_fkeys["draft_team_id"],
                                 nation_id = dict_fkeys["nation_id"],
                                 place_birth_id = dict_fkeys["place_birth_id"]
                                 )
        return player_entry
        
    def check_if_id_exists_in_table_player(self, u_id_1):
        row_data = db.session.query(db.Player.id).filter_by(u_id = u_id_1).first()
        if row_data is None:
            return None
        else:
            return row_data.id

        
    def create_team_entry(self, team_name, dict_fkeys):
        team_entry = db.Team(team=team_name, 
                                 league_id=dict_fkeys["league_id"],
                                 country_id = dict_fkeys["country_id"])
        return team_entry
            



