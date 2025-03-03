from sqlalchemy import Column, Table
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Session, Query

from logger.logging_config import logger
from database_queries.query_dict import QUERIES_INFO


class DbDataGetter():
    
    
    def __init__(self, session: Session):
        self.session = session


    def get_db_query_result(
            self, query_name: str, filters: list=None, distinct=False) -> list:

        query_info = QUERIES_INFO[query_name]
        query = self._get_db_query(base_table=query_info["base_table"],
                                 selected_cols=query_info["selected_cols"],
                                 joins=query_info["joins"],
                                 filters=query_info["filters"])
        if filters:
            for f in filters:
                query = query.filter(f)
        if distinct:
            query = query.distinct()
        self.log_query(query)

        return query.all()


    def _get_db_query(
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
    
    def get_list_filter(table_column: Column, values: list):

        return filter(table_column.in_(values))
    

    def log_query(self, query):
        compiled_query = query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
        logger.debug("Executed SQL: %s", str(compiled_query))