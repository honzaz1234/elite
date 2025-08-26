import pytest
import pdb

from deepdiff import DeepDiff
from pathlib import Path
from sqlalchemy import text

from database_session.database_session import GetScrapeDBSession
from hockeydata.entity_data.input_html import PlayerHTMLInputter
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data" 
def load_html(file_name: str) -> str:
    with open(DATA_DIR / file_name, "rb") as f:
        file_bytes = f.read()
    return file_bytes


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
    session_o = GetScrapeDBSession(db_path=str(db_path))
    session_o.start_session()
    yield session_o.session
    session_o.session.close()
    session_o.clear_all_tables()
    session_o.engine.dispose()


@pytest.fixture(scope="session")
def player_html():
    folder = Path(__file__).parent / "data"
    return {
        file.stem: file.read_bytes()
        for file in folder.glob("*.html")
    }


@pytest.fixture(scope="function")
def get_player_html_dict(player_html, request):
    player_info = request.param
    player_type = player_info["player_type"]
    player_name = player_info["player_name"]

    base_dict = {
        "player_facts": player_html[f"{player_name}_player_facts"],
        "achievements": player_html[f"{player_name}_achievements"],
        "player_type": player_type,
        "player_uid": PLAYER_UID[player_name]
    }

    if player_type == "G":
        base_dict.update({
            "stats_league": {
                "regular": player_html[f"{player_name}_stats_league_regular"],
                "play_off": player_html[f"{player_name}_stats_league_play_off"],
            },
            "stats_tournament": {
                "regular": player_html[f"{player_name}_stats_tournament_regular"],
                "play_off": player_html[f"{player_name}_stats_tournament_play_off"],
            },
        })
    else:
        base_dict.update({
            "stats_league": player_html[f"{player_name}_stats_league"],
            "stats_tournament": player_html[f"{player_name}_stats_tournament"],
        })

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


@pytest.fixture(scope="function")
def set_player_parameters(create_player_html_inputter):
    create_player_html_inputter._set_is_goalie()
    create_player_html_inputter._set_player_uid()

    return create_player_html_inputter


@pytest.fixture(scope="function")
def input_player_data(set_player_parameters):
    set_player_parameters._input_player()

    return set_player_parameters


def get_player_dict(db_session, player_id: int):
    # Base player data
    base_sql = text("""
        SELECT 
            players.id,
            players.player_uid,
            players.is_goalie,
            players.scrape_id,
            player_facts.html_data AS facts_html,
            achievements.html_data as achievements
        FROM players
        LEFT JOIN player_facts ON players.id = player_facts.player_id
        LEFT JOIN achievements ON players.id = achievements.player_id
        WHERE players.id = :player_id
    """)
    base_data = db_session.execute(base_sql, {"player_id": player_id}).mappings().first()

    if not base_data:
        return None

    player_dict = {"base_player_html_data": dict(base_data)}

    if base_data["is_goalie"]:
        # Goalie stats
        goalie_sql = text("""
            SELECT
                players.id,
                goalie_stats.league_type,
                goalie_stats.season_type,
                goalie_stats.html_data
            FROM players
            LEFT JOIN goalie_stats ON players.id = goalie_stats.player_id
            WHERE players.id = :player_id
        """)
        goalie_stats = db_session.execute(goalie_sql, {"player_id": player_id}).mappings().all()
        player_dict["goalie_stats"] = [dict(row) for row in goalie_stats]
    else:
        # Skater stats
        skater_sql = text("""
            SELECT
                players.id,
                skater_stats.league_type,
                skater_stats.html_data
            FROM players
            LEFT JOIN skater_stats ON players.id = skater_stats.player_id
            WHERE players.id = :player_id
        """)
        skater_stats = db_session.execute(skater_sql, {"player_id": player_id}).mappings().all()
        player_dict["skater_stats"] = [dict(row) for row in skater_stats]

    return player_dict



