from abc import abstractmethod
from sqlalchemy.orm import Session

import hockeydata.database_creator.storage_database_creator as storage_db

from hockeydata.database_get.storage_db.base import (TableDataGetter,
                                                     StorageEntityDBDataGetter)


class BaseDataGetter(TableDataGetter):


    DB_QUERY = "player_base_info"


    def save_info(self, row: tuple) -> None:
        player_uid, is_goalie, player_url, scrape_id = row
        self.data[player_uid] = {}
        self.data[player_uid]["is_goalie"] = is_goalie
        self.data[player_uid]["player_url"] = player_url
        self.data[player_uid]["scrape_id"] = scrape_id


class PlayerFactsGetter(TableDataGetter):


    DB_QUERY = "player_facts"


    def save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["player_facts"] = html_data


class AchievementsGetter(TableDataGetter):


    DB_QUERY = "achievements"


    def save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["achievements"] = html_data


class SkaterStatsGetter(TableDataGetter):


    DB_QUERY = "skater_stats"


    def save_info(self, row: tuple) -> None:
        player_uid, league_type, html_data = row
        self.data[player_uid]['stats'][league_type] = html_data


class GoalieStatsGetter(TableDataGetter):


    DB_QUERY = "goalie_stats"


    def save_info(self, row: tuple) -> None:
        player_uid, competition_type, season_type, html_data = row
        self.data[player_uid]['stats'][competition_type][season_type] = html_data


class PlayerStorageDBDataGetter(StorageEntityDBDataGetter):
    

    RETURN_TEMPLATE = None
    UID_QUERY = "player_uids"


    def __init__(self, db_session: Session, filters: list):
        super().__init__(db_session=db_session, filters=filters)
        self.filters.append(storage_db.PlayerLog.is_goalie.is_(self.IS_GOALIE))


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
            filters=self.filters
            )
        base_getter.get_data()
        facts_getter = PlayerFactsGetter(
            db_query=self.db_query, 
            data=self.data, 
            filters=self.filters
            )
        facts_getter.get_data()
        achievements_getter = AchievementsGetter(
            db_query=self.db_query, 
            data=self.data, 
            filters=self.filters
            )
        achievements_getter.get_data()
        stats_getter = self.STATS_GETTER(
                    db_query=self.db_query, 
                    data=self.data, 
                    filters=self.filters
                )
        stats_getter.get_data()

        return self.data
    

class SkaterStorageDBDataGetter(PlayerStorageDBDataGetter):


        IS_GOALIE = False
        RETURN_TEMPLATE = {
                    "player_facts": {},
                    "achievements": {},
                    "stats": {
                        "league": {},
                        "tournament": {}
                        }
        }
        STATS_GETTER = SkaterStatsGetter


class GoalieStorageDBDataGetter(PlayerStorageDBDataGetter):


        IS_GOALIE = True
        RETURN_TEMPLATE =  {
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
        STATS_GETTER = GoalieStatsGetter