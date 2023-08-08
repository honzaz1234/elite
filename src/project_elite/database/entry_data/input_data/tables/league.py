import database.create_database.database_creator as db

class CreateLeagueTableEntry:



    def __init__(self):
        pass


    def find_id_in_league_table(self, league_uid):
        row_data =  db.session.query(db.League.id).filter_by(league_elite=league_uid).first()
        if row_data is None:
            return None
        else:
            return row_data.id
        
    def create_league_entry(self, league_uid):
        league_entry = db.League(league_elite=league_uid, country=None, league=None)
        return league_entry
    
    def insert_uid_league_entry(self, league_uid):
         team_entry = db.League(league_elite = league_uid)
         return team_entry