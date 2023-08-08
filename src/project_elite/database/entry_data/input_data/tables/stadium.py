import database.create_database.database_creator as db

class CreateStadiumEntry():

    def __init__(self):
        pass

    def create_stadium_entry(self, stadium_dict):
        stadium_entry = db.Stadium(stadium=stadium_dict["arena_name"],
                                   capacity=stadium_dict["capacity"],
                                   construction_year=stadium_dict["construction_year"],
                                   place_id=stadium_dict["place_id"])
        return stadium_entry
    
    def find_id_in_stadium_table(self, stadium_dict):
        row_data = db.session.query(db.Stadium.id).filter_by(stadium=stadium_dict["arena_name"],
                                                            capacity=stadium_dict["capacity"],
                                                            construction_year=stadium_dict["construction_year"],
                                                            place_id=stadium_dict["place_id"]).first()
        if row_data is None:
            return None
        else:
            return row_data.id      
