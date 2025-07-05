import database_creator.database_creator as db


QUERIES_INFO = {
    "nhl_season_players": {
        "base_table": db.PlayerStats,
        "selected_cols": [
            db.PlayerStats.player_id,
            db.Player.name.label("player_name"),
            db.PlayerStats.team_id,
            db.Team.team,
            db.Team.uid,
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
            db.Team.uid,
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
    "nhl_teams": {
        "base_table": db.Team,
        "selected_cols": [
            db.Team.id,
            db.Team.team,
            db.League.uid
            ],
        "joins": [
            (db.TeamSeason, db.TeamSeason.team_id == db.Team.id),
            (db.Season, db.TeamSeason.season_id == db.Season.id),
            (db.League, db.TeamSeason.league_id == db.League.id)
        ],
        "filters": [
            (db.League.uid == "nhl")
        ]
    },
    "name_mapper": {
        "base_table": db.NHLEliteNameMapper,
        "selected_cols": [
            db.NHLEliteNameMapper.player_id,
             db.NHLEliteNameMapper.elite_name,
            db.NHLEliteNameMapper.nhl_name,
            db.NHLEliteNameMapper.player_number,
            db.NHLEliteNameMapper.team_id,
            db.Season.season,
            ],
        "joins": [
            (db.Season, db.NHLEliteNameMapper.season_id == db.Season.id),
            ],
        "filters": [
            ]
    },
    "nhl_teams": {
        "base_table": db.Team,
        "selected_cols": [
            db.Team.id,
            db.Team.team,
            db.League.uid
            ],
        "joins": [
            (db.TeamSeason, db.TeamSeason.team_id == db.Team.id),
            (db.Season, db.TeamSeason.season_id == db.Season.id),
            (db.League, db.TeamSeason.league_id == db.League.id)
        ],
        "filters": [
            (db.League.uid == "nhl")
        ]
    },
    "nhl_elite_names": {
        "base_table": db.NHLEliteNameMapper,
        "selected_cols": [
            db.NHLEliteNameMapper.elite_name,
            db.NHLEliteNameMapper.nhl_name,
            ],
        "joins": [
        ],
        "filters": [
        ]
    },
    "nhl_elite_stadium_mapper": {
        "base_table": db.StadiumMapper,
        "selected_cols": [
            db.StadiumMapper.nhl_name,
            db.StadiumMapper.elite_name,
        ]
    },
    "play_types": {
        "base_table": db.PlayType,
        "selected_cols": [
            db.PlayType.id,
            db.PlayType.play_type,
        ]
    },
    "shot_types": {
        "base_table": db.ShotType,
        "selected_cols": [
            db.ShotType.id,
            db.ShotType.shot_type,
        ]
    },
    "zone_types": {
        "base_table": db.ZoneType,
        "selected_cols": [
            db.ZoneType.id,
            db.ZoneType.zone_type,
        ]
    },
    "shot_results": {
        "base_table": db.ShotResult,
        "selected_cols": [
            db.ShotResult.id,
            db.ShotResult.shot_result,
        ]
    },
    "penalty_types": {
        "base_table": db.PenaltyType,
        "selected_cols": [
            db.PenaltyType.id,
            db.PenaltyType.penalty_type,
        ]
    },
    "deflection_types": {
        "base_table": db.DeflectionType,
        "selected_cols": [
            db.DeflectionType.id,
            db.DeflectionType.deflection_type,
        ]
    },
    "blocker_types": {
        "base_table": db.BlockerType,
        "selected_cols": [
            db.BlockerType.id,
            db.BlockerType.blocker_type,
        ]
    },
    "challenge_reasons": {
        "base_table": db.ChallengeReason,
        "selected_cols": [
            db.ChallengeReason.id,
            db.ChallengeReason.challenge_reason,
        ]
    },
    "challenge_results": {
        "base_table": db.ChallengeResult,
        "selected_cols": [
            db.ChallengeResult.id,
            db.ChallengeResult.challenge_result,
        ]
    },
    "time_zones": {
        "base_table": db.TimeZone,
        "selected_cols": [
            db.TimeZone.id,
            db.TimeZone.time_zone,
        ]
    },
    "period_types": {
        "base_table": db.PeriodType,
        "selected_cols": [
            db.PeriodType.id,
            db.PeriodType.period_type,
        ]
    },
    "game_stopage_types": {
        "base_table": db.GameStopageType,
        "selected_cols": [
            db.GameStopageType.id,
            db.GameStopageType.stopage_type,
        ]
    },
    "seasons": {
        "base_table": db.Season,
        "selected_cols": [
            db.Season.id,
            db.Season.season,
        ]
    },
    "firstname_mapper": {
        "base_table": db.FirstNameMapper,
        "selected_cols": [
            db.FirstNameMapper.name,
            db.FirstNameMapper.alternative_name,
        ]
    },
    "player_uid": {
        "base_table": db.Player,
        "selected_cols": [
            db.Player.uid,
        ],
        "filters": [
            (db.Player.name.isnot(None))
        ]
    }
}