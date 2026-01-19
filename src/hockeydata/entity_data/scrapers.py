import re

from abc import ABC, abstractmethod
from datetime import datetime
from playwright.sync_api import Page
from scrapy import Selector
from typing import Any

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import PLAYER_UID_REGEX, LEAGUE_UID_REGEX
from hockeydata.logger.logging_config import logger


class PlaywrightScraper(ABC):
    """Parent Class for downloading information from individual dynamic
       webpages;
       includes one method which wraps around methods from classes for downloading specific types (Players, Teams and Leagues)
    """


    @property
    @classmethod
    @abstractmethod
    def PATHS(cls):
        pass


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls):
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
        ps.go_to_page_wait_selector(
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


class URLScraper(PlaywrightScraper):


    CHECK_ARRIVAL_XPATH_KEY = ""
    
    
    PATHS = {
    }

    def __init__(self, url: str, page: Page):
        super().__init__(url=url, page=page)
        self.scraped_data: dict[str, Any|None] = {
            }


    def get_data(self) -> dict:
        pass


    @abstractmethod
    def _get_player_stats(self):
        pass


class PlayerScraper(PlaywrightScraper):
    """Class for downloading information from individual players webpages;
       includes one method which wraps around methods from classes for downloading 
       individual subparts of player web page:
       a) general info (name, position, age...)
       b) player  season stats 
       c) player achievements 
    """

    
    PATHS = {
        "achievements": "//section[@id='career-highlights']",
        "accept_cookies": "//button[contains(., 'AGREE')]",
        "landing_check": "//section[@id='player-facts']",
        "player_facts":  "//section[@id='player-facts']",
        "player_type": "//dt[contains(text(), 'Position')]"
                       "/following-sibling::dd/text()",
        "stats_league": "//section[@id='player-statistics' "
                       "and not(contains(., 'No Data Found'))]",
        "stats_tournament": "//section[@id='tournament-statistics' "
                           "and not(contains(., 'No Data Found'))]",
    }

    TYPE = "player"

    def __init__(self, url: str, page: Page):
        super().__init__(url=url, page=page)
        self.scraped_data: dict[str, Any|None] = {
                "uid": None,
                "player_type": None,
                "player_facts": None,
                "achievements": None,
                "stats": None,
                "missing_data": []
            }


    def get_data(self) -> dict:
        logger.info(
            'Scraping of new player info at web adress: %s '
            'started', self.url
            )
        self.scraped_data["uid"] = re.findall(
            PLAYER_UID_REGEX, self.url)[0]
        self.scraped_data["player_type"] = cf.get_single_xpath_value(
            sel=Selector(text=self.page.content()),
            xpath=self.PATHS["player_type"],
            is_optional=False
            )
        self.scraped_data["player_facts"] = self._scrape_data(
            xpath_name="player_facts",
            is_optional=False
            )
        self.scraped_data["achievements"] = self._scrape_data(
            xpath_name="achievements"
            )
        self.scraped_data['stats'] = self._get_player_stats()
        self.scraped_data['time_scraped'] = datetime.now()
        logger.info(
            'Scraping of new player info at web adress: %s '
            'finished', self.url
            )
        
        return self.scraped_data


    @abstractmethod
    def _get_player_stats(self):
        pass


class SkaterScraper(PlayerScraper):
    """Class for downloading data for field players - defenders, wingers and 
       centers
       Data for both types of stats - Regular Season and Play Offs can be accessed without interacting with the page in any way
    """


    def _get_player_stats(self) -> dict:
        stats = dict()
        stats["league"] = self._scrape_data(
            xpath_name="stats_league"
            )
        stats["tournament"] = self._scrape_data(
            xpath_name="stats_tournament" 
            )
        
        return stats


class GoalieScraper(PlayerScraper):
    """Class for downloading stats data of goalies
       To access complete Regular Season and Play Off stats, individual tables must be selected on the page
    """


    GOALIE_PATHS = {
        "season_scroll": "//div[./*[contains(@id," 
                         "'player-statistics-default-season')]]",
        "title_check": "//*[contains(@id,'player-statistics-default-season')]/"
                        "following-sibling::div//*[contains(@class,"
                        "'singleValue')]"
    }

    TYPE = {
        'regular': 'Regular Season (Complete Stats)', 
        'play_off': 'Postseason (Complete Stats)'
        }
    
    NAME_MAPPER = {
        "stats_league": "league",
        "stats_tournament": "tournament"
    }


    def _get_player_stats(self) -> dict:
        stats = dict()
        stats["league"] = self._get_table_stats_wrapper(
            path_type="stats_league"
            )
        stats["tournament"] = self._get_table_stats_wrapper(
            path_type="stats_tournament" 
            )
        
        return stats
        
        
    def _get_table_stats_wrapper(self, path_type: str) -> dict|None:
        path = self.PATHS[path_type]
        data_present = cf.check_data_presence(
            self.page, 
            path, 
            path_type,
            self.scraped_data['missing_data']
            )
        if not data_present:
            logger.info(
                "Table for type: %s is not present on the page of the player",
                path_type
                )
            return None
        stats = self._get_table_stats_wrapper_type(
            path_type=path_type
            )
        
        return stats
    

    def _get_table_stats_wrapper_type(self, path_type: str) -> dict:
        """wrapper method for downloading both regular and play off data for  
           one type of competition (league or tournament)
        """

        stats = dict()
        for season_type in GoalieScraper.TYPE:
            self._select_season_type(
                path_type=path_type, season_type=season_type
                )
            stats[season_type] = self._scrape_data(
                xpath_name=path_type
                )
        
        return stats
    
    
    def _select_season_type(self, path_type: str, season_type: str) -> None:
        """method for selecting specific table on the page - regular season vs 
           play off
        """

        button_path = (
            self.PATHS[path_type]
            + self.GOALIE_PATHS['season_scroll']
            )
        ps.click_on_button(self.page, button_path)
        self.page.keyboard.type(self.TYPE[season_type])
        self.page.keyboard.press("Enter")
        self.page.wait_for_selector(
            self.GOALIE_PATHS["title_check"], 
            timeout=10000
            )
        

class LeagueScraper(PlaywrightScraper):

        
    PATHS = {
        "achievements": "//header[./h2[contains(text(),'Awards')]]/"
                        "following-sibling::div",
        "accept_cookies": "//button[contains(., 'AGREE')]",
        'first_year':"//li[last()]//a[contains(@class,'yearLink')]/text()",
        "last_year": "//li[1]//a[contains(@class,'yearLink')]/text()",
        "landing_check": "//h1/span[contains(@class,'LeagueHeader_titleMain')]",
        "league_name":  "//h1/span[contains(@class,'LeagueHeader_titleMain')]",
        "season": "//header[./h2[contains(text(),'Standings')]]"
                        "/following-sibling::div[contains(@class,"
                        "'Loader_loadingContentWrapper')  "
                        "and not(contains(.,'No Data Found'))]",
        "seasons": "//header[./h2[contains(text(),'Champions')]]/"
                   "following-sibling::div",
    }

    TYPE = "league"


    def __init__(self, url: str, page: Page):
        super().__init__(url=url, page=page)
        self.scraped_data: dict[str, Any|None] = {
                "uid"
                "league_name": None,
                "achievements": None,
                "seasons": None,
                "stats": {},
                "missing_data": [],
                "season_range": {
                    "first_season": None,
                    "last_season": None
                    }
            }


    def get_data(
            self, scrape_seasons: bool = True, season_list: list = [] ) -> dict:
        logger.info(
            'Scraping of new league info at web adress: %s '
            'started', self.url
            )
        self.scraped_data["uid"] = re.findall(
            LEAGUE_UID_REGEX, self.url)[0]
        self.scraped_data["league_name"] = self._scrape_data(
            xpath_name="league_name",
            is_optional=False
            )
        self.scraped_data["seasons"] = self._scrape_data(
            xpath_name="seasons",
            is_optional=False
            )
        self.scraped_data["achievements"] = self._scrape_data(
            xpath_name="achievements"
            )
        self._get_list_of_years()
        self._set_season_range()
        if scrape_seasons:
            self._get_stats(season_list=season_list)
        self.scraped_data['time_scraped'] = datetime.now()
        logger.info(
            'Scraping of new player info at web adress: %s '
            'finished', self.url
            )
        
        return self.scraped_data


    def _get_list_of_years(self) -> None:
        sel = Selector(text=self.page.content())
        first_year = self._get_year(sel=sel, xpath="first_year")
        last_year = self._get_year(sel=sel, xpath="last_year")
        self.year_list = [year for year in range(first_year, last_year + 1)]

    
    def _get_year(self, sel: Selector, xpath: str) -> int:
        xpath = self.PATHS['seasons'] + self.PATHS[xpath]
        extracted_year = sel.xpath(xpath).getall()[0]

        return int(extracted_year)


    def _set_season_range(self) -> None:
        first_season = self._create_season_string(
            year=self.year_list[0], 
            preceeding=False
            )
        self.scraped_data['season_range']['first_season'] = first_season
        last_season = self._create_season_string(
            year=self.year_list[len(self.year_list) - 1], 
            preceeding=False
            )
        self.scraped_data['season_range']['last_season'] = last_season


    def _get_stats(self, season_list: list) -> None:
        if season_list == []:
            season_list = self.year_list
        for year in season_list:
            season = self._create_season_string(year=year, preceeding=False)
            self.scraped_data['stats'][season] = self._get_year_stats(year=year)
    

    def _get_year_stats(self, year: str) -> Selector:
        season_string = self._create_season_string(year=year, preceeding=True)
        season_url = self.url + "/standings/" + season_string
        ps.go_to_page_wait_selector(
            page=self.page, 
            url=season_url, 
            sel_wait=self.PATHS["season"]
            )

        return self._scrape_data(xpath_name="season", is_optional=False)


    def _create_season_string(self, year: str, preceeding: bool=True) -> list:
        if preceeding == True:
            year_plus = int(year) + 1
            season_string = str(year) + "-" +  str(year_plus)
        else:
            year_minus = int(year) - 1
            season_string = str(year_minus) + "-" + str(year)
            
        return season_string

