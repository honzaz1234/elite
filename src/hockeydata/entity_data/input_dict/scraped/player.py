from abc import abstractmethod
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import DatabaseMethods
from hockeydata.entity_data.input_dict.scraped.base import HTMLEntityInputter
from hockeydata.logger.logging_config import logger



class PlayerHTMLInputter(HTMLEntityInputter):


    def __init__(
            self, db_session: Session, scraped_data: dict):
        super().__init__(
            db_session=db_session, 
            scraped_data=scraped_data
            )
        self.is_goalie = None


    def input_data(self) -> None:
        self._set_is_goalie()
        self._input_log()
        self._input_player_facts_html()
        self._input_achievements_html()
        self._input_stats_htmls()
        self._input_missing_data_logs()
        self.db_session.commit()
        logger.info(
            'Data for player %s succesfully inputed into storage DB.', 
            self.scraped_data["uid"]
            )
    

    def _set_is_goalie(self) -> None:

        """method for establishing if the player is goalie or field player; important because of different structure of downloaded html
        """

        position = self.scraped_data["player_type"]
        if position == "G":
            self.is_goalie =  True
        else:
            self.is_goalie = False


    def _input_log(self):
        self.db_id = self.insert_db._input_data(
            table=db.PlayerLog, 
            uid=self.scraped_data["uid"],
            is_goalie=self.is_goalie,
            scrape_id=self.scrape_id,
            time_scraped=self.scraped_data['time_scraped']
            )


    def _input_player_facts_html(self) -> None:
        self.insert_db._input_data(
            table=db.PlayerFacts, 
            player_id=self.db_id,
            html_data=self.scraped_data["player_facts"]
            )
        

    def _input_achievements_html(self) -> None:
        self.insert_db._input_data(
            table=db.PlayerAchievements, 
            player_id=self.db_id,
            html_data=self.scraped_data["achievements"]
            )
        

    def _input_stats_htmls(self):
        if self.is_goalie:
            stats_class = InputGoalieStatsHtml(
                scraped_data=self.scraped_data['stats'], 
                insert_db=self.insert_db,
                player_id=self.db_id
                ) 
        else:
            stats_class = InputSkaterStatsHtml(
                scraped_data=self.scraped_data['stats'], 
                insert_db=self.insert_db,
                player_id=self.db_id
                ) 
        stats_class._input_data()


    def _input_missing_data_logs(self) -> None:
        for data_type in self.scraped_data["missing_data"]:
            self.insert_db._input_data(
                db.PlayerMissingDataLog, 
                player_id=self.db_id, 
                data_type=data_type
            )


class InputStatsHtml(ABC):


    def __init__(
            self, scraped_data: dict, insert_db: DatabaseMethods, 
            player_id: int):
        self.scraped_data = scraped_data
        self.insert_db = insert_db
        self.db_id = player_id


    @abstractmethod
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
                    player_id=self.db_id,
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
                    player_id=self.db_id,
                    competition_type=competition_type, 
                    html_data=self.scraped_data[competition_type]
                    )