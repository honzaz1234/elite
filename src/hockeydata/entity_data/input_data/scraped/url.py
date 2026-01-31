from abc import abstractmethod
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

import hockeydata.database_creator.storage_database_creator as db

from hockeydata.database_insert.db_insert import StorageDatabaseMethods, Query
from hockeydata.database_queries.database_query import StorageDBQuery
from hockeydata.entity_data.input_data.scraped.base import HTMLInputter
from hockeydata.logger.logging_config import logger


class PlayerURLHTMLInputter(HTMLInputter):


    def __init__(
            self, db_session: Session, 
            scraped_data: dict[str, dict[list[str]]|str]):
        super().__init__(
            db_session=db_session, 
            scraped_data=scraped_data["data"]
            )
        self.league_id = scraped_data["uid"]
        self.query_manager = StorageDBQuery(db_session=db_session)
        self.season_mapper: dict[str, int] = {}


    def _set_league_id(self) -> None:
        self.league_id = self.query._find_id_in_table(
            db.LeagueInfo, 
            uid=self.league_id
            )
        

    def _set_season_mapper(self) -> None:
        seasons = list(self.scraped_data.keys())
        filter_ = [db.Season.season.in_(seasons)]
        raw_data = self.query_manager.get_db_query_result(
            query_name="season_mapper",
            filters=filter_
            )
        for row in raw_data:
            self.season_mapper[row[0]] = row[1]


    def input_data(self) -> None:
        self._set_league_id()
        self._set_season_mapper()
        for season in self.scraped_data:
            self._input_season_player_urls(
                scraped_data=self.scraped_data[season],
                season=season
                )
        #maybe delete later?
        self.db_session.commit()


    def _input_season_player_urls(
            self, scraped_data: dict[str, list], season: str) -> None:
        season_id = self.season_mapper[season]
        self.input_type_urls(
            type_inputter_cls=GoalieURLHTMLInputter, type_scraped_data=scraped_data["goalies"],
            season_id=season_id
            )
        self.input_type_urls(
            type_inputter_cls=SkaterURLHTMLInputter, type_scraped_data=scraped_data["skaters"],
            season_id=season_id
            )
    

    def input_type_urls(
            self, type_inputter_cls: type['PlayerTypeURLHTMLInputter'], type_scraped_data: list[str], season_id: int) -> None:
        type_inputter = type_inputter_cls(
            scrape_id=self.scrape_id,
            season_id=season_id,
            league_id=self.league_id,
            db_session=self.db_session
        )
        type_inputter.input_data(scraped_data=type_scraped_data)


class PlayerTypeURLHTMLInputter():


    @property
    @classmethod
    @abstractmethod
    def IS_GOALIE(cls) -> bool:
        pass


    def __init__(
            self, scrape_id: int,  season_id: int, league_id: int, db_session: Session):
        self.scrape_id = scrape_id
        self.season_id = season_id
        self.league_id = league_id
        self.insert_db = StorageDatabaseMethods(db_session=db_session)


    def input_data(self, scraped_data: list) -> None:
        insert_list = []
        for url_html in scraped_data:
            row_dict = self.get_row_dict(url_html=url_html)
            insert_list.append(row_dict)
        self.insert_db.insert_bulk(table=db.PlayerURLHTML, data=insert_list)


    def get_row_dict(self, url_html: bytes) -> dict[str, bool|int|str]:
        return {
                "scrape_id": self.scrape_id,
                "is_goalie": self.IS_GOALIE,
                "league_id": self.league_id,
                "season_id": self.season_id,
                "html_data": url_html
                }
    

class SkaterURLHTMLInputter(PlayerTypeURLHTMLInputter):


    IS_GOALIE = False


class GoalieURLHTMLInputter(PlayerTypeURLHTMLInputter):


    IS_GOALIE = True


class URLInputter():


    @property
    @classmethod
    @abstractmethod
    def URL_TABLE(cls) -> Table:
        pass

    @property
    @classmethod
    @abstractmethod
    def URL_TYPE(cls) -> str:
        pass


    def __init__(self, db_session: Session, 
                 parsed_data: list[dict[str, int|list|str]]):
        self.db_session = db_session
        self.insert_db = StorageDatabaseMethods(db_session=db_session)
        self.query = Query(db_session=db_session) 
        self.parsed_data = parsed_data


    def input_data(self) -> None:
        for chunk in self.parsed_data:
            self._input_page(chunk=chunk)


    def _input_page(self, chunk: dict[str, int|list|str]) -> None:
        insert_list = []
        for url in chunk["urls"]:
            url_entry = self._create_input_dict(url=url, chunk=chunk)
            insert_list.append(url_entry)
        self.insert_db.insert_update_or_ignore_on_conflict_bulk(
            table=self.URL_TABLE, 
            data=insert_list,
            update=True
            )


    def _create_input_dict(
            self, url: str, chunk: dict[str, int|list|str]
            ) -> dict[str, int|str]:
        
        return {
            "url": url,
            "league_id": chunk["league_id"],
            "season_id": chunk["season_id"],
            "scrape_id": chunk["scrape_id"],
            "is_goalie": chunk["is_goalie"]
        }
    

    def input_parse_log(self, start_time: datetime, 
                         end_time: datetime) -> None:
        url_type_id = self.query._find_id_in_table(
            table=db.URLType, 
            url_type=self.URL_TYPE
            )
        self.insert_db._input_data(
            table=db.URLLog, 
            start_datetime=start_time,
            end_datetime=end_time,
            url_type_id=url_type_id
            )
        #maybe delete later?
        self.db_session.commit()


class PlayerURLInputter(URLInputter):


    URL_TABLE = db.PlayerURL
    URL_TYPE = "player"