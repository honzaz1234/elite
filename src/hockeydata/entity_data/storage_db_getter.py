import database_creator.storage_database_creator as storage_db
from database_queries.database_query import DbDataGetter

from sqlalchemy.orm import Session


class StorageDBGetter():



    def __init__(
            self, db_session: Session, scrape_ids: list, player_uids: list, is_goalie: bool):
        self.db_query = DbDataGetter(db_session=db_session)
        self.data = {}
        self.facts_getter = PlayerFactsGetter(
            db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )
        self.achievements_getter = AchievementsGetter(
            db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )
        if is_goalie:
            self.stats_getter = GoalieStatsGetter(
                db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )
        else:
            self.stats_getter = PlayerStatsGetter(
                db_query=self.db_query, data=self.data, scrape_ids=scrape_ids, player_uids=player_uids
            )


    def get_data(self) -> dict:
        self.facts_getter.get_data()
        self.achievements_getter.get_data()
        self.stats_getter.get_data()

        return self.data


class DataGetter():


    DB_QUERY = ""


    def __init__(self, db_query: DbDataGetter, filters: list, data: dict):
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


    DB_QUERY = "storage_player_base_info"


    def __init__(self, db_query: DbDataGetter, data: dict):
        filters = [
                db_query.get_list_filter(
                    table_column=storage_db.Scrape.id, 
                    values=self.scrape_ids
                    )
            ]
        super().__init__(db_query=db_query, filters=filters, data=data) 


    def _save_info(self, row) -> None:
        player_uid, is_goalie, player_url = row
        self.data[player_uid] = {}
        self.data[player_uid]["is_goalie"] = is_goalie
        self.data[player_uid]["player_url"] = player_url


class HTMLDataGetter(DataGetter):


    DB_QUERY = "storage_player_facts"


    def __init__(
            self, db_query: DbDataGetter, data: dict, scrape_ids: list, player_uids: list):
        filters = [
                db_query.get_list_filter(
                    table_column=storage_db.Scrape.id, 
                    values=scrape_ids
                    ),
                db_query.get_list_filter(
                    table_column=storage_db.Player.player_uid,
                    values=player_uids
                    )
            ]
        super().__init__(db_query=db_query, filters=filters, data=data) 


class PlayerFactsGetter(HTMLDataGetter):


    DB_QUERY = "storage_player_facts"


    def _save_info(self, row) -> None:
        player_uid, html_data = row
        self.data[player_uid]["player_facts"] = html_data


class AchievementsGetter(HTMLDataGetter):


    DB_QUERY = "storage_achievements"


    def _save_info(self, row) -> None:
        player_uid, html_data = row
        self.data[player_uid]["achievements"] = html_data




        



