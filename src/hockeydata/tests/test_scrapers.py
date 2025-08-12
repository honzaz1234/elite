import pytest

from playwright.sync_api import sync_playwright

from hockeydata.scrapers import *


SKATER_URLS = [

]


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


# One page for the entire session
@pytest.fixture(scope="session")
def session_page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def clean_page(session_page):
    session_page.goto("about:blank")
    session_page.context.clear_cookies()
    session_page.evaluate("localStorage.clear()")
    session_page.evaluate("sessionStorage.clear()")
    return session_page


@pytest.fixture
def player_scraper(clean_page, request):
    url = request.param
    return PlayerScraper(url=url, page=clean_page)

class TestSkaterScraper(unittest.TestCase):


    def 