def get_player_table_dict(db_session, player_id: int):
    sql = text("""
        SELECT 
            players.id,
            players.player_uid,
            players.is_goalie,
            players.scrape_id
        FROM players
        WHERE players.id = :player_id
    """)
    base_data = db_session.execute(sql, {"player_id": player_id}).mappings().first()

    if not base_data:
        return None

    player_table_dict = dict(base_data)

    return player_table_dict


def get_player_facts_table_dict(db_session, player_id: int):
    sql = text("""
        SELECT 
            player_facts.id,
            player_facts.player_id,
            player_facts.html_data
        FROM player_facts
        WHERE player_facts.id = :player_id
    """)
    facts_data = db_session.execute(sql, {"player_id": player_id}).mappings().first()

    if not facts_data:
        return None

    facts_dict = dict(facts_data)

    return facts_dict


def get_achievements_table_dict(db_session, player_id: int):
    sql = text("""
        SELECT 
            achievements.id,
            achievements.player_id,
            achievements.html_data
        FROM achievements
        WHERE achievements.id = :player_id
    """)
    achievements_data = db_session.execute(sql, {"player_id": player_id}).mappings().first()

    if not achievements_data:
        return None

    achievements_data = dict(achievements_data)

    return achievements_data


def get_stats_table_dict(db_session, player_id: int):
    base_sql = text("""
        SELECT 
            players.is_goalie
        FROM players
        WHERE players.id = :player_id
    """)
    base_data = db_session.execute(base_sql, {"player_id": player_id}).mappings().first()

    if not base_data:
        return None
    
    stats_dict = {}

    if base_data["is_goalie"]:
        # Goalie stats
        goalie_sql = text("""
            SELECT
                players.id,
                goalie_stats.league_type,
                goalie_stats.season_type,
                goalie_stats.html_data
            FROM players
            LEFT JOIN goalie_stats ON players.id = goalie_stats.player_id
            WHERE players.id = :player_id
        """)
        goalie_stats = db_session.execute(goalie_sql, {"player_id": player_id}).mappings().all()
        stats_dict["goalie_stats"] = [dict(row) for row in goalie_stats]
    else:
        # Skater stats
        skater_sql = text("""
            SELECT
                players.id,
                skater_stats.league_type,
                skater_stats.html_data
            FROM players
            LEFT JOIN skater_stats ON players.id = skater_stats.player_id
            WHERE players.id = :player_id
        """)
        skater_stats = db_session.execute(skater_sql, {"player_id": player_id}).mappings().all()
        stats_dict["skater_stats"] = [dict(row) for row in skater_stats]

    return stats_dict


