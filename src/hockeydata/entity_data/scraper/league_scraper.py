import entity_data.playwright_setup.playwright_setup as ps
import playwright.sync_api as sync_api
import re
import scrapy

import common_functions as cf
from constants import *
from decorators import time_execution
from logger.logging_config import logger


class LeagueScrapper():

    """class used for scrapping data from the league webpage on eliteprospects website, data downloaded consists of league name, standings of teams in individual seasons and list of achievements (trophies)
    """
    #xpath to access different types of info regarding the league

    PATHS = {
        "achievements": "//div[preceding-sibling::header[./h2[contains(text(),"
                        "'Awards')]]]/ul/li//a[1]/text()",
        "long_name": "//h1//text()",
        "season_href": "//div[preceding-sibling::header[./h2[contains(text(),"
                       "'Champions')]]]/ul/li//a[1]/@href"
    }

    def __init__(self, url: str, page: sync_api.Page):
        """url is the web address of league on elite prospect website"""

        self.url = url
        self.html = cf.get_valid_request(url=url, return_type="content")
        self.page = page

    @time_execution
    def get_info(self) -> dict:
        """method that creates dictionary of all data that is available for scrappping within this class
        """
        logger.info(f'Scraping of new league info at web adress: {self.url}'
                    f' started')
        league_dict = {}
        self.page.goto(self.url)
        self.selector = scrapy.Selector(text=self.page.content())
        league_dict[LEAGUE_UID] = self._get_uid()
        league_dict[LEAGUE_NAME] = self._get_name()
        league_dict[LEAGUE_ACHIEVEMENTS] = self.get_achievements()
        league_dict[SEASON_STANDINGS] = self.get_season_data()
        logger.debug(f"League dict: {league_dict}")
        logger.info(f"Dict of league with name " 
                    f"{league_dict[LEAGUE_NAME]} "
                    f"({league_dict[LEAGUE_UID]})"
                    f"scraped")
        
        return league_dict

    def _get_uid(self) -> str:
        """method for accessing uid of league from url"""

        uid = re.findall(LEAGUE_UID_REGEX, self.url)[0]
        logger.debug(f"League uid: {uid}")

        return uid

    def _get_name(self) -> str:
        """method for scraping league name"""

        league_name = cf.get_single_xpath_value(
            sel=self.selector,
            xpath=LeagueScrapper.PATHS["long_name"],
            optional=False
        ) 
        league_name = league_name.strip()
        logger.debug(f"League name: {league_name}")

        return league_name

    def get_achievements(self) -> list:
        """method for scraping list of achievements(trophies):
        most points, goals in the season etc."""

        achievements_list = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=LeagueScrapper.PATHS["achievements"],
            optional=True)
        achievements_list = [achievement.strip()
                             for achievement in achievements_list]
        logger.debug(f"League achievements: {achievements_list}")

        return achievements_list

    def get_season_data(self) -> dict:
        """method for creating dictionary with season standings of teams for all years that are availiable on the website
        """

        season_href_list = cf.get_list_xpath_values(
            sel=self.selector, 
            xpath=LeagueScrapper.PATHS["season_href"],
            optional=False) 
        league_standings_dict = {}
        logger.info(f"{len(season_href_list)} links for season tables found"
                    f" on the page")
        for season_ref in season_href_list:
            season = re.findall('\/([0-9\-]+)$', season_ref)[0]
            season_link = ELITE_URL + season_ref
            league_season_o = LeagueSeasonScraper(url=season_link)
            season_dict = league_season_o.get_season_standings()
            league_standings_dict[season] = season_dict
        logger.debug(f"All season data: {league_standings_dict}")

        return league_standings_dict


