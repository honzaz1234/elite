import database_creator.database_creator as db


QUERIES_INFO = {
    "nhl_season_players": {
        "base_table": db.PlayerStats,
        "selected_cols": [
            db.PlayerStats.player_id,
            db.Player.name.label("player_name"),
            db.PlayerStats.team_id,
            db.Team.team,
            db.Season.season
            ],
        "joins": [
            (db.Player, db.PlayerStats.player_id == db.Player.id),
            (db.Team, db.PlayerStats.team_id == db.Team.id),
            (db.Season, db.PlayerStats.season_id == db.Season.id),
            (db.League, db.PlayerStats.league_id == db.League.id),
            ],
        "filters": [
            (db.League.uid == 'nhl')
            ]
    },
    "nhl_season_goalies": {
        "base_table": db.GoalieStats,
        "selected_cols": [
            db.GoalieStats.player_id,
            db.Player.name.label("player_name"),
            db.GoalieStats.team_id,
            db.Team.team,
            db.Season.season
            ],
        "joins": [
            (db.Player, db.GoalieStats.player_id == db.Player.id),
            (db.Team, db.GoalieStats.team_id == db.Team.id),
            (db.Season, db.GoalieStats.season_id == db.Season.id),
            (db.League, db.GoalieStats.league_id == db.League.id),
            ],
        "filters": [
            (db.League.uid == 'nhl')
            ]
    },
    "draft_data": {
        "base_table": db.PlayerStats,
        "selected_cols": [
            db.PlayerStats.player_id,
            db.Player.name.label("player_name"),
            db.PlayerStats.regular_season,
            db.PlayerStats.team_id,
            db.Team.team,
            db.Season.season,
            db.PlayerStats.games_played,
            db.PlayerStats.goals,
            db.PlayerStats.assists,
            db.PlayerStats.total_points,
            db.PlayerStats.plus_minus,
            db.PlayerDraft.draft_position,
            db.PlayerDraft.draft_round,
            db.PlayerDraft.draft_year
            ],
        "joins": [
            (db.Player, db.PlayerStats.player_id == db.Player.id),
            (db.Team, db.PlayerStats.team_id == db.Team.id),
            (db.Season, db.PlayerStats.season_id == db.Season.id),
            (db.PlayerDraft, db.Player.id == db.PlayerDraft.player_id),
            (db.League, db.PlayerStats.league_id == db.League.id),
            ],
        "filters": [
            (db.League.uid == 'nhl')
            ]
    },

}