class TestPlayerHTMLInputter():


    @pytest.mark.parametrize(
        "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "G"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["dostal"],
                        "is_goalie": 1,
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
                {"player_name": "hasek", "player_type": "G"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["hasek"],
                        "is_goalie": 1,
                        "scrape_id": 1,
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
                {"player_name": "howe", "player_type": "RW"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["howe"],
                        "is_goalie": 0,
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
                {"player_name": "mcdavid", "player_type": "C"},
                {
                    "base_player_html_data": {
                        "id": 1,
                        "player_uid": PLAYER_UID["mcdavid"],
                        "is_goalie": 0,
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


    def test___input_data(self, create_player_html_inputter, expected_data):
      #  pdb.set_trace()
        create_player_html_inputter._input_data()
     #   pdb.set_trace()
        db_data = get_player_dict(
            db_session=create_player_html_inputter.db_session,
            player_id=1
            )
      #  pdb.set_trace()
        diff = DeepDiff(expected_data, db_data, ignore_order=True)
        assert not diff, diff


    @pytest.mark.parametrize(
         "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "G"},
                {
                        "id": 1,
                        "player_uid": PLAYER_UID["dostal"],
                        "is_goalie": 1,
                        "scrape_id": 1,
                },
            ),
            (
                {"player_name": "hasek", "player_type": "G"},
                {
                        "id": 1,
                        "player_uid": PLAYER_UID["hasek"],
                        "is_goalie": 1,
                        "scrape_id": 1,
                },
            ),
            # ---------------- SKATER ----------------
            (
                {"player_name": "howe", "player_type": "RW"},
                {
                        "id": 1,
                        "player_uid": PLAYER_UID["howe"],
                        "is_goalie": 0,
                        "scrape_id": 1,
                },
            ),
            (
                {"player_name": "mcdavid", "player_type": "C"},
                {
                        "id": 1,
                        "player_uid": PLAYER_UID["mcdavid"],
                        "is_goalie": 0,
                        "scrape_id": 1,
                },
            ),
        ],
        indirect=["get_player_html_dict"],
    )


    def test___input_player(self, set_player_parameters, expected_data):
      #  pdb.set_trace()
        set_player_parameters._input_player()
     #   pdb.set_trace()
        db_data = get_player_table_dict(
            db_session=set_player_parameters.db_session,
            player_id=1
            )
      #  pdb.set_trace()
        diff = DeepDiff(expected_data, db_data, ignore_order=True)
        assert not diff, diff


    @pytest.mark.parametrize(
        "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "G"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("dostal_player_facts.html")
                },
            ),
            (
                {"player_name": "hasek", "player_type": "G"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("hasek_player_facts.html")
                },
            ),
            # ---------------- SKATER ----------------
            (
                {"player_name": "howe", "player_type": "RW"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("howe_player_facts.html")
                },
            ),
            (
                {"player_name": "mcdavid", "player_type": "C"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("mcdavid_player_facts.html")
                },
            ),
        ],
        indirect=["get_player_html_dict"],
    )


    def test___input_player_facts(
        self, input_player_data, expected_data):
        input_player_data._input_player_facts_html()
        db_data = get_player_facts_table_dict(
            db_session=input_player_data.db_session,
            player_id=1
            )
        #pdb.set_trace()
        diff = DeepDiff(expected_data, db_data, ignore_order=True)
        assert not diff, diff


    @pytest.mark.parametrize(
        "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "G"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("dostal_achievements.html")
                },
            ),
            (
                {"player_name": "hasek", "player_type": "G"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("hasek_achievements.html")
                },
            ),
            # ---------------- SKATER ----------------
            (
                {"player_name": "howe", "player_type": "RW"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("howe_achievements.html")
                },
            ),
            (
                {"player_name": "mcdavid", "player_type": "C"},
                {
                    "id": 1,
                    "player_id": 1,
                    "html_data": load_html("mcdavid_achievements.html")
                },
            ),
        ],
        indirect=["get_player_html_dict"],
    )


    def test___input_achievements(
        self, input_player_data, expected_data):
        input_player_data._input_achievements_html()
        db_data = get_achievements_table_dict(
            db_session=input_player_data.db_session,
            player_id=1
            )
        #pdb.set_trace()
        diff = DeepDiff(expected_data, db_data, ignore_order=True)
        assert not diff, diff


    @pytest.mark.parametrize(
        "get_player_html_dict, expected_data",
        [
            # ---------------- GOALIE ----------------
            (
                {"player_name": "dostal", "player_type": "G"},
                {
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
                {"player_name": "hasek", "player_type": "G"},
                {
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
                {"player_name": "howe", "player_type": "RW"},
                {
                    "skater_stats": [
                        {"id": 1, "league_type": "league",
                        "html_data": load_html("howe_stats_league.html")},
                        {"id": 1, "league_type": "tournament",
                        "html_data": load_html("howe_stats_tournament.html")},
                    ],
                },
            ),
            (
                {"player_name": "mcdavid", "player_type": "C"},
                {
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
        

    def test___input_stats_htmls(
        self, input_player_data, expected_data):
        input_player_data._input_stats_htmls()
        db_data = get_stats_table_dict(
            db_session=input_player_data.db_session,
            player_id=1
            )
        #pdb.set_trace()
        diff = DeepDiff(expected_data, db_data, ignore_order=True)
        assert not diff, diff