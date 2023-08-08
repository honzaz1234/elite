import database.create_database.database_creator as db

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
