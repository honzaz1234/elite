import database.create_database.database_creator as db

class CreateSeasonTableEntry:

    def __init__(self):
        pass

    def create_season_entry(self, season_name):
        season_query = db.Season(season=season_name)
        return season_query
    
    def find_id_in_season_table(self, season_name):
        row_data = db.session.query(db.Season.id).filter_by(season=season_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id        
        