class LeagueSeasonScraper():

    """class grouping methods for scraping data from one season standings table"""

    #xpaths to access different parts of season standing table
    
    PATHS = {
        "table_section_l": "//table[@class = 'table standings table-sortable']"
                         "//tbody[count(./tr/*)>1]",
        "table_section_r": "/tr[not(@class = 'title')]",
        "table_section_names": "//table[@class = 'table standings"
                               " table-sortable']//tr[@class='title']"
                               "/td//text()",
        "table_row": "//table[@class = 'table standings"
                          " table-sortable']//tr",
        "one_row_r": "/td//text()",
        "team_url_r": "/td[@class='team']//a/@href"
    }
    
    #names of columns in season standings table 

    STAT_NAMES = [LEAGUE_POSITION, TEAM, GP, W, T, L,
                    OTW, OTL, GOALS_FOR, GOALS_AGAINST, PLUS_MINUS, TOTAL_POINTS, POSTSEASON
    ]
    

    def __init__(self, url: str):
        self.url = url
        self.season = re.findall('([0-9\-]+)$', self.url)
        self.html = cf.get_valid_request(url=url, return_type="content")
        self.selector = scrapy.Selector(text=self.html)

    
    def get_season_standings(self) -> dict:
        """method for downloading season standings data from one season"""

        section_names = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=LeagueSeasonScraper.PATHS["table_section_names"],
            optional=True
        )
        section_names = [name.strip() for name in section_names]
        section_list = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=LeagueSeasonScraper.PATHS["table_section_l"],
            optional=True
        )
        n_sections = len(section_list)
        if n_sections > len(section_names):
            section_names = ["main"] + section_names
        dict_season = {}
        for section_ind in range(1, n_sections + 1):
            dict_season[section_names[section_ind - 1]] = self._get_section(
                section_ind=section_ind)
        logger.debug(f"League standings for season ({self.season}): scraped")
        if len(dict_season) == 0:
            error_message = f"0 rows found in table at adress: {self.url}"
            cf.log_and_raise(error_message)
        
        return dict_season
    

    def _get_section(self, section_ind: int) -> dict:
        """wrapper method for downloading season standings data from one section of season standings table
        """

        path_section = (LeagueSeasonScraper.PATHS["table_section_l"] 
                            + "[" 
                            + str(section_ind) 
                            + "]" 
                            + LeagueSeasonScraper.PATHS["table_section_r"])
        dict_section = self._get_section_standings(
                path_section=path_section)
        logger.debug(f"Section standings: {dict_section}")

        return dict_section


    def _get_section_standings(self, path_section: str) -> dict:
        """method for downloading season standings data from one section of season standings table
        """
        rows = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=path_section,
            optional=False
        )
        n_rows = len(rows)
        dict_section = {}
        for row_ind in range(1, n_rows + 1):
            row_dict = self._get_one_row(
                path_section=path_section, row_ind=row_ind)
            dict_section[row_dict[LEAGUE_POSITION]] = row_dict

        return dict_section
    

    def _get_one_row(self, path_section: str, row_ind: int) -> dict:
        """method for downloading one row from season stadndings table"""

        dict_row = {}
        dict_row[TEAM_URL] = self._get_team_url(path_section=path_section, 
                                               row_ind=row_ind)
        row_stats = self._get_row_stats(path_section=path_section,
                                        row_ind=row_ind)
        for ind in range(len(row_stats)):
            dict_row[LeagueSeasonScraper.STAT_NAMES[ind]
                        ] = row_stats[ind].strip()
        logger.debug(f"One Row standings: {dict_row}")

        return dict_row


    def _get_row_stats(self, path_section: str, row_ind: int) -> list:
         """methods for downloading indvidiual attributes from one row of season standings table (total points, goals, goals against...)
         """

         one_row_path = (path_section 
                        + "[" 
                        + str(row_ind) 
                        + "]" 
                        + LeagueSeasonScraper.PATHS["one_row_r"])
         row_data = cf.get_list_xpath_values(
             sel=self.selector,
             xpath=one_row_path,
             optional=False
         )
         row_data = [
             value.strip() for value in row_data if value.strip() != ""
             ]
         
         return row_data


    def _get_team_url(self, path_section: str, row_ind: int) -> str:
        """method for accessing url of team from season standings table"""

        path_url = (
            path_section 
            + "[" 
            + str(row_ind) 
            + "]" 
            +  LeagueSeasonScraper.PATHS["team_url_r"]
            )
        url_list = cf.get_single_xpath_value(
             sel=self.selector,
             xpath=path_url,
             optional=False
         )
        
        return url_list