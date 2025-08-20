import pytest

from playwright.sync_api import sync_playwright

from hockeydata.entity_data.scrapers import GoalieScraper, SkaterScraper


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def clean_page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def scraper_factory(clean_page, request):
    url, type_ = request.param
    if type_ == "skater":
        return SkaterScraper(url=url, page=clean_page)
    elif type_ == "goalie":
        return GoalieScraper(url=url, page=clean_page)


# Uses the scraper and navigates to its page
@pytest.fixture
def player_page(scraper_factory):
    scraper_factory.go_to_page()

    return scraper_factory


class TestPlayerScraper():


    @pytest.mark.parametrize(
        "scraper_factory, xpath_name, html_key",
        [
            ((
                "https://www.eliteprospects.com/player/20605/gordie-howe", "skater"
                ),
            "achievements",
            "howe_achievements"),
            
            ((
                "https://www.eliteprospects.com/player/20605/gordie-howe", "skater"
                ),
            "player_facts",
            "howe_player_facts"),
            
            ((
                "https://www.eliteprospects.com/player/20605/gordie-howe", "skater"
                ),
            "stats_league",
            "howe_stats_league"),
            
            ((
                "https://www.eliteprospects.com/player/20605/gordie-howe", "skater"
                ),
            "stats_tournament",
            "howe_stats_tournament"),
            
            ((
                "https://www.eliteprospects.com/player/183442/connor-mcdavid", "skater"
                ),
            "player_facts",
            "mcdavid_player_facts"),
            
            ((
                "https://www.eliteprospects.com/player/236340/lukas-dostal", "goalie"
                ),
            "player_facts",
            "dostal_player_facts"),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
            "player_facts",
            "hasek_player_facts"),
        ],
        indirect=["scraper_factory"]
    )

    def test__scrape_data(
        scraper_factory, player_page, xpath_name, html_key, player_html):
        expected_html = player_html[html_key]
        scraped_data = player_page._scrape_data(xpath_name=xpath_name)
        assert scraped_data == expected_html


class TestSkaterScraper():


    @pytest.mark.parametrize(
        "scraper_factory, html_keys",
        [
            ((
                "https://www.eliteprospects.com/player/20605/gordie-howe", "skater"
                ),
                ["howe_stats_league", "howe_stats_tournament"]
            ),
        ],
        indirect=["scraper_factory"]
    )

    def test__get_player_stats(
        scraper_factory, player_page, html_keys, player_html):
        league_key, tournament_key = html_keys
        expected_htmls = [player_html[league_key], player_html[tournament_key]]
        player_page._get_player_stats()
        assert expected_htmls[0] == player_page.scraped_data["stats_league"]
        assert expected_htmls[1] == player_page.scraped_data["stats_tournament"]


class TestGoalieScraper():


    @pytest.mark.parametrize(
        "scraper_factory, html_keys",
        [
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                {
                    "stats_league": ["regular", "play_off"],
                    "stats_tournament": ["regular", "play_off"]
                }
            ),
        ],
        indirect=["scraper_factory"]
    )

    def test__get_player_stats(
        scraper_factory, player_page, html_keys, player_html):
        player_page._get_player_stats()
        for section, keys in html_keys.items():
            for subkey in keys:
                expected_html = player_html[f"hasek_{section}_{subkey}"]
                assert expected_html == player_page.scraped_data[section][subkey]


    @pytest.mark.parametrize(
        "scraper_factory, html_keys, path_type",
        [
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                {
                    "stats_league": ["regular", "play_off"],
                },
                "stats_league"
            ),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                {
                    "stats_tournament": ["regular", "play_off"],
                },
                "stats_tournament"
            ),
        ],
        indirect=["scraper_factory"]
    )


    def test__get_table_stats_wrapper(
        scraper_factory, player_page, html_keys, path_type, player_html):
        player_page._get_table_stats_wrapper(
            path_type=path_type
            )
        for section, keys in html_keys.items():
            for subkey in keys:
                expected_html = player_html[f"hasek_{section}_{subkey}"]
                assert expected_html == player_page.scraped_data[section][subkey]


    @pytest.mark.parametrize(
        "scraper_factory, html_keys, path_type",
        [
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                {
                    "stats_league": ["regular", "play_off"],
                },
                "stats_league"
            ),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                {
                    "stats_tournament": ["regular", "play_off"],
                },
                "stats_tournament"
            ),
        ],
        indirect=["scraper_factory"]
    )


    def test__get_table_stats_wrapper_type(
        scraper_factory, player_page, html_keys, player_html, path_type):
        player_page._get_table_stats_wrapper_type(
            path_type=path_type
            )
        for section, keys in html_keys.items():
            for subkey in keys:
                expected_html = player_html[f"hasek_{section}_{subkey}"]
                assert expected_html == player_page.scraped_data[section][subkey]


    @pytest.mark.parametrize(
        "scraper_factory, path_type, season_type",
        [
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                "stats_league",
                "regular"
            ),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                "stats_league",
                "play_off"
            ),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                "stats_tournament",
                "regular"
            ),
            ((
                "https://www.eliteprospects.com/player/8665/dominik-hasek", "goalie"
                ),
                "stats_tournament",
                "play_off"
            ),
        ],
        indirect=["scraper_factory"]
    )

    def test__select_season_type(
        scraper_factory, player_page, path_type, season_type):
        player_page._select_season_type(
            path_type=path_type,
            season_type=season_type
            )

