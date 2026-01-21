import re

from datetime import datetime
from playwright.sync_api import Page
from scrapy import Selector
from typing import Any

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import LEAGUE_UID_REGEX
from hockeydata.entity_data.scraper.base import PlaywrightScraper
from hockeydata.logger.logging_config import logger


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
                "uid": None,
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


    def get_season_range(self) -> dict:
        self._get_list_of_years()
        self._set_season_range()

        return self.scraped_data['season_range']


    def _get_list_of_years(self) -> None:
        sel = Selector(text=self.page.content())
        first_year = self._get_year(sel=sel, xpath="first_year")
        last_year = self._get_year(sel=sel, xpath="last_year")
        self.year_list = [year for year in range(first_year, last_year + 1)]

    
    def _get_year(self, sel: Selector, xpath: str) -> int:
        xpath = self.PATHS['seasons'] + self.PATHS[xpath]
        extracted_year = cf.get_single_xpath_value(
            sel=sel, 
            xpath=xpath, 
            optional=False
            )

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
        ps.go_to_page_wait(
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