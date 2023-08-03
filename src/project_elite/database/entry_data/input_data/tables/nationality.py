import database.create_database.database_creator as db

class CreateNationalityTableEntry:



    def __init__(self):
        pass

    def create_nationality_entry(self, nationality_name):
        nationality_entry = db.Nationality(nationality=nationality_name)
        return nationality_entry

    def find_id_in_nationality_table(self, nationality_name):
        row_data =  db.session.query(db.Nationality.id).filter_by(nationality=nationality_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id