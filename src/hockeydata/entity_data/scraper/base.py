import re

from abc import ABC, abstractmethod
from playwright.sync_api import Page
from scrapy import Selector

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.logger.logging_config import logger


class PlaywrightScraper(ABC):
    """Parent Class for downloading information from individual dynamic
       webpages;
       includes one method which wraps around methods from classes for downloading specific types (Players, Teams and Leagues)
    """


    @property
    @classmethod
    @abstractmethod
    def PATHS(cls) -> dict[str, str]:
        pass


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        pass


    def __init__(self, url: str, page: Page):
        """Arguments:
        url - url of webpage with player's information
        html - html code of player profile webpage
        selector - selector object created from html of player's webpage   
                   used for attaining individual pieces of information
        """

        self.url = url
        self.page = page
        self.scraped_data = {}  


    def go_to_page(self):
        ps.go_to_page_wait(
            page=self.page, url=self.url,
            sel_wait=self.PATHS["landing_check"]
            )
        ps.click_optional_button(
            page=self.page, sel_click=self.PATHS["accept_cookies"],
            button_type="Accept Cookies", wait_time=5000
            )


    def _scrape_data(
            self, xpath_name: str, is_optional: bool = True) -> str|None:
        selector = Selector(text=self.page.content())
        scraped_data = selector.xpath(
            self.PATHS[xpath_name]
            )  
        if not scraped_data:
            if is_optional:
                message = (
                    "Data type %s not present on the %s page.", 
                    xpath_name,
                    self.TYPE
                )
                self.scraped_data['missing_data'].append(xpath_name)
                logger.info(message)
                return None
            else:
                cf.log_and_raise(message, ValueError)
        else:    
            logger.info("Data type %s succesfully scraped.", xpath_name) 

            return scraped_data.get().encode("utf-8")
        
    
    @abstractmethod
    def get_data(self) -> dict:
        pass


class LeagueSeasonRangeScraper():


    PATHS = {
        "first_year":"[1]/ol/li[1]/a/@href",
        "last_year": "[last()]/ol/li[last()]/a/@href",
        "seasons": "//header[contains(.,'seasons')]/following-sibling::div"
    }


    def __init__(self, league_uid: str):
        self.url = ( 
            "https://www.eliteprospects.com/league/" 
            + league_uid 
            + "/standings/"
        )
        self.year_list: list[int] = []
    

    def _get_season_range(self) -> tuple[str, str]:
        resp = cf.get_valid_request(self.url, return_type="content")
        sel = Selector(text=resp)
        first_season = self._get_season(sel=sel, xpath="first_year")
        last_season = self._get_season(sel=sel, xpath="last_year")
        
        return first_season, last_season

    
    def _get_season(self, sel: Selector, xpath: str) -> str:
        xpath = self.PATHS["seasons"] + self.PATHS[xpath]
        extracted_season = cf.get_single_xpath_value(
            sel=sel, 
            xpath=xpath, 
            optional=False
            )
        extracted_season = re.findall("standings\/(.+)$", extracted_season)[0]

        return extracted_season
    