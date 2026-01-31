from abc import abstractmethod
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as storage_db

from hockeydata.database_get.storage_db.base import (StorageDBDataGetter, 
                                                     TableDataGetter)


class PlayerURLHTMLDataGetter(TableDataGetter):


    DB_QUERY = "player_url_html"


    def save_info(self, row: tuple) -> None:
        (
            html,
            season_id,
            league_id,
            scrape_id,
            is_goalie,
            league_uid,
            season,
        ) = row
        self.data.append(
             {
                  "html": html,
                  "season_id": season_id,
                  "league_id": league_id,
                  "scrape_id": scrape_id,
                  "is_goalie": is_goalie,
                  "league_uid": league_uid,
                  "season": season
             }
        ) 


class URLHTMLDBDataGetter(StorageDBDataGetter):


    ALLOWED_FILTERS = ["league_uid", "season"]
    
    
    @property
    @classmethod
    @abstractmethod
    def DATA_GETTER(cls) -> type[TableDataGetter]:
        pass


    def __init__(self, db_session: Session, filters: list):
        super().__init__(db_session=db_session, filters=filters)
        self.data = []


    def get_data(self) -> list[dict[str, bytes|int|str]]:

        table_getter = self.DATA_GETTER(
            db_query=self.db_query, 
            filters=self.filters, 
            data=self.data
            )
        table_getter.get_data()

        return self.data
    

class PlayerURLHTMLDBDataGetter(URLHTMLDBDataGetter):


    DATA_GETTER = PlayerURLHTMLDataGetter



