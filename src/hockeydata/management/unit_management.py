from abc import ABC, abstractmethod

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import *
from hockeydata.database_creator.database_creator import *
from hockeydata.entity_data.scraper.player_scraper import PlaywrightScraper
from hockeydata.logger.logging_config import logger


class ScraperManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def SCRAPE_CLASS(cls) -> type[PlaywrightScraper]:
        pass


    def __init__(self, url_mapper: dict[str]=None):
        playwright_session = ps.PlaywrightSetUp()
        self.page = playwright_session.page
        self.url_mapper = url_mapper


    def process(self) -> list[dict]:
        self.initiate_playwright_session()

        return self.scrape_data()


    def initiate_playwright_session(self) -> None:
        playwright = ps.PlaywrightSetUp()
        self.page = playwright.page
        logger.debug("Playwright session succesfully initiated.")


    def scrape_data(self) -> list[dict]:
        scraped_entities = []
        for uid in self.url_mapper:
            try:
                scraped_entity = self.scrape_entity_data(
                    url=self.url_mapper[uid]
                    )
            #add custom exception
            except Exception as e:
                error_message = (
                    "Scraped failed for uid %s: %s",
                    uid, e
                )
            #    self.db_session.bulk_insert_mappings(
            #        self.db_source.Season, self.scrape_log
            #        )
                cf.log_and_raise(error_message, Exception)
            scraped_entities.append(scraped_entity)
        
        return scraped_entities


    def scrape_entity_data(self, url: str) -> dict:
        scraper = self.SCRAPE_CLASS(url=url, page=self.page)
        scraper.go_to_page(check_xpath=scraper.PATHS["landing_check"])
        scraper.get_data()

        return scraper.get_data()


class PlayerScraperManager(ScraperManager):


    SCRAPE_CLASS = PlayerScraper