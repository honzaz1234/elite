from datetime import datetime

from hockeydata.entity_data.playwright_setup.playwright_setup import PlaywrightSetUp
from hockeydata.database_session.database_session import ScrapeDBSession
from hockeydata.management.scrape_management import PlayerURLScrapeManager


DB_PATH = "./database/storage_db_test.db"
LEAGUE_UID = "nhl"




playwright = PlaywrightSetUp()
scraper = PlayerURLScrapeManager(
    league_uid=LEAGUE_UID, 
    )
scraper.set_up()
scraped_data = scraper.scrape_data()
