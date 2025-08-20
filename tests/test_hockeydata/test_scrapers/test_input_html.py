import pytest
import pdb

from pathlib import Path

from database_session.database_session import GetDatabaseSession
from hockeydata.entity_data.input_html import PlayerHTMLInputter
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data" 
def load_html(file_name: str) -> str:
    return (DATA_DIR / file_name).read_text(encoding="utf-8")


PLAYER_UID = {
    "dostal": 236340,
    "hasek": 8665,
    "howe": 20605,
    "mcdavid": 183442,
    }


@pytest.fixture(scope="function")
def test_storage_db_session():
    current_dir = Path(__file__).parent
    db_path = current_dir / "data/test_storage_db.db" 
    session_o = GetDatabaseSession(db_path=str(db_path))
    session_o.set_up_connection()
    yield session_o.session
    session_o.session.close()
    session_o.engine.dispose()


@pytest.fixture(scope="session")
def player_html():
    folder = Path(__file__).parent / "data"
    return {
        file.stem: file.read_text(encoding="utf-8")
        for file in folder.glob("*.html")
    }
    

@pytest.fixture(scope="function")
def get_player_html_dict(player_html, player_info):
    player_type = player_info["player_type"]
    player_name = player_info["player_name"]

    base_dict = {
        "player_facts": player_html[f"{player_name}_player_facts"],
        "achievements": player_html[f"{player_name}_achievements"],
        "type": player_type,
        "player_uid": PLAYER_UID[player_name]
    }

    if player_type == "goalie":
        base_dict.update({
            "stats_league_playoff": player_html[f"{player_name}_stats_league_play_off"],
            "stats_league_regular": player_html[f"{player_name}_stats_league_regular"],
            "stats_tournament_playoff": player_html[f"{player_name}_stats_tournament_play_off"],
            "stats_tournament_regular": player_html[f"{player_name}_stats_tournament_regular"],
        })
    elif player_type == "skater":
        base_dict.update({
            "stats_league": player_html[f"{player_name}_stats_league"],
            "stats_tournament": player_html[f"{player_name}_stats_tournament"],
        })
    else:
        raise ValueError(f"Unknown player_type for {player_name}: {player_type}")

    return base_dict


@pytest.fixture(scope="function")
def get_scrape_info(get_player_html_dict):

    return (1, get_player_html_dict)


@pytest.fixture(scope="function")
def create_player_html_inputter(test_storage_db_session, get_scrape_info):
    scrape_id, scraped_data = get_scrape_info

    return PlayerHTMLInputter(
        db_session=test_storage_db_session, 
        scraped_data=scraped_data,
        scrape_id=scrape_id
        )


def get_player_dict(session, player_id: int):
    # Base player data
    base_sql = """
        SELECT 
            Player.id,
            Player.player_uid,
            Player.is_goalie,
            Player.scrape_id,
            PlayerFacts.html_data AS facts_html,
            Achievements.html_data as achievements_html
        FROM Player
        LEFT JOIN PlayerFacts ON Player.id = PlayerFacts.player_id
        LEFT JOIN Achievements ON Player.id = Achievements.player_id
        WHERE Player.id = :player_id
    """
    base_data = session.execute(base_sql, {"player_id": player_id}).mappings().first()

    if not base_data:
        return None

    player_dict = {"base_player_html_data": dict(base_data)}

    if base_data["is_goalie"]:
        # Goalie stats
        goalie_sql = """
            SELECT
                Player.id,
                GoalieStats.league_type,
                GoalieStats.season_type,
                GoalieStats.html_data
            FROM Player
            LEFT JOIN GoalieStats ON Player.id = GoalieStats.player_id
            WHERE Player.id = :player_id
        """
        goalie_stats = session.execute(goalie_sql, {"player_id": player_id}).mappings().all()
        player_dict["goalie_stats"] = [dict(row) for row in goalie_stats]
    else:
        # Skater stats
        skater_sql = """
            SELECT
                Player.id,
                SkaterStats.league_type,
                SkaterStats.html_data
            FROM Player
            LEFT JOIN SkaterStats ON Player.id = SkaterStats.player_id
            WHERE Player.id = :player_id
        """
        skater_stats = session.execute(skater_sql, {"player_id": player_id}).mappings().all()
        player_dict["skater_stats"] = [dict(row) for row in skater_stats]

    return player_dict


