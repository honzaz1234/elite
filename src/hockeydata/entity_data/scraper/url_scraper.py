import re 


from abc import ABC, abstractmethod
from playwright.sync_api import Page
from scrapy import Selector


from hockeydata.constants import *
from hockeydata.decorators import repeat_request_until_success
from hockeydata.database_session.database_session import ScrapeDBSession
from hockeydata.database_queries.database_query import StorageDBQuery
from hockeydata.entity_data.scraper.league_scraper import LeagueScraper
from hockeydata.decorators import time_execution
from hockeydata.logger.logging_config import logger


import hockeydata.common_functions as cf
import hockeydata.database_creator.storage_database_creator as storage_db
import hockeydata.entity_data.playwright_setup.playwright_setup as ps


class URLScraper():


    WAIT_LEAGUE_PAGE = (
        "//ul[preceding-sibling::header[./h2[contains(text(),"
        "'Champions')]]]/li[last()]/a[1]"
        )


    def __init__(self, league_uid: str, page: Page, db_path: str):
        self.page = page
        self.selector = None
        self.league_uid = league_uid
        self.url = ELITE_URL + "/league/" + league_uid
        self.season_range = {
            "first_season": None, 
            "last_season": None
            }
        self.seasons = []
        self.db_path = db_path


    @time_execution
    def get_info(self) -> dict[str, dict[str, list]]:
        self._add_seasons()
        seasons = self._generate_seasons()
        scraped_data = self._scrape_season_urls(seasons=seasons)

        return scraped_data


    def _add_seasons(self) -> None:
        season_range_set = self._check_season_range_in_db(
            league_uid=self.league_uid
            )
        if season_range_set:
            return
        self._scrape_season_range()


    def _check_season_range_in_db(
            self, league_uid: str) -> bool:
        db_session = ScrapeDBSession(db_path=self.db_path)
        db_session.set_up_connection()
        query = StorageDBQuery(db_session=db_session.session)
        filter_ = [storage_db.LeagueInfo.uid.is_(league_uid)]
        season_range = query.get_db_query_result(
             query_name="year_range", 
             filters=filter_
             )
        #update based on return value
        if not season_range:
            logger.info(
                "Season range for league %s not yet in DB. Scrape will proceed",
                league_uid
                )
            
            return False
        else:
            logger.info(
                "Season range for league %s fetched from DB.",
                league_uid
                )
            self._set_season_range(season_range=season_range)
            
            return True 


    def _set_season_range(self, season_range: tuple) -> None:
        self.season_range['first_season'] = season_range[0][0]
        self.season_range['last_season'] = season_range[0][1]


    def _scrape_season_range(self):
        league_scraper = LeagueScraper(url=self.url, page=self.page)
        self.season_range = league_scraper.get_season_range()


    def _generate_seasons(self) -> list[str]:
        first = self.season_range.get("first_season")
        last = self.season_range.get("last_season")
        if not first or not last:

            return []
        start_year = int(first.split("-")[0])
        end_year = int(last.split("-")[0])
        seasons = []
        for year in range(start_year, end_year + 1):
            next_year = year + 1
            seasons.append(f"{year}-{next_year}")

        return seasons


    @abstractmethod
    def _scrape_season_urls(self, seasons: str) -> None:
        pass


class PlayerURLScraper(URLScraper):


    def __init__(self, league_uid: str, page: Page, db_path: str):
        super().__init__(league_uid=league_uid, page=page, db_path=db_path)
        self.base_url = ELITE_URL + "/league/" + league_uid + "/stats/"


    def _scrape_season_urls(
            self, seasons: list[str]) -> dict[str, dict[str, list]]:
        scraped_data = {}
        for season in seasons:
            season_scraper = PlayerSeasonURLScraper(
                season=season, 
                page=self.page,
                league_uid=self.league_uid
                )
            scraped_data[season] = season_scraper.get_data()

        return scraped_data


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


class PlayerPageURLScraper(ABC):


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
        stats_table = sel.xpath(self.TABLE_XPATH)
        self.scraped_data.append(stats_table)
    

class SkaterPageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page=([0-9]+)"
    QUERY_STRING = "?page="
    TABLE_XPATH = "//div[@id='skater-stats']"


class GoaliePageURLScraper(PlayerPageURLScraper):


    PAGE_REGEX = "page-goalie=([0-9]+)"
    QUERY_STRING = "?page-goalie="
    TABLE_XPATH = "//div[@id='goalie-stats']"

    
