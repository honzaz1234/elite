import json

from datetime import datetime

from hockeydata.entity_data.playwright_setup.playwright_setup import PlaywrightSetUp
from hockeydata.database_session.database_session import ScrapeDBSession
from hockeydata.management.scrape.management import PlayerURLScrapeManager


DB_PATH = "./database/storage_db_test.db"
LEAGUE_UID = "nhl"


def main():
    scraper_manager = PlayerURLScrapeManager(
        storage_db_path=DB_PATH,
        league_uid=LEAGUE_UID, 
        )
    scraper_manager.set_up()
    scraped_data = scraper_manager.scrape_data(max_workers=4)
    scraper_manager._input_all_data(scraped_data=scraped_data)
    scraper_manager.close_session()


if __name__ == "__main__":
    main()