class TestPlayerHTMLInputter():


    @pytest.mark.parametrize(
        "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "goalie"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["dostal"],
                        "is_goalie": True,
                        "scrape_id": 1,
                        "facts_html": load_html("dostal_player_facts.html"),
                        "achievements": load_html("dostal_achievements.html"),
                    },
                    "goalie_stats": [
                        {"id": 1, "league_type": "league", "season_type": "regular",
                        "html_data": load_html("dostal_stats_league_regular.html")},
                        {"id": 1, "league_type": "league", "season_type": "play_off",
                        "html_data": load_html("dostal_stats_league_play_off.html")},
                        {"id": 1, "league_type": "tournament", "season_type": "regular",
                        "html_data": load_html("dostal_stats_tournament_regular.html")},
                        {"id": 1, "league_type": "tournament", "season_type": "play_off",
                        "html_data": load_html("dostal_stats_tournament_play_off.html")},
                    ],
                },
            ),
            (
                {"player_name": "hasek", "player_type": "goalie"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["hasek"],
                        "is_goalie": True,
                        "scrape_id": 2,
                        "facts_html": load_html("hasek_player_facts.html"),
                        "achievements": load_html("hasek_achievements.html"),
                    },
                    "goalie_stats": [
                        {"id": 1, "league_type": "league", "season_type": "regular",
                        "html_data": load_html(
                            "hasek_stats_league_regular.html"
                            )},
                        {"id": 1, "league_type": "league", "season_type": "play_off",
                        "html_data": load_html(
                            "hasek_stats_league_play_off.html"
                            )},
                        {"id": 1, "league_type": "tournament", "season_type": "regular",
                        "html_data": load_html(
                            "hasek_stats_tournament_regular.html"
                            )},
                        {"id": 1, "league_type": "tournament", "season_type": "play_off",
                        "html_data": load_html(
                            "hasek_stats_tournament_play_off.html"
                            )},
                    ],
                },
            ),
            # ---------------- SKATER ----------------
            (
                {"player_name": "howe", "player_type": "skater"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["howe"],
                        "is_goalie": False,
                        "scrape_id": 1,
                        "facts_html": load_html("howe_player_facts.html"),
                        "achievements": load_html("howe_achievements.html"),
                    },
                    "skater_stats": [
                        {"id": 1, "league_type": "league",
                        "html_data": load_html("howe_stats_league.html")},
                        {"id": 1, "league_type": "tournament",
                        "html_data": load_html("howe_stats_tournament.html")},
                    ],
                },
            ),
            (
                {"player_name": "mcdavid", "player_type": "skater"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["mcdavid"],
                        "is_goalie": False,
                        "scrape_id": 1,
                        "facts_html": load_html("mcdavid_player_facts.html"),
                        "achievements": load_html("mcdavid_achievements.html"),
                    },
                    "skater_stats": [
                        {"id": 1, "league_type": "league",
                        "html_data": load_html("mcdavid_stats_league.html")},
                        {"id": 1, "league_type": "tournament",
                        "html_data": load_html("mcdavid_stats_tournament.html")},
                    ],
                },
            ),
        ],
        indirect=["get_player_html_dict"],
    )


    def test___input_player(self, create_player_html_inputter, expected_data):
        create_player_html_inputter._input_data()
        db_data = get_player_dict(
            session=create_player_html_inputter.session,
            player_id=1
            )
        
        assert db_data == expected_data
        