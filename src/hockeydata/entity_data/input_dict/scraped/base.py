from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import DatabaseMethods, Query


class HTMLInputter(ABC):
    """Parent class for handling inputting downloaded html files into storage  
       DB
    """


    def __init__(
            self, db_session: Session, scraped_data: dict):
        self.db_session = db_session
        self.insert_db = DatabaseMethods(db_session=db_session)
        self.scraped_data = scraped_data
        self.query = Query(db_session=db_session)
        self.scrape_id: int|None = None


    @abstractmethod
    def input_data(self) -> None:
        pass


    def input_scrape_log(self, scrape_type: str, start_time: datetime, 
                         end_time: datetime) -> None:
        scrape_type_id = self.query._find_id_in_table(
            table=db.ScrapeType, 
            scrape_type=scrape_type
            )
        self.scrape_id = self.insert_db._input_data(
            table=db.Scrape, 
            start_datetime=start_time,
            end_datetime=end_time,
            scrape_type_id=scrape_type_id
            )
        #maybe delete later?
        self.db_session.commit()


class HTMLEntityInputter(HTMLInputter):
    """Parent class for handling inputting downloaded html files into storage  
       DB
    """


    def __init__(
            self, db_session: Session, scraped_data: dict):
        super().__init__(db_session=db_session, scraped_data=scraped_data)
        self.db_id = None


    @abstractmethod
    def _input_log(self) -> None:
        pass


    @abstractmethod
    def _input_missing_data_logs(self) -> None:
        pass