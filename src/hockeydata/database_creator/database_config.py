import hockeydata.database_creator.database_creator as db
import hockeydata.database_creator.storage_database_creator as storage_db


TABLE_CONFIG = {
        db.Match: {
            "index_update": [
                db.Match.match_id.name,
                db.Match.season_id.name
            ]
        },
        db.Play: {
            "index_update": [
                db.Play.play_type_id.name,
                db.Play.match_id.name,
                db.Play.period.name,
                db.Play.time.name
            ]
        },
        db.PlayerShift: {
            "index_update": [
                db.PlayerShift.match_id.name,
                db.PlayerShift.player_id.name,
                db.PlayerShift.team_id.name,
                db.PlayerShift.period.name,
                db.PlayerShift.shift_start.name,
                db.PlayerShift.shift_end.name
            ]
        },
        db.PlayerOnIce: {
            "index_update": [
                db.PlayerOnIce.play_id.name,
                db.PlayerOnIce.player_id.name,
                db.PlayerOnIce.team_id.name,
            ]
        },
        db.NHLEliteNameMapper: {
            "index_update": [
                db.NHLEliteNameMapper.player_id.name,
                db.NHLEliteNameMapper.elite_name.name,
                db.NHLEliteNameMapper.nhl_name.name,
                db.NHLEliteNameMapper.team_id.name,
                db.NHLEliteNameMapper.season_id.name,
                db.NHLEliteNameMapper.player_number.name,
            ]
        },
        db.StadiumMapper: {
            "index_update": [
                db.StadiumMapper.nhl_name.name,
                db.StadiumMapper.elite_name.name,
            ]
        },
        # Specific play-type tables (all keyed by play_id unless specified)
        db.GoalPlay: {
            "index_update": [db.GoalPlay.play_id.name]
        },
        db.AssistPlay: {
            "index_update": [
                db.AssistPlay.goal_id.name,
                db.AssistPlay.player_id.name,
                db.AssistPlay.is_primary.name,
            ]
        },
        db.ShotPlay: {
            "index_update": [db.ShotPlay.play_id.name]
        },
        db.MissedShotPlay: {
            "index_update": [db.MissedShotPlay.play_id.name]
        },
        db.BlockedShotPlay: {
            "index_update": [db.BlockedShotPlay.play_id.name]
        },
        db.HitPlay: {
            "index_update": [db.HitPlay.play_id.name]
        },
        db.FaceoffPlay: {
            "index_update": [db.FaceoffPlay.play_id.name]
        },
        db.GiveawayPlay: {
            "index_update": [db.GiveawayPlay.play_id.name]
        },
        db.TakeawayPlay: {
            "index_update": [db.TakeawayPlay.play_id.name]
        },
        db.PenaltyPlay: {
            "index_update": [db.PenaltyPlay.play_id.name]
        },
        db.ChallengePlay: {
            "index_update": [db.ChallengePlay.play_id.name]
        },
        db.DelayedPenaltyPlay: {
            "index_update": [db.DelayedPenaltyPlay.play_id.name]
        },
        db.PeriodPlay: {
            "index_update": [db.PeriodPlay.play_id.name]
        },
        db.GameStopagePlay: {
            "index_update": [db.GameStopagePlay.play_id.name],
        },
        db.PlayType: {
            "index_update": [db.PlayType.play_type.name],
        },
        db.ShotType: {
            "index_update": [db.ShotType.shot_type.name],
        },
        db.ZoneType: {
            "index_update": [db.ZoneType.zone_type.name],
        },
        db.ShotResult: {
            "index_update": [db.ShotResult.shot_result.name],
        },
        db.PenaltyType: {
            "index_update": [db.PenaltyType.penalty_type.name],
        },
        db.DeflectionType: {
            "index_update": [db.DeflectionType.deflection_type.name],
        },
        db.BlockerType: {
            "index_update": [db.BlockerType.blocker_type.name],
        },
        db.ChallengeReason: {
            "index_update": [db.ChallengeReason.challenge_reason.name],
        },
        db.ChallengeResult: {
            "index_update": [db.ChallengeResult.challenge_result.name],
        },
        db.TimeZone: {
            "index_update": [db.TimeZone.time_zone.name],
        },
        db.PeriodType: {
            "index_update": [db.PeriodType.period_type.name],
        },
        db.GameStopageType: {
            "index_update": [db.GameStopageType.stopage_type.name],
        },
        db.BrokenPOI: {
            "index_update": [db.BrokenPOI.play_id.name],
        },
        db.BrokenPBP: {
        "index_update": [db.BrokenPOI.play_id.name],
        },
        db.Season: {
        "index_update": [db.Season.season.name],
        },
        db.NHLEliteNameMapper: {
        "index_update": [
            db.NHLEliteNameMapper.player_id.name,
            db.NHLEliteNameMapper.nhl_name.name,
            db.NHLEliteNameMapper.elite_name.name,
            db.NHLEliteNameMapper.team_id.name,
            db.NHLEliteNameMapper.season_id.name,
            db.NHLEliteNameMapper.player_number.name
            ],
        },
        db.StadiumMapper: {
        "index_update": [
            db.StadiumMapper.nhl_name.name,
            db.StadiumMapper.elite_name.name
            ],
        },
    }


STORAGE_TABLE_CONFIG = {
    storage_db.Season: {
        "index_update": [storage_db.Season.season],
    },
    storage_db.ScrapeType: {
        "index_update": [storage_db.ScrapeType.scrape_type],
    },
    storage_db.LeagueInfo: {
        "index_update": [
            storage_db.LeagueInfo.uid,
        ],
    },
    storage_db.GoalieStats: {
        "index_update": [
            storage_db.GoalieStats.player_id,
            storage_db.GoalieStats.competition_type,
            storage_db.GoalieStats.season_type,
        ],
    },
    storage_db.PlayerMissingDataLog: {
        "index_update": [
            storage_db.PlayerMissingDataLog.player_id,
            storage_db.PlayerMissingDataLog.data_type,
        ],
    },
    storage_db.LeagueLog: {
        "index_update": [
            storage_db.LeagueLog.scrape_id,
            storage_db.LeagueLog.league_id,
        ],
    },
    storage_db.LeagueMissingDataLog: {
        "index_update": [
            storage_db.LeagueMissingDataLog.league_id,
            storage_db.LeagueMissingDataLog.data_type,
        ],
    },
    storage_db.URLType: {
        "index_update": [storage_db.URLType.url_type],
    },
    storage_db.PlayerURL: {
        "index_update": [
            storage_db.PlayerURL.url,
            storage_db.PlayerURL.scrape_id,
            storage_db.PlayerURL.season_id,
            storage_db.PlayerURL.league_id,
            ],
    },
}
