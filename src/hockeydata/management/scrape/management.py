import re 

from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.common_functions as cf
import hockeydata.database_creator.storage_database_creator as storage_db

from hockeydata.constants import *
from hockeydata.database_queries.database_query import StorageDBQuery
from hockeydata.database_session.database_session import ScrapeDBSession
from hockeydata.entity_data.input_data.scraped.base import HTMLInputter
from hockeydata.entity_data.input_data.scraped.url import PlayerURLHTMLInputter
from hockeydata.entity_data.scraper.base import LeagueSeasonRangeScraper
from hockeydata.entity_data.scraper.league_scraper import LeagueScraper
from hockeydata.management.scrape.paralel_management import MultiScrapeManager
from hockeydata.management.scrape.paralel_management import  PlayerURLMultiScrapeManager
from hockeydata.management.scrape.paralel_management import PlayerURLMultiScrapeManager
from hockeydata.entity_data.playwright_setup.playwright_setup import PlaywrightSetUp
from hockeydata.mappers.db_mappers import StorageDBMapper
from hockeydata.logger.logging_config import logger


class ScrapeManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def DB_INSERTER(cls) -> type[HTMLInputter]:
        pass

    @property
    @classmethod
    @abstractmethod
    def PARALEL_MANAGER(cls) -> type[MultiScrapeManager]:
        pass

 #   @property
 #   @classmethod
 #   @abstractmethod
 #   def SESSION_CLASS(cls) -> type[DatabaseSession]:
 #       pass

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls):
        pass


    def __init__(self, storage_db_path: str):
        self.storage_db_path = storage_db_path
        self.db_session: Session = None
        self.scrape_id: int = None
        self.start_time: datetime = None
        self.end_time: datetime = None


    def _set_session(self) -> None:
        db_session = ScrapeDBSession(db_path=self.storage_db_path)
        db_session.set_up_connection()
        self.db_session = db_session.session


  #  def get_session(
  #          self, db_path: str, 
  #          session_type: type[ScrapeDBSession|ParseDBSession]):
  #      session = session_type(db_path=db_path)
  #      session.set_up_connection()

   #     return session.session
    

    @abstractmethod
    def set_up(self, db_path: str):
        pass
        

   # def set_up_management(self):
   #     self._load_uid_status_mapper()
        

   # def _load_uid_status_mapper(self) -> None:
   #     self.uid_status_mapper =  self.GETDBID.get_parsed_data_statuses()


    def _input_all_data(self, data: list[dict]) -> None:
        data_inserter = self.DB_INSERTER(data=entity_dict)
        data_inserter.input_scrape_log(
            scrape_type=self.TYPE,
            start_time=self.start_time,
            end_time=self.end_time
        )
        for entity_dict in data:
            data_inserter.input_data()


    def _set_start_time(self) -> None:
        self.start_time = datetime.now()
        logger.debug("Started at %s", self.start_time)


    def _set_end_time(self) -> None:
        self.end_time = datetime.now()
        logger.debug("Ended at %s", self.end_time)


    def scrape_data(self, max_workers: int=4) -> list[dict]:
        self._set_start_time()
        paralel_manager = self.PARALEL_MANAGER(
            max_workers=max_workers,
            data=self.data
            )
        scraped_data = paralel_manager.scrape_data()
        self._set_end_time()

        return scraped_data


