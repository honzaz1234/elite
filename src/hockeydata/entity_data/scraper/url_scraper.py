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


class PlayerSeasonURLScraper():


    PATHS = {
        "goalie_stats": "//div[@id='goalie-stats']",
        "skater_stats": "//div[@id='skater-stats']"
    }


    def __init__(
            self, season: str, league_uid: str, page: Page):
        self.url = (
            ELITE_URL 
            + "/league/" 
            + league_uid 
            + "/stats/" 
            + season 
            + "/total"
        )
        self.page_nums = {
            "skaters": None,
            "goalies": None
        }
        self.page = page
        self.scraped_data = {
            "skaters": [],
            "goalies": []
        }


    def get_data(self) -> dict:
        ps.go_to_page_wait(
            page=self.page, 
            url=self.url, 
            sel_wait=self.PATHS["skater_stats"]
            )
        self.scraped_data["skaters"] = self.get_player_type_data(
            page_scraper_cls=SkaterPageURLScraper,
            )
        self.scraped_data["goalies"] = self.get_player_type_data(
            page_scraper_cls=GoaliePageURLScraper,
            )
        
        return self.scraped_data


    def get_player_type_data(
            self, page_scraper_cls: type['PlayerPageURLScraper']):
        page_scraper = page_scraper_cls(
            base_url=self.url, 
            page=self.page, 
            )
        
        return page_scraper._get_player_type_urls()


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
        "last_player_check": "//tbody[last()]//tr[last()]"
                             "//td[@class='position']/text()",
        "page_num": "//a[contains(text(), 'Last page')]/@href",
        "url": "//td[@class='player']//a[@href]",
    }


    def __init__(self, base_url: str, page: Page):
        self.base_url = base_url
        self.page = page
        self.scraped_data = []


    def _get_player_type_urls(self) -> list:
        page_num = self._get_page_num()
        for page in range(1, page_num + 1):
            self._get_page_data(page=page)

        return self.scraped_data


    def _get_page_num(self) -> int:
        sel = Selector(text=self.page.content())
        page_url = cf.get_single_xpath_value(
            sel=sel,
            xpath=self.PATHS["page_num"],
            optional=True
            )
        if page_url:

            return int(re.findall(self.PAGE_REGEX, page_url)[0])
        is_one_page = self._one_page_check(sel=sel) 
        if is_one_page:

            return 1
        
        raise ValueError 


    def _one_page_check(self, sel: Selector) -> bool:
        """In case page listing is not found, checks that last postion in 
            stat table is than 100
        """
        last_position = cf.get_single_xpath_value(
            sel=sel,
            xpath=self.PATHS["last_player_check"],
            optional=False
            )
        last_position = int(re.findall("[0-9]+", last_position)[0])
        if last_position < 100:

            return True
        
        return False


    @repeat_request_until_success
    def _get_page_data(self, page: int) -> None:
        url = self.base_url + self.QUERY_STRING + str(page)
        self.page.goto(url=url)
        sel = Selector(text=self.page.content())
        url_xpath = self.TABLE_XPATH + self.PATHS["url"] 
        urls_check = cf.get_list_xpath_values(
            sel=sel,
            xpath=url_xpath,
            optional=False
        )
        if not urls_check:
            raise ValueError
        stats_table = self._scrape_data(
            xpath=self.TABLE_XPATH,
            is_optional=False
            )
        self.scraped_data.append(stats_table)
    

class SkaterPageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page=([0-9]+)"
    QUERY_STRING = "?page="
    TABLE_XPATH = "//div[@id='skater-stats']"


class GoaliePageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page-goalie=([0-9]+)"
    QUERY_STRING = "?page-goalie="
    TABLE_XPATH = "//div[@id='goalie-stats']"

    
