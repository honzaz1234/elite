import hockeydata.database_creator.database_creator as db


MODEL_MAP = {
    "Player": db.Player,
    "PlayerStats": db.PlayerStats,
    "GoalieStats": db.GoalieStats,
    "Team": db.Team,
    "Season": db.Season,
    "PlayerDraft": db.PlayerDraft,
    "League": db.League,
    "PlayerNationality": db.PlayerNationality,
    "Nationality": db.Nationality,
    "GoalPlay": db.GoalPlay,
    "Play": db.Play,
    "Match": db.Match,
    "AssistPlay": db.AssistPlay,
    "PlayerShift": db.PlayerShift
}