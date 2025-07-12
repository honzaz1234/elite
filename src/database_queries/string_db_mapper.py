import database_creator.database_creator as db


MODEL_MAP = {
    "Player": db.Player,
    "PlayerStats": db.PlayerStats,
    "Team": db.Team,
    "Season": db.Season,
    "PlayerDraft": db.PlayerDraft,
    "League": db.League,
    "PlayerNationality": db.PlayerNationality,
    "Nationality": db.Nationality
}