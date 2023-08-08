import database.create_database.database_creator as db

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