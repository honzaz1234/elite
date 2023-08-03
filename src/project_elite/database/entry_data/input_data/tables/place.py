import database.create_database.database_creator as db

class CreatePlaceTableEntry:

    def __init__(self):
        pass

    def create_place_entry(self, place_name, region_name, country_name):
        place_entry = db.Place(place=place_name, region=region_name, country_s=country_name)
        return place_entry

    def find_id_in_place_table(self, place_name, region_name, country_name):
        row_data =  db.session.query(db.Place.id).filter_by(place=place_name, region=region_name, country_s=country_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id