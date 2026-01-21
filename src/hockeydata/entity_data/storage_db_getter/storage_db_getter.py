from abc import ABC, abstractmethod
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import Session


import hockeydata.database_creator.storage_database_creator as storage_db


from hockeydata.database_queries.database_query import StorageDBQuery


class DataGetter(ABC):


    @property
    @classmethod
    @abstractmethod
    def DB_QUERY(cls) -> str:
        pass


    def __init__(self, db_query: StorageDBQuery, scrape_ids: list):
            self.db_query = db_query
            self.filters = [
                storage_db.Scrape.id.in_(scrape_ids)
            ]


    def get_data(self) -> None:
        raw_data = self.db_query.get_db_query_result(
            query_name=self.DB_QUERY,
            filters=self.filters
            )
        for row in raw_data:
            self.save_info(row=row)
    

    @abstractmethod
    def save_info(self, row: tuple) -> None:
        pass


class PlayerURLDataGetter(DataGetter):


    DB_QUERY = "player_url_html"


    def __init__(
              self, db_query: StorageDBQuery, scrape_ids: list, 
              season_list: list = None, league_uids: list = None):
            super().__init__(
                db_query=db_query, 
                scrape_ids=scrape_ids
                )
            self.data: list[str] = []

            if league_uids:
                uid_filter = storage_db.LeagueInfo.uid.in_(league_uids)
                self.filters.append(uid_filter)
            if season_list:
                uid_filter = storage_db.Season.season.in_(league_uids)
                self.filters.append(uid_filter)


    def save_info(self, row: tuple) -> None:
        html, season, league_uid, scrape_id = row
        self.data.append(
             {
                  "html": html,
                  "season": season,
                  "league_uid": league_uid,
                  "scrape_id": scrape_id
             }
        ) 


class EntityDataGetter(DataGetter):


    @property
    @classmethod
    @abstractmethod
    def TABLE_COLUMN(cls) -> InstrumentedAttribute:
        pass


    def __init__(self, db_query: StorageDBQuery, data: dict, 
                 scrape_ids: list, uids: list|None = None):
            super().__init__(
                db_query=db_query, 
                scrape_ids=scrape_ids
                )
            self.data = data
            if uids is not None:
                uid_filter = self.TABLE_COLUMN.in_(uids)
                self.filters.append(uid_filter)


class PlayerDataGetter(EntityDataGetter):


    TABLE_COLUMN = storage_db.PlayerLog.uid


    def __init__(self, db_query: StorageDBQuery, data: dict, 
                scrape_ids: list, uids: list, is_goalie: str):
        super().__init__(
            db_query=db_query, 
            data=data, 
            scrape_ids=scrape_ids, 
            uids=uids
            )
        is_goalie_filter = storage_db.PlayerLog.is_goalie.is_(is_goalie)
        self.filters.append(is_goalie_filter)


class BaseDataGetter(PlayerDataGetter):


    DB_QUERY = "player_base_info"


    def save_info(self, row: tuple) -> None:
        player_uid, is_goalie, player_url, scrape_id = row
        self.data[player_uid] = {}
        self.data[player_uid]["is_goalie"] = is_goalie
        self.data[player_uid]["player_url"] = player_url
        self.data[player_uid]["scrape_id"] = scrape_id


class PlayerFactsGetter(PlayerDataGetter):


    DB_QUERY = "player_facts"


    def save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["player_facts"] = html_data


class AchievementsGetter(PlayerDataGetter):


    DB_QUERY = "achievements"


    def save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["achievements"] = html_data


class SkaterStatsGetter(PlayerDataGetter):


    DB_QUERY = "skater_stats"


    def save_info(self, row: tuple) -> None:
        player_uid, league_type, html_data = row
        self.data[player_uid]['stats'][league_type] = html_data


class GoalieStatsGetter(PlayerDataGetter):


    DB_QUERY = "goalie_stats"


    def save_info(self, row: tuple) -> None:
        player_uid, competition_type, season_type, html_data = row
        self.data[player_uid]['stats'][competition_type][season_type] = html_data


class StorageDBDataGetter(ABC):


    def __init__(self, db_session: Session, scrape_ids: list, uids: list):
        self.db_query = StorageDBQuery(db_session=db_session)
        self.data: dict|None = None
        self.scrape_ids = scrape_ids
        self.uids = uids


    @abstractmethod
    def get_data(self) -> dict:
        pass


class PlayerStorageDBDataGetter(StorageDBDataGetter):


    @property
    @classmethod
    @abstractmethod
    def IS_GOALIE(cls) -> bool:
        pass

    @property
    @classmethod
    @abstractmethod
    def STATS_GETTER(cls) -> type[SkaterStatsGetter|GoalieStatsGetter]:
        pass


    def get_data(self) -> dict:
        base_getter = BaseDataGetter(
            db_query=self.db_query, 
            data=self.data, 
            scrape_ids=self.scrape_ids, 
            uids=self.uids,
            is_goalie = self.IS_GOALIE
            )
        base_getter.get_data()
        facts_getter = PlayerFactsGetter(
            db_query=self.db_query, 
            data=self.data, 
            scrape_ids=self.scrape_ids, 
            uids=self.uids,
            is_goalie = self.IS_GOALIE
            )
        facts_getter.get_data()
        achievements_getter = AchievementsGetter(
            db_query=self.db_query, 
            data=self.data, 
            scrape_ids=self.scrape_ids, 
            uids=self.uids,
            is_goalie = self.IS_GOALIE
            )
        achievements_getter.get_data()
        stats_getter = self.STATS_GETTER(
                    db_query=self.db_query, 
                    data=self.data, 
                    scrape_ids=self.scrape_ids, 
                    uids=self.uids,
                    is_goalie = self.IS_GOALIE
                )
        stats_getter.get_data()

        return self.data
    

class SkaterStorageDBDataGetter(PlayerStorageDBDataGetter):


        IS_GOALIE = False
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


        IS_GOALIE = True
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