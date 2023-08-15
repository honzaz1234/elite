import database.create_database.database_creator as db

class CreateColourTableEntry:

    def __init__(self):
        pass

    def create_colour_entry(self, colour):
        colour_entry = db.Colour(colour=colour)
        return colour_entry

    def find_id_in_colour_table(self, colour):
        row_data =  db.session.query(db.Colour.id).filter_by(colour=colour).first()
        if row_data is None:
            return None
        else:
            return row_data.id