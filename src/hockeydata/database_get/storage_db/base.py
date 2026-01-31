from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute

import hockeydata.database_creator.storage_database_creator as storage_db

from hockeydata.database_queries.database_query import StorageDBQuery
from hockeydata.logger.logging_config import logger


class TableDataGetter(ABC):


    @property
    @classmethod
    @abstractmethod
    def DB_QUERY(cls) -> str:
        pass


    def __init__(
            self, db_query: StorageDBQuery, filters: list, data: dict|list):
            self.db_query = db_query
            self.filters = filters
            self.data = data


    def get_data(self) -> None:
        raw_data = self.db_query.get_db_query_result(
            query_name=self.DB_QUERY,
            filters=self.filters
            )
        for row in raw_data:
            self.save_info(row=row)
    

    @abstractmethod
    def save_info(self, row: tuple) -> None:
        pass


class StorageDBDataGetter(ABC):


    @property
    @classmethod
    @abstractmethod
    def ALLOWED_FILTERS(cls) -> str:
        pass


    FILTER_MAPPER = {
        "scrape_id":  storage_db.Scrape.id,
        "season": storage_db.Season.season,
        "league_uid": storage_db.LeagueInfo.uid
        }


    def __init__(self, db_session: Session, filters: list):
        self.db_query = StorageDBQuery(db_session=db_session)
        self.filters = []
        if "scrape_id" not in filters:
             raise Exception
        for col in filters:
            if col not in (
                *self.ALLOWED_FILTERS,
                "scrape_id",
            ):
                raise Exception
            filter_ = self.FILTER_MAPPER[col].in_(filters[col])
            self.filters.append(filter_)


    @abstractmethod
    def get_data(self) -> dict:
        pass


class StorageEntityDBDataGetter(StorageDBDataGetter):
    
    
    @property
    @classmethod
    @abstractmethod
    def RETURN_TEMPLATE(cls) -> dict:
        pass

    @property
    @classmethod
    @abstractmethod
    def UID_QUERY(cls) -> dict:
        pass


    def __init__(self, db_session: Session, filters: list):
        super().__init__(db_session=db_session, filters=filters)
        if "uids" in filters:
             uids = filters["uids"]
        else:
             logger.info(
                 "No UID filter selected. UIDs will be attained " 
                  "based on Scrape IDs"
                  )
             uids = self._get_uids(scrape_ids=filters["scrape_ids"])
        self.data = {
             uid: self.RETURN_TEMPLATE
             for uid in uids
        }


    @abstractmethod
    def _get_uids(self) -> list:
        output = self.db_query.get_db_query_result(
             query_name=self.UID_QUERY,
             filters=self.filters
        )
        
        return [row[0] for row in output]