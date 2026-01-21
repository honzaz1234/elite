import re 

from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.common_functions as cf

from hockeydata.constants import *
from hockeydata.database_creator.database_creator import *
from hockeydata.database_session.database_session import DatabaseSession, ParseDBSession, ScrapeDBSession
from hockeydata.entity_data.input_html import HTMLInputter
from hockeydata.management.paralel_manager import MultiScrapeManager
from hockeydata.mappers.db_mappers import StorageDBMapper
from hockeydata.logger.logging_config import logger


class Manager(ABC):


    REGEX_UID = None
    SCRAPE_MANAGER = None
    PARSE_MANAGER = None
    INPUT_MANAGER = None
    SCRAPE_DICT = None 
    UPDATE_DICT = None
    INPUT_DICT = None
    GETDBID = None
    TYPE = None


    @property
    @classmethod
    @abstractmethod
    def DB_INSERTER(cls) -> type[HTMLInputter]:
        pass

    @property
    @classmethod
    @abstractmethod
    def SESSION_CLASS(cls) -> type[DatabaseSession]:
        pass


    def __init__(self):
        self.db_session: Session = None
        self.scrape_id: int = None
        self.start_time: datetime = None
        self.end_time: datetime = None


    def set_session(self, db_path: str) -> None:
        self.db_session = self.get_session(
            db_path=db_path,
            session_type=self.SESSION_CLASS
            )    


    def get_session(
            self, db_path: str, 
            session_type: type[ScrapeDBSession|ParseDBSession]):
        session = session_type(db_path=db_path)
        session.set_up_connection()

        return session.session
    

    @abstractmethod
    def set_up(self, db_path: str):
        pass
        

    def set_up_management(self):
        self._load_uid_status_mapper()
        

    def _load_uid_status_mapper(self) -> None:
        self.uid_status_mapper =  self.GETDBID.get_parsed_data_statuses()


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


class EntityScrapeManager(Manager):


    @property
    @classmethod
    @abstractmethod
    def PARALEL_MANAGER(cls) -> type[MultiScrapeManager]:
        pass

    @property
    @classmethod
    @abstractmethod
    def MAPPER(cls) -> type[StorageDBMapper]:
        pass

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls):
        pass


    SESSION_CLASS = ScrapeDBSession


    def __init__(self):
        super().__init__()
        self.uid_url_mapper: dict[str|int, str] = None


    def set_up(
            self, db_path: str, scrape_ids: list, 
            rescrape: bool) -> None:
        self.set_session(db_path=db_path)
        urls = self.get_urls(scrape_ids=scrape_ids)
        self._get_uid_to_url_mapper(urls=urls)
        if not rescrape:
            logger.info(
                "Rescrape set to True, already scraped data will"
                " be rescraped."
                )
            scraped_uids = self._load_scraped_uids(
                uids=self.uid_url_mapper.keys()
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
                self.uid_url_mapper[uid] = url
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
        keep_uids = list(set(self.uid_url_mapper.keys()) - scraped_uids)
        self.uid_url_mapper = {
            uid: url 
            for uid, url in self.uid_url_mapper.items() 
            if uid in keep_uids
            }
        logger.info("UIDs for already scraped players filtered out. %s UIDs "
                    " left to scrape.", len(self.data))
        

    def scrape_data(self, max_workers: int=None) -> list[dict]:
        self._set_start_time()
        paralel_manager = self.PARALEL_MANAGER(
            db_session=self.db_session,
            max_workers=max_workers,
            data=self.uid_url_mapper
            )
        scraped_data = paralel_manager.scrape_data_with_multiple_processes()
        self._set_end_time()

        return scraped_data
    

    