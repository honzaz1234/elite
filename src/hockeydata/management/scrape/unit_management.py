from abc import ABC, abstractmethod
from playwright.sync_api import Browser, Page

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


    def __init__(self, page: Page):
        self.page = page


    @abstractmethod
    def scrape_data(self) -> list[dict]:
        pass


class EntityScraperUnitManager(ScraperUnitManager):


    def __init__(self, page: Page, url_mapper: dict[str]=None):
        super().__init__(page=page)
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


    def __init__(self, page: Page, league_uid: str, seasons: list[str]):
        super().__init__(page=page)
        self.league_uid = league_uid
        self.seasons = seasons
        self.scraped_data = {
            season: {}
            for season in self.seasons
        }


    def scrape_data(self) -> dict[str, dict[str, list[bytes]]]:
        for season in self.seasons:
            try:
                self.scraped_data[season] = self.scrape_season_data(
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
        
        return self.scraped_data
    

    def scrape_season_data(
            self, season: str, league_uid: str) -> dict[str, list[bytes]]:
        scraper = self.SCRAPE_CLASS(
            season=season, 
            page=self.page, 
            league_uid=league_uid
            )

        return scraper.get_data()
    

class PlayerURLScraperUnitManager(URLScraperUnitManager):


    SCRAPE_CLASS = PlayerSeasonURLScraper
    TYPE = "Player"