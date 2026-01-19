import re

from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.schema import MetaData, Table
from types import ModuleType


import hockeydata.common_functions as cf
import hockeydata.database_creator.database_creator as db
import hockeydata.database_creator.storage_database_creator as storage_db
import hockeydata.database_insert.db_insert  as db_insert
import hockeydata.entity_data.get_urls.get_urls as league_url


from hockeydata.constants import *
from hockeydata.database_insert.db_insert import DatabaseMethods
from hockeydata.database_insert.db_insert import  ParsedDatabaseMethods
from hockeydata.database_insert.db_insert import  StorageDatabaseMethods
from hockeydata.entity_data.get_urls.league_uids import LEAGUE_UIDS
from hockeydata.logger.logging_config import logger


class DatabaseSession(ABC):
    """class which purpose is to manage scraping of all available entities including establishing connection to the database
    Arguments:
        db_path - path to the database file or in case id does not exist yet 
        where it should be saved
        db_source - 
    """


    @property
    @classmethod
    @abstractmethod
    def DB_CONTROL(cls) -> type[DatabaseMethods]:
        pass


    @property
    @classmethod
    @abstractmethod
    def DB_SOURCE(cls) -> type[ModuleType]:
        pass


    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine: Engine = None
        self.session: Session = None
        self.db_control: DatabaseMethods = None
        self.meta_data: MetaData = None
        self.scrape_id: int = None


    def start_session(self) -> None:
        self.engine = create_engine(
            "sqlite:///" + self.db_path, echo=False
            )
        self.DB_SOURCE.Base.metadata.create_all(bind=self.engine)
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
        self.meta_data = self.DB_SOURCE.Base.metadata
        logger.info(
            "New DB session initiated with db at %s", 
            self.db_path
                    )
        

    def set_up_db_control(self) -> None:
        self.db_control = self.DB_CONTROL(db_session=self.session) 


    @abstractmethod
    def add_data_to_tables(self) -> None:
        pass


    def clear_all_tables(self) -> None:
        if 'test' not in self.db_path.lower():
            error_message = (
                f"Data deletion is not allowed on the" 
                f"database  as {self.db_path} does not"
                f" contain 'test'."
                )
            cf.log_and_raise(error_message, ValueError)
        for table in self.meta_data.sorted_tables:
            self.session.execute(text(f"DELETE FROM {table.name};"))
        logger.info(
            "Data from all tables in db %s has been deleted", 
            self.db_path
            )

        self.session.commit()


    def check_is_table_empty(self, table: Table) -> bool:
        check_data = self.session.query(table).all()
        if check_data == []:
            return False
        return True
    

    def close_session(self) -> None:
        self.session.close()
        logger.debug("DB session closed.")


    def add_seasons_to_seasons_table(self) -> None:
        league_getter = league_url.LeagueUrlDownload()
        season_list = league_getter.create_season_list(1886, 2024)
        seasons_insert = []
        for season in season_list:
            seasons_insert.append({"season": season})
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=self.DB_SOURCE.Season,
            data=seasons_insert,
            update=False
            )


    def add_years_to_seasons_table(self) -> None:
        years = [*range(1886, 2025, 1)]
        years_insert = []
        for year in years:
            years_insert.append({"season": year})
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=self.DB_SOURCE.Season,
            data=years_insert,
            update=False,
            )


class ParseDBSession(DatabaseSession):
    """Class managing session used for connection with DB storing parsed data
       of games and hockey entitites (players, leagues, teams)"""
    

    DB_CONTROL = ParsedDatabaseMethods
    DB_SOURCE = db
    

    def __init__(self, db_path):
        super().__init__(db_path=db_path)
    

    def set_up_connection(self) -> None:
        logger.info("New parsing session started")
        self.start_session()
        self.set_up_db_control()
        are_seasons_filled = self.check_is_table_empty(
            table=db.Season
            )
        if are_seasons_filled==False:
            self.add_data_to_tables()


    def add_data_to_tables(self) -> None:
        self.add_seasons_to_seasons_table()
        self.add_years_to_seasons_table()
        #add after the data is at least almost complete
     #   self.add_data_to_stadium_mapper_table()
      #  self.add_data_to_reference_tables()
        self.add_data_to_status_type_table()
        self.session.commit()
        logger.debug("Season, Year, Stadium Mapper and Reference Table values"
                     "added to the db.")


    def add_data_to_stadium_mapper_table(self, stadium_mapper: list) -> None:
        stadium_mapper_insert = []
        for row in stadium_mapper:
            stadium_mapper_insert.append(row)
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=db.StadiumMapper,
            data=stadium_mapper_insert,
            update=False
            )


    def add_data_to_reference_tables(
            self, reference_table_mapper: dict) -> None:
        for table in reference_table_mapper:
            self.add_data_to_reference_table(
                reference_table_mapper[table], table
                )


    def add_data_to_reference_table(
            self, reference_table_mapper: list, table: Table) -> None:
        reference_table_insert = []
        for row in reference_table_mapper:
            reference_table_insert.append(row)
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=table,
            data=reference_table_insert,
            update=False
            )
        

    def add_data_to_status_type_table(self) -> None:
        status_types_insert  = [
            {"status_type": "uid_insert"}, 
            {"status_type": "complete_insert"}, 
            {"status_type": "empty_update"}, 
            {"status_type": "update"}
            ]
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=db.StatusType,
            data=status_types_insert,
            update=False
            )


class ScrapeDBSession(DatabaseSession):
    """Class managing session used for connection with DB storing raw scraped 
       HTML data of games and hockey entitites (players, leagues, teams)"""
    

    DB_CONTROL = StorageDatabaseMethods
    DB_SOURCE = storage_db
    SCRAPE_TYPES = ["game", "player", "league", "team"]


    def __init__(self, db_path):
        super().__init__(db_path=db_path)


    def set_up_connection(self) -> None:
        logger.info("New scraping session started at path %s...", self.db_path)
        self.start_session()
        self.set_up_db_control()
        self.add_data_to_tables()


    def add_data_to_tables(self) -> None:
        self.add_seasons_to_seasons_table()
        self.add_years_to_seasons_table()
        self.add_scrape_types_to_scrape_types_table()
        self.add_league_info_to_league_info_table()
        self.session.commit()


    def add_scrape_types_to_scrape_types_table(self) -> None:
        scrape_type_insert = []
        for scrape_type in self.SCRAPE_TYPES:
            scrape_type_insert.append({"scrape_type": scrape_type})
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=storage_db.ScrapeType,
            data=scrape_type_insert,
            update=False
            )
        

    def add_league_info_to_league_info_table(self) -> None:
        insert_info = []
        for league_name in LEAGUE_UIDS:
            uid = re.findall('league\/(.+)$',LEAGUE_UIDS[league_name])[0]
            insert_info.append(
                {
                    "elite_name": league_name, 
                    "uid": uid,
                    "last_update": datetime.now()
                    }
            )
        self.db_control.insert_update_or_ignore_on_conflict_bulk(
            table=storage_db.LeagueInfo,
            data=insert_info,
            update=False
            )
        

    def create_scrape_table_entry(self, type_: str) -> int:
        self.db_control = self.DB_CONTROL(db_session=self.session)
        self.scrape_id = self.db_control._input_data(
            table=storage_db.Scrape, 
            type=type_,
            time_start=datetime.now()
            )
        self.session.commit()

        




        





           

