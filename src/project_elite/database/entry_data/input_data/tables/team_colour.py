import database.create_database.database_creator as db

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