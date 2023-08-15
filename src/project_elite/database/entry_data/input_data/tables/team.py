import database.create_database.database_creator as db
from sqlalchemy import update

class CreateTeamTableEntry:


    def __init__(self):
        pass


    def create_team_entry(self, gi_dict):
        team_entry = db.Team(u_id=gi_dict["u_id"], 
                             team = gi_dict["short_name"],
                              team_long_name = gi_dict["full_name"],
                              active=gi_dict["active"],
                               place_id = gi_dict["place_id"], 
                               founded=gi_dict["founded"],
                               stadium_id=gi_dict["stadium_id"])
        return team_entry
    
    def update_team_entry(self, gi_dict):
        update_query = update(db.Team).where(db.Team.u_id == gi_dict["u_id"]).values(team = gi_dict["short_name"],
                                                                                    team_long_name = gi_dict["full_name"],
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
                              team_long_name = gi_dict["full_name"],
                              active=gi_dict["active"],
                               place_id = gi_dict["place_id"], 
                               founded=gi_dict["founded"],
                               stadium_id=gi_dict["stadium_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id
                
    def insert_uid_team_entry(self, u_id_1):
         team_entry = db.Team(u_id = u_id_1, 
                              team = None,
                              team_long_name = None,
                              active=None,
                               place_id = None, 
                               founded=None,
                               stadium_id=None)
         return team_entry

