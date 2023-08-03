import database.create_database.database_creator as db

class CreateAchievementTableEntry:



    def __init__(self):
        pass


    def create_achievement_entry(self, achievement_name, league_id=None):
        achievement_entry = db.Achievement(achievement=achievement_name, league_id=league_id)
        return achievement_entry

    def find_id_in_achievement_table(self, achievement_name):
        row_data =  db.session.query(db.Achievement.id).filter_by(achievement=achievement_name).first()
        if row_data is None:
            return None
        else:
            return row_data.id