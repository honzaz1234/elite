import re
import scrapy

from playwright.sync_api import Page

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import PLAYER_UID_REGEX
from hockeydata.logger.logging_config import logger


class PlaywrightScraper:
    """Parent Class for downloading information from individual dynamic
       webpages;
       includes one method which wraps around methods from classes for downloading specific types (Players, Teams and Leagues)
    """


    PATHS = None


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
        self.missing_data = []   


    def get_data(self, **kwargs) -> dict:
        pass


    def _scrape_data(self, xpath_name: str) -> str|None:
        selector = scrapy.Selector(text=self.page.content())
        scraped_data = selector.xpath(
            self.PATHS[xpath_name]
            )  
        if not scraped_data:
            self.missing_data.append(xpath_name)
            logger.info(
                "Data type %s not present on the player page.", xpath_name
                )
            return None
        else:    
            logger.info("Data type %s succesfully scraped.", xpath_name) 

            return scraped_data.get().encode("utf-8")


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
        "player_facts":  "//section[@id='player-facts']",
        "player_type": "//dt[contains(text(), 'Position')]"
                       "/following-sibling::dd/text()",
        "stats_league": "//section[@id='player-statistics' "
                       "and not(contains(., 'No Data Found'))]",
        "stats_tournament": "//section[@id='tournament-statistics' "
                           "and not(contains(., 'No Data Found'))]",
    }


    def go_to_page(self):
        ps.go_to_page_wait_selector(
            page=self.page, url=self.url,
            sel_wait=self.PATHS["player_facts"]
            )
        ps.click_optional_button(
            page=self.page, sel_click=self.PATHS["accept_cookies"],
            button_type="Accept Cookies", wait_time=5000
            )


    def get_data(self):
        logger.info(
            'Scraping of new player info at web adress: %s '
            'started', self.url
            )
        self.scraped_data["player_uid"] = re.findall(
            PLAYER_UID_REGEX, self.url)[0]
        self.scraped_data["player_type"] = cf.get_single_xpath_value(
            sel=scrapy.Selector(text=self.page.content()),
            xpath=self.PATHS["player_type"],
            optional=False
            )
        self.scraped_data["player_facts"] = self._scrape_data(
            xpath_name="player_facts"
            )
        self.scraped_data["achievements"] = self._scrape_data(
            xpath_name="achievements"
            )
        self.scraped_data['stats'] = self._get_player_stats()
        logger.info(
            'Scraping of new player info at web adress: %s '
            'finished', self.url
            )
        

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
            self.missing_data
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


        
