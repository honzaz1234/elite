import hockeydata.common_functions as cf
import hockeydata.database_creator.database_creator as db
import hockeydata.database_insert.db_insert  as db_insert
import hockeydata.entity_data.get_urls.get_urls as league_url

from hockeydata.constants import *
from hockeydata.logger.logging_config import logger

from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import Table


class GetDatabaseSession():
    """class which purpose is to manage scraping of all available entities including establishing connection to the database
    """

    def __init__(self, db_path: str):

        self.database_path = db_path
        self.engine = None
        self.session = None
        self.meta_data = None


    def set_up_connection(self) -> None:
        logger.info("New scrapping session started")
        self.start_session()
        are_seasons_filled = self.check_seasons_table()
        if are_seasons_filled==False:
            self.add_data_to_season_table()


    def start_session(self) -> None:
        self.engine = create_engine("sqlite:///" + self.database_path, echo=False)
        db.Base.metadata.create_all(bind=self.engine)
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
        self.meta_data = db.Base.metadata
        logger.info(
            "New DB session initiated with db at %s", 
            self.database_path
                    )


    def clear_all_tables(self) -> None:
        if 'test' not in self.database_path.lower():
            error_message = (
                f"Data deletion is not allowed on the" 
                f"database  as {self.database_path}' does not"
                f" contain 'test'."
                )
            cf.log_and_raise(error_message, ValueError)
        for table in self.meta_data.sorted_tables:
            self.session.execute(text(f"DELETE FROM {table.name};"))
        logger.info(
            "Data from all tables in db %s has been deleted", 
            self.database_path
            )

        self.session.commit()


    def check_seasons_table(self) -> bool:
        check_data = self.session.query(db.Season).all()
        if check_data == []:
            return False
        return True


    def add_data_to_season_table(self) -> None:
        self.add_seasons_to_seasons_table()
        self.add_years_to_seasons_table()
     #   self.add_data_to_stadium_mapper_table()
      #  self.add_data_to_reference_tables()
        self.session.commit()
        logger.debug("Season, Year, Stadium Mapper and Reference Table values"
                     "added to the db.")


    def add_seasons_to_seasons_table(self) -> None:
        league_getter = league_url.LeagueUrlDownload()
        season_list = league_getter.create_season_list(1886, 2024)
        seasons_insert = []
        for season in season_list:
            seasons_insert.append({"season": season})
        self.session.bulk_insert_mappings(db.Season, seasons_insert)


    def add_years_to_seasons_table(self) -> None:
        years = [*range(1886, 2025, 1)]
        years_insert = []
        for year in years:
            years_insert.append({"season": year})
        self.session.bulk_insert_mappings(db.Season, years_insert)


    def add_data_to_stadium_mapper_table(self, stadium_mapper: list) -> None:
        stadium_mapper_insert = []
        for row in stadium_mapper:
            stadium_mapper_insert.append(row)
        self.session.bulk_insert_mappings(db.StadiumMapper, stadium_mapper_insert)


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
        self.session.bulk_insert_mappings(
            db.StadiumMapper, reference_table_insert)


    def create_scrape_table_entry(self, type_: str) -> int:
        insert_o = db_insert.DatabaseMethods(db_session=self.session)
        scrape_id = insert_o._input_data(
            table=db.ScrapeLog, type=type_,
            time_start=datetime.now()
            )
        self.session.commit()

        return scrape_id

        




        





           

