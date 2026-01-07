from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import DatabaseMethods, Query
from hockeydata.logger.logging_config import logger


class HTMLInputter():
    """Parent class for handling inputting downloaded html files into storage  
       DB
    """


    def __init__(
            self, db_session: Session, scrape_id: int):
        self.insert_db = DatabaseMethods(db_session=db_session)
        self.scrape_id = scrape_id


    def input_data(self) -> None:
        pass


class LogInputter(HTMLInputter):


    def __init__(
            self, db_session: Session, scrape_id: int, 
            start_time: datetime, end_time: datetime, scrape_type: str
            ):
        super().__init__(
            db_session=db_session, scrape_id=scrape_id
            )
        self.query = Query(db_session=db_session)
        self.db_session = db_session
        self.start_time = start_time
        self.end_time = end_time
        self.scrape_type = scrape_type


    def _input_log(self):
        scrape_type_id = self.query._find_id_in_table(
            table=db.ScrapeType, 
            scrape_type=self.scrape_type
            )
        self.player_id = self.insert_db._input_data(
            table=db.Scrape, 
            start_datetime=self.start_time,
            end_datetime=self.end_time,
            scrape_type_id=scrape_type_id
            )
        #maybe delete later?
        self.db_session.commit()


class PlayerHTMLInputter(HTMLInputter):


    def __init__(
            self, db_session: Session, scraped_data: dict, missing_data: dict, scrape_id: int):
        super().__init__(
            db_session=db_session, scrape_id=scrape_id
            )
        self.db_session = db_session
        self.scraped_data = scraped_data
        self.missing_data = missing_data
        self.is_goalie = None
        self.player_uid = None 
        self.player_id = None


    def input_data(self) -> None:
        self._set_is_goalie()
        self._set_player_uid()
        self._input_player_log()
        self._input_player_facts_html()
        self._input_achievements_html()
        self._input_stats_htmls()
        self._input_missing_data_logs()
        #to be deleted later
        self.db_session.commit()
        logger.info(
            'Data for player %s succesfully inputed into storage DB.', 
            self.player_uid
            )
    

    def _set_is_goalie(self) -> None:

        """method for establishing if the player is goalie or field player; important because of different structure of downloaded html
        """

        position = self.scraped_data["player_type"]
        if position == "G":
            self.is_goalie =  True
        else:
            self.is_goalie = False


    def _set_player_uid(self) -> None:
        self.player_uid = self.scraped_data["player_uid"]


    def _input_player_log(self):
        self.player_id = self.insert_db._input_data(
            table=db.PlayerLog, player_uid=self.player_uid,
            is_goalie=self.is_goalie,
            scrape_id=self.scrape_id
            )


    def _input_player_facts_html(self) -> None:
        self.insert_db._input_data(
            table=db.PlayerFacts, player_id=self.player_id,
            html_data=self.scraped_data["player_facts"]
            )
        

    def _input_achievements_html(self) -> None:
        self.insert_db._input_data(
            table=db.Achievements, player_id=self.player_id,
            html_data=self.scraped_data["achievements"]
            )
        

    def _input_stats_htmls(self):
        if self.is_goalie:
            stats_class = InputGoalieStatsHtml(
                scraped_data=self.scraped_data['stats'], 
                insert_db=self.insert_db,
                player_id=self.player_id
                ) 
        else:
            stats_class = InputSkaterStatsHtml(
                scraped_data=self.scraped_data['stats'], 
                insert_db=self.insert_db,
                player_id=self.player_id
                ) 
        stats_class._input_data()


    def _input_missing_data_logs(self) -> None:
        for data_type in self.missing_data:
            self.insert_db._input_data(
                db.PlayerMissingDataLog, 
                player_id=self.player_id, 
                data_type=data_type
            )


class InputStatsHtml():


    def __init__(
            self, scraped_data: dict, insert_db: DatabaseMethods, 
            player_id: int):
        self.scraped_data = scraped_data
        self.insert_db = insert_db
        self.player_id = player_id


    def _input_data(self) -> None:
        pass


class InputGoalieStatsHtml(InputStatsHtml):
    

    def _input_data(self) -> None:
        for competition_type in self.scraped_data:
            if self.scraped_data[competition_type] is None:
                continue
            for season_type in self.scraped_data[competition_type]:
                self.insert_db._input_data(
                    table=db.GoalieStats, 
                    player_id=self.player_id,
                    competition_type=competition_type, 
                    season_type=season_type, 
                    html_data=self.scraped_data[competition_type][season_type]
                    )
        

class InputSkaterStatsHtml(InputStatsHtml):
    

    def _input_data(self) -> None:
        for competition_type in self.scraped_data:
            if self.scraped_data[competition_type] is None:
                continue
            for competition_type in self.scraped_data:
                self.insert_db._input_data(
                    table=db.SkaterStats, 
                    player_id=self.player_id,
                    competition_type=competition_type, 
                    html_data=self.scraped_data[competition_type]
                    )



        