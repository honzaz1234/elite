from sqlalchemy import Table
from sqlalchemy.orm import Session, Query

from logger.logging_config import logger
from database_queries.query_dict import QUERIES_INFO


class DbDataGetter():
    
    
    def __init__(self, session: Session):
        self.session = session


    def get_db_query_wraper(
            self, query_name: str, filters: list=None) -> list:

        query_info = QUERIES_INFO[query_name]
        query = self.get_db_query(base_table=query_info["base_table"],
                                 selected_cols=query_info["selected_cols"],
                                 joins=query_info["joins"],
                                 filters=query_info["filters"])
        if filters:
            for f in filters:
                query = query.filter(f)

        return query.all()


    def get_db_query(
            self,
            base_table: Table,
            selected_cols: list,
            joins: list[tuple[Table, object]]=None,
            filters: list[object]=None
        ) -> Query:
            query = self.session.query(*selected_cols).select_from(base_table)

            if joins:
                for join_table, condition in joins:
                    query = query.join(join_table, condition)

            if filters:
                for f in filters:
                    query = query.filter(f)

            return query