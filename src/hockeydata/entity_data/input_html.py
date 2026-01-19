from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import DatabaseMethods, Query
from hockeydata.logger.logging_config import logger


class HTMLInputter(ABC):
    """Parent class for handling inputting downloaded html files into storage  
       DB
    """


    def __init__(
            self, db_session: Session):
        self.db_session = db_session
        self.insert_db = DatabaseMethods(db_session=db_session)
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
        super().__init__(db_session=db_session)
        self.scraped_data = scraped_data
        self.db_id = None


    @abstractmethod
    def _input_log(self) -> None:
        pass


    @abstractmethod
    def _input_missing_data_logs(self) -> None:
        pass


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


class InputStatsHtml():


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
                

class LeagueHTMLInputter(HTMLEntityInputter):


    def input_data(self) -> None:
        self._input_log()
        self.update_season_range()
        self._input_league_name_html()
        self._input_achievements_html()
        self._input_stats_htmls()
        self._input_missing_data_logs()
        self.db_session.commit()
        logger.info(
            'Data for league %s succesfully inputed into storage DB.', 
            self.scraped_data["uid"]
            )
        

    def _input_log(self) -> None:
        query = Query(db_session=self.db_session)
        league_id = query._find_id_in_table(
            table=db.LeagueInfo,
            uid=self.scraped_data["uid"]
            )
        self.db_id = self.insert_db._input_data(
            table=db.LeagueLog, 
            league_id=league_id,
            scrape_id=self.scrape_id,
            time_scraped=self.scraped_data['time_scraped']
            )
        

    def update_season_range(self) -> None:
        self.insert_db._update_data(
            table=db.LeagueInfo,
            where_col=db.LeagueInfo.uid,
            where_val=self.scraped_data["uid"],
            first_season=self.scraped_data["season_range"]["first_season"],
            last_season=self.scraped_data["season_range"]["last_season"],
            last_update=datetime.now()
            )


    def _input_league_name_html(self) -> None:
        self.insert_db._input_data(
            table=db.LeagueName, 
            league_id=self.db_id,
            html_data=self.scraped_data["league_name"]
            )
        

    def _input_achievements_html(self) -> None:
        self.insert_db._input_data(
            table=db.LeagueAchievement, 
            league_id=self.db_id,
            html_data=self.scraped_data["achievements"]
            )
        

    def _input_stats_htmls(self) -> None:
        insert_list = []
        for season in self.scraped_data["stats"]:
            dict_ = {
                "html_data": self.scraped_data["stats"][season],
                "league_id": self.db_id
            }
            insert_list.append(dict_)
        self.insert_db.insert_update_or_ignore_on_conflict_bulk(
            table=db.LeagueSeason,
            data=insert_list,
            update=False
            )
        

    def _input_missing_data_logs(self) -> None:
        for data_type in self.scraped_data["missing_data"]:
            self.insert_db._input_data(
                db.LeagueMissingDataLog, 
                league_id=self.db_id, 
                data_type=data_type
                )



        