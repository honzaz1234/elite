import hockeydata.database_creator.storage_database_creator as storage_db
from hockeydata.database_queries.database_query import StorageDBQuery

from sqlalchemy.orm import Session


class StorageDBDataGetter():


    def __init__(
            self, db_session: Session, scrape_ids: list, player_uids: list, is_goalie: bool):
        
        self.db_query = StorageDBQuery(db_session=db_session)
        if is_goalie:
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
                for uid in player_uids
            }
            stats_getter = GoalieStatsGetter(
                db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )

        else:
            self.data = {
                uid: {
                    "player_facts": {},
                    "achievements": {},
                    "stats": {
                        "league": {},
                        "tournament": {}
                    }
                }
                for uid in player_uids
            }
            stats_getter = SkaterStatsGetter(
                    db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
                )

        self.facts_getter = PlayerFactsGetter(
            db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )
        self.achievements_getter = AchievementsGetter(
            db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )
        self.stats_getter = stats_getter


    def get_data(self) -> dict:
        self.facts_getter.get_data()
        self.achievements_getter.get_data()
        self.stats_getter.get_data()

        return self.data
        

class DataGetter():


    DB_QUERY = ""


    def __init__(self, db_query: StorageDBQuery, filters: list, data: dict):
            self.db_query = db_query
            self.filters = filters
            self.data = data


    def get_data(self) -> None:
        raw_data = self.db_query.get_db_query_result(
            query_name=self.DB_QUERY,
            filters=self.filters
            )
        for row in raw_data:
            self._save_info(row=row)
            

    def _save_info(self, row: tuple) -> None:
        pass



class BaseDataGetter(DataGetter):


    DB_QUERY = ""


    def __init__(self, db_query: StorageDBQuery, data: dict):
        filters = [
                db_query._get_list_filter(
                    table_column=storage_db.Scrape.id, 
                    values=self.scrape_ids
                    )
            ]
        super().__init__(db_query=db_query, filters=filters, data=data) 


    def _save_info(self, row: tuple) -> None:
        player_uid, is_goalie, player_url = row
        self.data[player_uid] = {}
        self.data[player_uid]["is_goalie"] = is_goalie
        self.data[player_uid]["player_url"] = player_url


class HTMLDataGetter(DataGetter):


    DB_QUERY = "player_facts"


    def __init__(
            self, db_query: StorageDBQuery, data: dict, scrape_ids: list, player_uids: list):
        filters = [
                db_query._get_list_filter(
                    table_column=storage_db.Scrape.id, 
                    values=scrape_ids
                    ),
                db_query._get_list_filter(
                    table_column=storage_db.PlayerLog.player_uid,
                    values=player_uids
                    )
            ]
        super().__init__(db_query=db_query, filters=filters, data=data) 


class PlayerFactsGetter(HTMLDataGetter):


    DB_QUERY = "player_facts"


    def _save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["player_facts"] = html_data


class AchievementsGetter(HTMLDataGetter):


    DB_QUERY = "achievements"


    def _save_info(self, row: tuple) -> None:
        player_uid, html_data = row
        self.data[player_uid]["achievements"] = html_data


class SkaterStatsGetter(HTMLDataGetter):


    DB_QUERY = "skater_stats"


    def _save_info(self, row: tuple) -> None:
        player_uid, league_type, html_data = row
        self.data[player_uid]['stats'][league_type] = html_data


class GoalieStatsGetter(HTMLDataGetter):


    DB_QUERY = "goalie_stats"


    def _save_info(self, row: tuple) -> None:
        player_uid, competition_type, season_type, html_data = row
        self.data[player_uid]['stats'][competition_type][season_type] = html_data







        



