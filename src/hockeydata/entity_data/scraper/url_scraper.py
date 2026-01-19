import hockeydata.entity_data.playwright_setup.playwright_setup as ps

import playwright.sync_api as sync_api
import re
import scrapy

from hockeydata.constants import *
from hockeydata.decorators import time_execution
from hockeydata.errors import EmptyReturnXpathValueError
from hockeydata.logger.logging_config import logger

import hockeydata.common_functions as cf


class URLScraper():


    WAIT_LEAGUE_PAGE = (
        "//ul[preceding-sibling::header[./h2[contains(text(),"
        "'Champions')]]]/li[last()]/a[1]"
        )


    def __init__(self, league_uid: str, page: sync_api.Page):
        self.page = page
        self.selector = None
        self.league_uid = league_uid
        self.url = ELITE_URL + "/league/" + league_uid
        self.season_range = {
            "first_season": None, 
            "last_season": None
            }


    @time_execution
    def get_info(self) -> dict:
        pass



    def _add_season_range(self, league_uid: str, url_dict: dict) -> None:
        list_seasons = self.get_list_of_years(url=url)
        season_range = {
            'start': int(list_seasons[0]),
            'finish': int(list_seasons[-1])
            }
        url_dict[league_uid]["season_range"] = season_range


    def scrape_league_front_page(self):
        ps.go_to_page_wait_selector(
             page=self.page, 
             url=self.url, 
             sel_wait=self.WAIT_LEAGUE_PAGE
             )


    def get_list_of_years(self, url: str) -> list:
        
        block_check = True
        while block_check is not None:
                ps.go_to_page_wait_selector(
                    page=self.page, 
                    url=url, 
                    sel_wait=self.WAIT_LEAGUE_PAGE
                              )
                sel_league = scrapy.Selector(text=self.page.content())
                block_check = cf.get_single_xpath_value(
                    sel=sel_league, xpath=BLOCK_SELECTOR, optional=True
                    )
                if block_check is not None:
                    logger.info("Limit for pages scraped achieved. Timeout"
                                " will follow...")
                    time.sleep(LeagueUrlDownload.SLEEP)
        first_year = int((sel_league
                    .xpath(LeagueUrlDownload.PATHS["first_year"])
                    .getall()[0])) - 1
        last_year = int((sel_league
            .xpath(LeagueUrlDownload.PATHS["last_year"])
            .getall()[0]))
        years = [year for year in range(first_year, last_year)]

        return years
