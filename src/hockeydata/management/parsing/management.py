import re 

from abc import ABC, abstractmethod
from datetime import datetime

import hockeydata.common_functions as cf

from hockeydata.constants import *
from hockeydata.database_get.storage_db.base import StorageDBDataGetter
from hockeydata.database_get.storage_db.url import PlayerURLHTMLDBDataGetter
from hockeydata.database_session.database_session import (ParseDBSession, 
                                                          ScrapeDBSession)
from hockeydata.entity_data.input_data.scraped.base import HTMLInputter
from hockeydata.entity_data.input_data.scraped.url import (PlayerURLInputter, 
                                                           URLInputter)
from hockeydata.management.parsing.paralel_management import MultiParseManager
from hockeydata.management.parsing.paralel_management import  PlayerURLMultiParseManager
from hockeydata.logger.logging_config import logger


class ParseManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def DB_GETTER(cls) -> type[StorageDBDataGetter]:
        pass


    @property
    @classmethod
    @abstractmethod
    def PARALEL_MANAGER(cls) -> type[MultiParseManager]:
        pass

    @property
    @classmethod
    @abstractmethod
    def TYPE(cls):
        pass


    def __init__(
            self, storage_db_path: str, filters: dict[str, list[int|str]]):
        self.storage_db_path = storage_db_path
        self.storage_session_manager: ScrapeDBSession = None
        self.filters = filters
        self.scraped_data = []
        self.start_time: datetime = None
        self.end_time: datetime = None


    def _set_storage_session(self) -> None:
        self.storage_session_manager = ScrapeDBSession(
            db_path=self.storage_db_path
            )
        self.storage_session_manager.set_up_connection()


    def close_storage_session(self) -> None:
        self.storage_session_manager.close()


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


    def _get_data(self):
        data_getter = self.DB_GETTER(
            db_session=self.storage_session_manager.session,
            filters=self.filters,
            )
        self.scraped_data = data_getter.get_data()


    @abstractmethod
    def _input_all_data(self, parsed_data: list[dict]) -> None:
        pass

    def _set_start_time(self) -> None:
        self.start_time = datetime.now()
        logger.debug("Started at %s", self.start_time)


    def _set_end_time(self) -> None:
        self.end_time = datetime.now()
        logger.debug("Ended at %s", self.end_time)


    def parse_data(self, max_workers: int=4) -> list[dict]:
        self._set_start_time()
        paralel_manager = self.PARALEL_MANAGER(
            max_workers=max_workers,
            scraped_data=self.scraped_data
            )
        parsed_data = paralel_manager.parse_data()
        self._set_end_time()

        return parsed_data


class ParseEntityManager(ParseManager):


    @property
    @classmethod
    @abstractmethod
    def DB_INSERTER(cls) -> type[HTMLInputter]:
        pass


    def __init__(
            self, storage_db_path: str, parsed_db_path: str, filters: dict):
        super().__init__(storage_db_path=storage_db_path, filters=filters)
        self.parsed_db_path = parsed_db_path
        self.parsed_session_manager: ParseDBSession = None


    def _set_parsed_session(self) -> None:
        self.parsed_session_manager = ParseDBSession(
            db_path=self.storage_db_path
            )
        self.parsed_session_manager.set_up_connection()


    def close_parsed_session(self) -> None:
        self.parsed_session_manager.close()


    def _input_all_data(self, parsed_data: list[dict]) -> None:
        data_inserter = self.DB_INSERTER(
            db_session=self.parsed_session_manager.session,
            parsed_data=parsed_data
            )
        data_inserter.input_scrape_log(
            start_time=self.start_time,
            end_time=self.end_time
        )
        data_inserter.input_data()


class URLSParseManager(ParseManager):


    @property
    @classmethod
    @abstractmethod
    def DB_INSERTER(cls) -> type[URLInputter]:
        pass


    def set_up(self) -> None:
        self._set_storage_session()
        self._get_data()


    def _input_all_data(
            self, parsed_data: list[dict[str, bytes|int|str]]) -> None:
        data_inserter = self.DB_INSERTER(
            db_session=self.storage_session_manager.session,
            parsed_data=parsed_data
            )
        data_inserter.input_parse_log(
            start_time=self.start_time,
            end_time=self.end_time
        )
        data_inserter.input_data()
        self.storage_session_manager.commit()


class PlayerURLSParseManager(URLSParseManager):


    DB_GETTER = PlayerURLHTMLDBDataGetter
    DB_INSERTER = PlayerURLInputter
    PARALEL_MANAGER = PlayerURLMultiParseManager
    TYPE = "player url"
