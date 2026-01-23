import re

from datetime import datetime
from urllib import request
from playwright.sync_api import Page
from scrapy import Selector
from typing import Any

import hockeydata.common_functions as cf
import hockeydata.entity_data.playwright_setup.playwright_setup as ps

from hockeydata.constants import LEAGUE_UID_REGEX
from hockeydata.entity_data.scraper.base import LeagueSeasonRangeScraper
from hockeydata.entity_data.scraper.base import PlaywrightScraper
from hockeydata.logger.logging_config import logger


class LeagueScraper(PlaywrightScraper):

        
    PATHS = {
        "achievements": "//header[./h2[contains(text(),'Awards')]]/"
                        "following-sibling::div",
        "accept_cookies": "//button[contains(., 'AGREE')]",
        'first_year':"[1]/ol/li[1]/a/@href",
        "last_year": "[last()]/ol/li[last()]/a/@href",
        "landing_check": "//h1/span[contains(@class,'LeagueHeader_titleMain')]",
        "league_name":  "//h1/span[contains(@class,'LeagueHeader_titleMain')]",
        "season": "//header[./h2[contains(text(),'Standings')]]"
                        "/following-sibling::div[contains(@class,"
                        "'Loader_loadingContentWrapper')  "
                        "and not(contains(.,'No Data Found'))]",
        "seasons": "//header[contains(.,'seasons')]/following-sibling::div"
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
        self._get_season_list()
        self._set_season_range()
        if scrape_seasons:
            self._get_stats(season_list=season_list)
        self.scraped_data['time_scraped'] = datetime.now()
        logger.info(
            'Scraping of new player info at web adress: %s '
            'finished', self.url
            )
        
        return self.scraped_data


    def _get_season_list(self) -> None:
        range_scraper = LeagueSeasonRangeScraper(
            league_uid=self.scraped_data["uid"]
            )
        season_range = range_scraper._get_season_range()
        self.season_list = cf.create_season_list(
            first_season=season_range[0],
            last_season=season_range[1]
        )


    def _set_season_range(self) -> None:
        self.scraped_data['season_range']['first_season'] = self.season_list[0]
        self.scraped_data['season_range']['last_season'] = self.season_list[len(self.season_list) - 1]


    def _get_stats(self, season_list: list) -> None:
        if season_list == []:
            season_list = self.season_list
        for season in season_list:
            self.scraped_data['stats'][season] = self._get_year_stats(
                season=season
                )
    

    def _get_year_stats(self, season: str) -> Selector:
        season_url = self.url + "/standings/" + season
        ps.go_to_page_wait(
            page=self.page, 
            url=season_url, 
            sel_wait=self.PATHS["season"]
            )

        return self._scrape_data(xpath_name="season", is_optional=False)
