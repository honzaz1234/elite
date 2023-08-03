import database.create_database.database_creator as db

class CreateAchievementPlayerTableEntry:

    def __init__(self):
        pass


    def create_achievement_player_entry(self, achievement_id, player_id, season_id):
        achievement_entry = db.PlayerAchievement(player_id=player_id, achievement_id=achievement_id, season_id=season_id)
        return achievement_entry

    def find_id_in_achievement_player_table(self, achievement_id, player_id, season_id):
        row_data =  db.session.query(db.PlayerAchievement.id).filter_by(player_id=player_id, achievement_id=achievement_id, season_id=season_id).first()
        if row_data is None:
            return None
        else:
            return row_data.id