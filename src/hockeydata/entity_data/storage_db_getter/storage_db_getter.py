from abc import ABC, abstractmethod
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import Session
from typing import Optional


import hockeydata.database_creator.storage_database_creator as storage_db


from hockeydata.database_queries.database_query import StorageDBQuery


class EntityDataGetter(ABC):


    @property
    @classmethod
    @abstractmethod
    def TABLE_COLUMN(cls) -> InstrumentedAttribute:
        pass

    @property
    @classmethod
    @abstractmethod
    def DB_QUERY(cls) -> str:
        pass


    def __init__(self, db_query: StorageDBQuery, filters: list, data: dict, 
                 scrape_ids: list, uids: list):
            self.db_query = db_query
            self.filters = filters
            self.data = data
            self.filters = [
                db_query._get_list_filter(
                    table_column=storage_db.Scrape.id, 
                    values=scrape_ids
                    ),
                db_query._get_list_filter(
                    table_column=self.TABLE_COLUMN,
                    values=uids
                    )
            ]


    def get_data(self) -> None:
        raw_data = self.db_query.get_db_query_result(
            query_name=self.DB_QUERY,
            filters=self.filters
            )
        for row in raw_data:
            self._save_info(row=row)


    @abstractmethod
    def _save_info(self, row: tuple) -> None:
        pass


class PlayerDataGetter(EntityDataGetter):


    TABLE_COLUMN = storage_db.PlayerLog.player_uid


class BaseDataGetter(PlayerDataGetter):


    DB_QUERY = "player_base_info"


    def _save_info(self, row: tuple) -> None:
        player_uid, is_goalie, player_url = row
        self.data[player_uid] = {}
        self.data[player_uid]["is_goalie"] = is_goalie
        self.data[player_uid]["player_url"] = player_url


class PlayerFactsGetter(PlayerDataGetter):


    DB_QUERY = "player_facts"


    def _save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["player_facts"] = html_data


class AchievementsGetter(PlayerDataGetter):


    DB_QUERY = "achievements"


    def _save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["achievements"] = html_data


class SkaterStatsGetter(PlayerDataGetter):


    DB_QUERY = "skater_stats"


    def _save_info(self, row: tuple) -> None:
        player_uid, league_type, html_data = row
        self.data[player_uid]['stats'][league_type] = html_data


class GoalieStatsGetter(PlayerDataGetter):


    DB_QUERY = "goalie_stats"


    def _save_info(self, row: tuple) -> None:
        player_uid, competition_type, season_type, html_data = row
        self.data[player_uid]['stats'][competition_type][season_type] = html_data


class StorageDBDataGetter(ABC):


    def __init__(self, db_session: Session, scrape_ids: list, uids: list):
        self.db_query = StorageDBQuery(db_session=db_session)
        self.data: Optional[object] = None
        self.scrape_ids = scrape_ids
        self.uids = uids


class PlayerStorageDBDataGetter(StorageDBDataGetter):


    @property
    @classmethod
    @abstractmethod
    def STATS_GETTER(cls) -> type[SkaterStatsGetter|GoalieStatsGetter]:
        pass


    def get_data(self) -> dict:
        facts_getter = PlayerFactsGetter(
            db_query=self.db_query, 
            data=self.data, 
            scrape_ids=self.scrape_ids, 
            player_uids=self.uids
            )
        facts_getter.get_data()
        achievements_getter = AchievementsGetter(
            db_query=self.db_query, 
            data=self.data, 
            scrape_ids=self.scrape_ids, 
            player_uids=self.uids
            )
        achievements_getter.get_data()
        stats_getter = self.STATS_GETTER(
                    db_query=self.db_query, 
                    data=self.data, 
                    scrape_ids=self.scrape_ids, 
                    player_uids=self.uids
                )
        stats_getter.get_data()

        return self.data
    

class SkaterStorageDBDataGetter(PlayerStorageDBDataGetter):


        STATS_GETTER = SkaterStatsGetter

        def __init__(
            self, db_session: Session, scrape_ids: list, uids: list):
            super().__init__(
                db_session=db_session, 
                scrape_ids=scrape_ids, 
                uids=uids
                )
            self.data = {
                uid: {
                    "player_facts": {},
                    "achievements": {},
                    "stats": {
                        "league": {},
                        "tournament": {}
                    }
                }
                for uid in uids
            }


class GoalieStorageDBDataGetter(PlayerStorageDBDataGetter):


        STATS_GETTER = GoalieStatsGetter


        def __init__(
            self, db_session: Session, scrape_ids: list, uids: list):
            super().__init__(
                db_session=db_session, 
                scrape_ids=scrape_ids, 
                uids=uids
                )
            self.data = {
                uid: {
                    "player_facts": {},
                    "achievements": {},
                    "stats": {
                        "league": {
                            "regular": {},
                            "playoff": {}
                        },
                        "tournament": {
                            "regular": {},
                            "playoff": {}
                        }
                    }
                }
                for uid in uids
            }







        



