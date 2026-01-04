import hockeydata.database_creator.database_creator as db
import hockeydata.database_creator.storage_database_creator as storage_db


QUERIES_INFO = {
    "storage_player_base_info": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.player_uid,
            storage_db.PlayerLog.is_goalie,
            storage_db.PlayerURL.player_url
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.PlayerURL, 
                "conn": storage_db.PlayerLog.player_uid == storage_db.PlayerURL.player_uid, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "storage_player_facts": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.player_uid,
            storage_db.PlayerFacts.html_data,
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.PlayerFacts, 
                "conn": storage_db.PlayerFacts.player_id == storage_db.PlayerLog.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "storage_achievements": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.player_uid,
            storage_db.Achievements.html_data,
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.Achievements, 
                "conn": storage_db.Achievements.player_id == storage_db.PlayerLog.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "storage_skater_stats": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.player_uid,
            storage_db.SkaterStats.league_type,
            storage_db.SkaterStats.html_data,
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.SkaterStats, 
                "conn": storage_db.SkaterStats.player_id == storage_db.PlayerLog.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "goalie_stats": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.player_uid,
            storage_db.GoalieStats.league_type,
            storage_db.GoalieStats.season_type,
            storage_db.GoalieStats.html_data,
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.GoalieStats, 
                "conn": storage_db.GoalieStats.player_id == storage_db.PlayerLog.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
}