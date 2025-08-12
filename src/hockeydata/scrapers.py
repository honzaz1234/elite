import scrapy

from playwright.sync_api import Page

import hockeydata.playwright_setup.playwright_setup as ps

from logger.logging_config import logger


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


    def _scrape_data(self, xpath_name: str) -> str:
        selector = scrapy.Selector(text=self.page.content())
        scraped_data = selector.xpath(
            self.PATHS[xpath_name]
            )  
        if scraped_data is None:
            self.missing_data.append(xpath_name)
            logger.info(
                "Data type %s not present on the player page.", xpath_name
                )
        else:    
            logger.info("Data tpye %s succesfully scraped.", xpath_name) 

        return scraped_data   


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
        "player_type": "//li[./span[contains(text(), 'Position')]]/text()",
        "stats_league": "//section[@id='player-statistics' "
                       "and not(contains(., 'No Data Found'))]",
        "stats_tournament": "//section[@id='tournament-statistics' "
                           "and not(contains(., 'No Data Found'))]",
    }


    def get_data(self):
        logger.info(
            'Scraping of new player info at web adress: %s '
            'started', self.url
            )
        ps.go_to_page_wait_selector(
            page=self.page, url=self.url,
            sel_wait=self.PATHS["player_facts"]
            )
        ps.click_optional_button(
            page=self.page, sel_click=self.PATHS["accept_cookies"],
            button_type="Accept Cookies", wait_time=5000
            )
        self.scraped_data["player_type"] = self._scrape_data(
            xpath_name="player_type"
            )
        self.scraped_data["player_facts"] = self._scrape_data(
            xpath_name="player_facts"
            )
        self.scraped_data["achievements"] = self._scrape_data(
            xpath_name="achievements"
            )
        self._get_player_stats()
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


    def _get_player_stats(self):
        self.scraped_data["stats_league"] = self._scrape_data(
            xpath_name="stats_league"
            )
        self.scraped_data["stats_tournament"] = self._scrape_data(
            xpath_name="stats_tournament" 
            )


class GoalieScraper(PlayerScraper):
    """Class for downloading stats data of goalies
       To access complete Regular Season and Play Off stats, individual tables must be selected on the page
    """


    GOALIE_PATHS = {
        "season_scroll": "//div[contains(@class,"       
                         "'PlayerStatistics_selectorWrapper')]"
                         "/div[./*[contains(@id," 
                         "'player-statistics-default-season')]]",
        "season_selection": "//div[contains(@id,'default-season-selector')]"
                            "/div",
    }

    TYPE = {
        'regular': 'Regular Season (Complete Stats)', 
        'play_off': 'Postseason (Complete Stats)'
        }


    def _get_player_stats(self):
        self._get_table_stats_wrapper_type(
            path_type="stats_league"
            )
        self._get_table_stats_wrapper_type(
            path_type="stats_tournament" 
            )
        

    def _get_table_stats_wrapper_type(self, path_type: str) -> None:
        """wrapper method for downloading both regular and play off data for  
           one type of competition (league or tournament)
        """

        self.scraped_data[path_type] = {}
        for season_type in GoalieStatsScraper.TYPE:
            self._select_season_type(
                path_type=path_type, season_type=season_type
                )
            self.scraped_data[path_type][season_type] = self._scrape_data(
                xpath_name=self.PATHS[path_type]
                )
    
    
    def _select_season_type(self, path_type: str, season_type: str) -> None:
        """method for selecting specific table on the page - regular season vs 
           play off
        """

        button_path = (
            self.PATHS[path_type]
            + self.GOALIE_PATHS['season_scroll']
            )
        ps.click_on_button(self.page, button_path)
        selection_path = (
            self.PATHS[path_type]
            + self.GOALIE_PATHS['season_selection']
            + "[contains(text(), '" 
            + self.TYPE[season_type]
            + "')]"
            )
        ps.click_on_button(self.page, selection_path)
        
