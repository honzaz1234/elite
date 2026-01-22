from abc import ABC, abstractmethod
from datetime import datetime


from hockeydata.database_session.database_session import ParseDBSession
from hockeydata.database_session.database_session import ScrapeDBSession
from hockeydata.entity_data.input_data.scraped.base import HTMLInputter
from hockeydata.entity_data.input_data.scraped.player import PlayerHTMLInputter
from hockeydata.logger.logging_config import logger


class DBManager(ABC):


    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.session: type[ParseDBSession|ScrapeDBSession] = None


    def initiate_db_session(self) -> None:
        get_session = self.DB_MANAGER(db_path=self.db_path)
        self.session = get_session.session
        logger.debug(
            "DB session at path %s succesfully initiated.", 
            self.db_path
            )


class ScrapeInsertManager(DBManager):


    DB_MANAGER = ScrapeDBSession


    @property
    @classmethod
    @abstractmethod
    def INSERT_CLASS(cls) -> type[HTMLInputter]:
        pass


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls):
        pass


    def __init__(
            self, db_path: str, data: list[dict], start_time: datetime, end_time: datetime):
        super().__init__(db_path=db_path)
        self.data = data
        self.scrape_id: int|None = None
        self.start_time = start_time
        self.end_time = end_time


    def _set_scrape_id(self) -> None:
        self.scrape_id = self.session.create_scrape_table_entry(
            type_=self.TYPE
            )
        logger.info("Starting scrape n. %s...", self.scrape_id)


    def input_data(self) -> None:
        self._set_scrape_id()
        self._input_all_data()


    def _input_all_data(self) -> None:
        for entity_dict in self.data:
            data_inserter = self.INSERT_CLASS(data=entity_dict)
            data_inserter.input_data()


    def input_log(self) -> None:
        log_inputter = self.INSERT_CLASS(
            db_session=self.session,
            scrape_id=self.scrape_id,
            start_time=self.start_time,
            end_time=self.end_time,
            scrape_type=self.TYPE
        )
        log_inputter.input_data()


class PlayerScrapeInsertManager(ScrapeInsertManager):


    INSERT_CLASS = PlayerHTMLInputter
    TYPE = "player"


class ParseInsertManager(DBManager):


    DB_MANAGER = ParseDBSession


    def __init__(self, db_path: str):
        super().__init__(db_path=db_path)