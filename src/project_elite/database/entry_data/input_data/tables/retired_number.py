import database.create_database.database_creator as db

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

