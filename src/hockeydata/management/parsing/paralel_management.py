import math
import multiprocessing 
import re

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generator


import common_functions as cf

from database_session.database_session import ParseDBSession, ScrapeDBSession
from hockeydata.entity_data.storage_db_getter.storage_db_getter import GoalieStorageDBDataGetter, StorageDBDataGetter, SkaterStorageDBDataGetter
from management.scrape_management import ScraperManager, ParserManager, PlayerScraperManager
from hockeydata.mappers.db_mappers import DBMapper, PlayerStorageDBMapper
from hockeydata.logger.logging_config import logger


def scrape_worker(
        args: tuple[str, dict[int, str], type[ParserManager|ScraperManager]]) -> list[Any]:
    db_path, url_mapper, manager_class  = args

    manager = manager_class(
        url_mapper=url_mapper
    )
    manager.initiate_playwright_session()
    processed_data = manager.process()

    return processed_data


class MultiManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        pass


    def __init__(
            self, db_path: str, data: dict[int|str, str], max_workers: int=4):
        self.db_path = db_path
        self.max_workers = max_workers
        self.data = data
        self.chunk_size = None


    @abstractmethod
    def set_up_manager(self) -> None:
        pass
    
    
    @abstractmethod
    def _set_chunk_size(self, data: list) -> None:
        self.chunk_size = math.ceil(len(data) / self.max_workers)
        logger.info(
            'Data will be divided between %s chunks of size %s', 
            self.max_workers,
            self.chunk_size
            )


    def _chunk_uids(self) -> Generator[dict[str, int], None, None]:
        keys = list(self.data.keys())
        for i in range(0, len(keys), self.chunk_size):
            chunk_keys = keys[i:i + self.chunk_size]
            yield {k: self.data[k] for k in chunk_keys}


class MultiParseManager(MultiManager):


    @property
    @classmethod
    @abstractmethod
    def DB_MAPPER(cls) -> type[StorageDBDataGetter]:
        pass

    STORAGE_DB_GETTER = type[StorageDBDataGetter]


    def __init__(
            self, db_path: str, max_workers:int, scrape_ids: list[int], 
            uids: list=None, update: bool=False):
        super().__init__(db_path=db_path, max_workers=max_workers)
        self.scrape_ids = scrape_ids
        self.uids = uids
        self.update = update
        self._set_chunk_size(data=uids)


    def set_up_manager(self):
        self._load_data()
        self._set_chunk_size(data=self.data)
        if not self.update:
            mapper_getter = 
            status_mapper = 



    def _load_data(self) -> None:
        storage_db_getter = self.STORAGE_DB_GETTER(
            db_path=self.db_path,
            scrape_ids=self.scrape_ids,
            uids=self.uids
            )
        self.scraped_data =  storage_db_getter.get_data(
            )
        logger.info(
            "%s scraped %s from scrapes %s loaded", 
            len(self.scraped_data),
            self.TYPE,
            self.scrape_ids
            )

