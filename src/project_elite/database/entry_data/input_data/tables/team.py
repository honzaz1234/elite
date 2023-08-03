import database.create_database.database_creator as db

class CreateTeamTableEntry:


    def __init__(self):
        pass




    def create_team_entry(self, team_name, place_id=None,  team_colours=None, founded=None):
        team_entry = db.Team(team=team_name, place_id = place_id, team_colours=team_colours, founded=founded)
        return team_entry
            
    def find_id_in_team_table(self, team_name):
        row_data =  db.session.query(db.Team.id).filter_by(team=team_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id

