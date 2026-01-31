import hockeydata.database_creator.storage_database_creator as storage_db


STORAGE_QUERIES = {
    "player_base_info": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.uid,
            storage_db.PlayerLog.is_goalie,
            storage_db.PlayerURL.url,
            storage_db.PlayerURL.scrape_id
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "player_facts": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.uid,
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
    "achievements": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.uid,
            storage_db.PlayerAchievements.html_data,
            ],
        "joins": [
            {
                "table": storage_db.PlayerLog, 
                "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
                "type": "inner"
            },
            {
                "table": storage_db.PlayerAchievements, 
                "conn": storage_db.PlayerAchievements.player_id == storage_db.PlayerLog.id, 
                "type": "inner"
            },
        ],
        "filters": [
            ]
    },
    "skater_stats": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.uid,
            storage_db.SkaterStats.competition_type,
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
            storage_db.PlayerLog.uid,
            storage_db.GoalieStats.competition_type,
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
    "player_uids": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerLog.uid,
            ],
        "joins": [
            {
            "table": storage_db.PlayerLog, 
            "conn": storage_db.PlayerLog.scrape_id == storage_db.Scrape.id, 
            "type": "inner"
            },
        ],
        "filters": [
        ]
    },
    "player_urls": {
        "base_table": storage_db.Scrape,
        "selected_cols": [
            storage_db.PlayerURL.url,
            ],
        "joins": [
            {
            "table": storage_db.PlayerLog, 
            "conn": storage_db.Scrape.id == storage_db.PlayerURL.scrape_id, 
            "type": "inner"
            },
        ],
        "filters": [
        ]
    },
    "year_range": {
        "base_table": storage_db.LeagueInfo,
        "selected_cols": [
            storage_db.LeagueInfo.first_season,
            storage_db.LeagueInfo.last_season,
            ],
        "joins": [
        ],
        "filters": [
        ]
    },
    "player_url_html": {
        "base_table": storage_db.PlayerURLHTML,
        "selected_cols": [
            storage_db.PlayerURLHTML.html_data,
            storage_db.PlayerURLHTML.season_id,
            storage_db.PlayerURLHTML.league_id,
            storage_db.PlayerURLHTML.scrape_id,
            storage_db.PlayerURLHTML.is_goalie,
            storage_db.LeagueInfo.uid,
            storage_db.Season.season,
            ],
        "joins": [
            {
            "table": storage_db.LeagueInfo, 
            "conn": storage_db.PlayerURLHTML.league_id == storage_db.LeagueInfo.id, 
            "type": "inner"
            },
            {
            "table": storage_db.Season, 
            "conn": storage_db.PlayerURLHTML.season_id == storage_db.Season.id, 
            "type": "inner"
            },
        ],
        "filters": [
        ]
    },
        "season_mapper": {
        "base_table": storage_db.Season,
        "selected_cols": [
            storage_db.Season.season,
            storage_db.Season.id
            ],
        "joins": [
        ],
        "filters": [
        ]
    },
}