class EntityScrapeManager(ScrapeManager):


    @property
    @classmethod
    @abstractmethod
    def PARALEL_MANAGER(cls) -> type[MultiScrapeManager]:
        pass

    @property
    @classmethod
    @abstractmethod
    def REGEX_UID(cls) -> type[MultiScrapeManager]:
        pass

    @property
    @classmethod
    @abstractmethod
    def MAPPER(cls) -> type[StorageDBMapper]:
        pass


    def __init__(self):
        super().__init__()
        self.data: dict[str|int, str] = None


    def set_up(
            self, db_path: str, scrape_ids: list, 
            rescrape: bool) -> None:
        self._set_session(db_path=db_path)
        urls = self.get_urls(scrape_ids=scrape_ids)
        self._get_uid_to_url_mapper(urls=urls)
        if not rescrape:
            logger.info(
                "Rescrape set to True, already scraped data will"
                " be rescraped."
                )
            scraped_uids = self._load_scraped_uids(
                uids=self.data.keys()
                )
            self._filter_out_new_uids(
                scraped_uids=scraped_uids
                )
        else:
            logger.info(
                "Rescrape set to False, already scraped data will"
                "not  be rescraped."
                )


    def get_urls(self, scrape_ids: list) -> list:
        mapper = self.MAPPER(db_session=self.db_session)

        return mapper.get_urls(scrape_ids=scrape_ids)


    def _get_uid_to_url_mapper(self, urls: list) -> None:
        for url in urls:
            try:
                uid = re.findall(self.REGEX_UID, url)[0]
                self.data[uid] = url
            #add exception
            except Exception as e:
                error_message = (
                    f"URL is in a wrong format: {url}"       
                )
                cf.log_and_raise(error_message, ValueError)
        logger.info("%s UIDs extracted from URLs.", len(urls))


    def _load_scraped_uids(self, uids: list) -> set:
        db_mapper = self.MAPPER(db_session=self.db_session)
        scraped_uids =  db_mapper.get_scraped_uids(
            uids=uids
            )
        logger.info("%s scraped UIDs loaded. ", len(scraped_uids))

        return scraped_uids


    def _filter_out_new_uids(
            self, scraped_uids: set) -> None:
        keep_uids = list(set(self.data.keys()) - scraped_uids)
        self.data = {
            uid: url 
            for uid, url in self.data.items() 
            if uid in keep_uids
            }
        logger.info("UIDs for already scraped players filtered out. %s UIDs "
                    " left to scrape.", len(self.data))
        

    def scrape_data(self, max_workers: int=None) -> list[dict]:
        self._set_start_time()
        paralel_manager = self.PARALEL_MANAGER(
            db_session=self.db_session,
            max_workers=max_workers,
            data=self.data
            )
        scraped_data = paralel_manager.scrape_data()
        self._set_end_time()

        return scraped_data
    

class PlayerURLScrapeManager(ScrapeManager):


    DB_INSERTER = PlayerURLHTMLInputter
    PARALEL_MANAGER = PlayerURLMultiScrapeManager
    TYPE = "player_url"


    def __init__(self, storage_db_path:str, league_uid: str):
        super().__init__(storage_db_path=storage_db_path)
        self.data = {
            "seasons": [],
            "league_uid": league_uid
        }
        self.season_range = {
            "first_season": None,
            "last_season": None
        }


    def set_up(self) -> None:
        self._set_session()
        self._add_season_range()
        self._get_seasons()


    def _add_season_range(self) -> None:
        season_range_set = self._check_season_range_in_db()
        if season_range_set:
            return
        season_range = self._scrape_season_range()
        self._set_season_range(season_range=season_range)


    def _check_season_range_in_db(self) -> bool:
        query = StorageDBQuery(db_session=self.db_session)
        filter_ = [storage_db.LeagueInfo.uid.is_(self.data["league_uid"])]
        season_range = query.get_db_query_result(
             query_name="year_range", 
             filters=filter_
             )
        #update based on return value
        if all(value is None for value in season_range[0]):
            logger.info(
                "Season range for league %s not yet in DB. Scrape will proceed",
                self.data["league_uid"]
                )
            
            return False
        else:
            logger.info(
                "Season range for league %s fetched from DB.",
                self.data["league_uid"]
                )
            self._set_season_range(season_range=season_range)
            
            return True 


    def _set_season_range(self, season_range: tuple) -> None:
        self.season_range['first_season'] = season_range[0][0]
        self.season_range['last_season'] = season_range[0][1]
    

    def _scrape_season_range(self) -> tuple[str, str]:
        range_scraper = LeagueSeasonRangeScraper(
            league_uid=self.data["league_uid"]
            )
        season_range = range_scraper._get_season_range()

        return season_range
    

    def _get_seasons(self):
        first_season = self.season_range['first_season']
        last_season = self.season_range['last_season']
        self.data["seasons"] = cf.create_season_list(
            first_season=first_season, 
            last_season=last_season
            )