import re 


from abc import ABC, abstractmethod
from playwright.sync_api import Page
from scrapy import Selector


from hockeydata.constants import *
from hockeydata.decorators import repeat_request_until_success
from hockeydata.entity_data.scraper.base import PlaywrightScraper
from hockeydata.decorators import time_execution
from hockeydata.logger.logging_config import logger


import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps


class PlayerSeasonURLScraper(PlaywrightScraper):


    PATHS = {
        "goalie_stats": "//div[@id='goalie-stats']",
        "landing_check": "//div[@id='skater-stats']"
                        "//td[@class='player']//a[@href]",
        "last_player_check": "//tbody[last()]//tr[last()]"
                             "//td[@class='position']/text()",
        "page_num": "//a[contains(text(), 'Last page')]/@href",
        "skater_stats": "//div[@id='skater-stats']",
        "table_goalies": "//div[@id='goalie-stats']",
        "table_skaters": "//div[@id='skater-stats']",
    }
    TYPE = "Player URL"


    def __init__(
            self, season: str, league_uid: str, page: Page):
        url = (
            ELITE_URL 
            + "/league/" 
            + league_uid 
            + "/stats/" 
            + season 
            + "/total"
        )
        super().__init__(url=url, page=page)
        self.page_nums = {
            SkaterPageURLScraper: None,
            GoaliePageURLScraper: None
        }
        self.scraped_data = {
            "skaters": [],
            "goalies": []
        }
        self.season = season
    

    def _one_page_check(
            self, sel: Selector, 
            page_cls: type['PlayerPageURLScraper']) -> bool:
        """In case page listing is not found, checks that last postion in 
            stat table is than 100
        """
        last_player_xpath = (
            self.PATHS[page_cls.TABLE_XPATH] 
            + self.PATHS["last_player_check"]
            )
        last_position = cf.get_single_xpath_value(
            sel=sel,
            xpath=last_player_xpath,
            optional=False
            )
        last_position = int(re.findall("[0-9]+", last_position)[0])
        if last_position < 100:

            return True
        
        return False
    

    def get_data(self) -> dict:
        self._get_page_nums()
        self.scraped_data["skaters"] = self.get_player_type_data(
            page_cls=SkaterPageURLScraper,
            )
        self.scraped_data["goalies"] = self.get_player_type_data(
            page_cls=GoaliePageURLScraper,
            )
        
        return self.scraped_data
    

    def _get_page_nums(self) -> None:
        self.page_nums[SkaterPageURLScraper] = self._get_page_num(
            page_cls=SkaterPageURLScraper
            )
        self.page_nums[GoaliePageURLScraper] = self._get_page_num(
            page_cls=GoaliePageURLScraper
            )
    
    
    def _get_page_num(self, page_cls: type['PlayerPageURLScraper']) -> int:
        sel = Selector(text=self.page.content())
        last_page_xpath = ( 
            self.PATHS[page_cls.TABLE_XPATH] 
            + self.PATHS["page_num"] 
            )
        page_url = cf.get_single_xpath_value(
            sel=sel,
            xpath=last_page_xpath,
            optional=True
            )
        if page_url:

            return int(re.findall(page_cls.PAGE_REGEX, page_url)[0])
        is_one_page = self._one_page_check(sel=sel, page_cls=page_cls) 
        if is_one_page:

            return 1
        
        raise ValueError 


    def get_player_type_data(
            self, 
            page_cls: type['PlayerPageURLScraper']) -> list[bytes]:
        tables = []
        logger.info(
            "Scraping %s data.. (%s page(s), %s)", 
            page_cls.TYPE, 
            self.page_nums[page_cls],
            self.season
            )
        for page in range(1, self.page_nums[page_cls] + 1):
            table_html = self._get_one_table(
                page_num=page, 
                page_cls=page_cls
                )
            tables.append(table_html)
        logger.info("%s data  scraped. (%s)", page_cls.TYPE, self.season)

        return tables
    

    def _get_one_table(
            self, page_num: int, 
            page_cls: type['PlayerPageURLScraper']) -> bytes:
            page_scraper = page_cls(
                base_url=self.url, 
                page_num=page_num,
                page=self.page, 
                )
            page_scraper.go_to_page()
            scraped_table = page_scraper.get_data()
            logger.info(
                "%s/%s (%s, %s)",  
                page_num, 
                self.page_nums[page_cls],
                page_cls.TYPE,
                self.season
                )
            
            return scraped_table
    

class PlayerPageURLScraper(PlaywrightScraper):


    @property
    @classmethod
    @abstractmethod
    def PAGE_REGEX(cls):
        pass


    @property
    @classmethod
    @abstractmethod
    def QUERY_STRING(cls):
        pass


    @property
    @classmethod
    @abstractmethod
    def TABLE_XPATH(cls):
        pass


    PATHS = {
        "landing_check": "//div[@id='skater-stats']"
                         "//td[@class='player']//a[@href]",
        "table_goalies": "//div[@id='goalie-stats']",
        "table_skaters": "//div[@id='skater-stats']"
    }


    def __init__(self, base_url: str, page_num: int, page: Page):
        url = base_url + self.QUERY_STRING + str(page_num)
        super().__init__(url=url, page=page)

    
    def get_data(self) -> None:
        return  self._scrape_data(
            xpath_name=self.TABLE_XPATH,
            is_optional=False
            )
    

class SkaterPageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page=([0-9]+)"
    QUERY_STRING = "?page="
    TABLE_XPATH = "table_skaters"
    TYPE = "Skater Page URLs"


class GoaliePageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page-goalie=([0-9]+)"
    QUERY_STRING = "?page-goalie="
    TABLE_XPATH = "table_goalies"
    TYPE = "Goalie Page URLs"

    
