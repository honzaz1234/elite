from abc import ABC, abstractmethod
from playwright.sync_api import Page

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import *
from hockeydata.database_creator.database_creator import *
from hockeydata.entity_data.scraper.base import PlaywrightScraper
from hockeydata.entity_data.scraper.player_scraper import PlayerScraper
from hockeydata.entity_data.scraper.url_scraper import PlayerSeasonURLScraper
from hockeydata.logger.logging_config import logger


class ScraperUnitManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def SCRAPE_CLASS(cls) -> type[PlaywrightScraper]:
        pass

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        pass


    def __init__(self):
        playwright_session = ps.PlaywrightSetUp()
        self.page = playwright_session.page


    def process(self) -> list[dict]:
        self.initiate_playwright_session()

        return self.scrape_data()


    def initiate_playwright_session(self) -> None:
        playwright = ps.PlaywrightSetUp()
        self.page = playwright.page
        logger.debug("Playwright session succesfully initiated.")


    @abstractmethod
    def scrape_data(self) -> list[dict]:
        pass


class EntityScraperUnitManager(ScraperUnitManager):


    def __init__(self, url_mapper: dict[str]=None):
        super().__init__()
        self.url_mapper = url_mapper


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
                    "%s scrape failed for uid %s: %s",
                    self.TYPE, 
                    uid, 
                    e
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

        return scraper.get_data()


class PlayerScraperUnitManager(EntityScraperUnitManager):


    SCRAPE_CLASS = PlayerScraper
    TYPE = "Player"


class URLScraperUnitManager(ScraperUnitManager):


    def __init__(self, league_uid: str, seasons: list[str]):
        super().__init__()
        self.league_uid = league_uid
        self.seasons = seasons


    def scrape_data(self) -> list[dict]:
        scraped_entities = []
        for season in self.seasons:
            try:
                scraped_entity = self.scrape_entity_data(
                    season=season,
                    league_uid=self.league_uid
                    )
            #add custom exception
            except Exception as e:
                error_message = (
                    "%s URL Scrape failed for season %s: %s",
                    self.TYPE, 
                    season, 
                    e
                )
            #    self.db_session.bulk_insert_mappings(
            #        self.db_source.Season, self.scrape_log
            #        )
                cf.log_and_raise(error_message, Exception)
            scraped_entities.append(scraped_entity)
        
        return scraped_entities
    

    def scrape_entity_data(
            self, season: str, league_uid: str) -> dict:
        scraper = self.SCRAPE_CLASS(
            season=season, 
            page=self.page, 
            league_uid=league_uid
            )

        return scraper.get_data()
    

class PlayerURLScraperUnitManager(URLScraperUnitManager):


    SCRAPER_CLASS = PlayerSeasonURLScraper
    TYPE = "Player"