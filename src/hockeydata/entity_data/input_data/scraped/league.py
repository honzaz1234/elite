from abc import abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import Query
from hockeydata.entity_data.input_data.scraped.base import HTMLEntityInputter
from hockeydata.logger.logging_config import logger


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
