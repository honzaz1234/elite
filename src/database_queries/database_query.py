import importlib
import json

from sqlalchemy import Column, Table
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Session, Query

from logger.logging_config import logger
from database_queries.query_dict import QUERIES_INFO
from database_queries.string_db_mapper import MODEL_MAP


class DbDataGetter():
    
    
    def __init__(self, db_session: Session):
        self.db_session = db_session


    def get_db_query_result(
            self, query_name: str, filters: list=None, distinct=False,
              query_file_path: str=None) -> list:
        if query_file_path is None:
            query_info = QUERIES_INFO[query_name]
        else:
            query_info = self._get_query_info_from_file(
                file_path=query_file_path, query_name=query_name
                )
        for type_ in ["joins", "filters"]:
            if type_ not in query_info:
                query_info[type_] = None
        query = self._get_db_query(base_table=query_info["base_table"],
                                 selected_cols=query_info["selected_cols"],
                                 joins=query_info["joins"],
                                 filters=query_info["filters"])
        if filters:
            for f in filters:
                query = query.filter(f)
        if distinct:
            query = query.distinct()
        self._log_query(query)

        return query.all()


    def _get_db_query(
            self,
            base_table: Table,
            selected_cols: list,
            joins: list[tuple[Table, object]]=None,
            filters: list[object]=None
        ) -> Query:
            query = self.db_session.query(*selected_cols).select_from(base_table)

            if joins:
                for join in joins:
                    query = self._create_join(
                        query=query, join=join
                        )

            if filters:
                for f in filters:
                    query = query.filter(f)

            return query
    
    
    def _create_join(self, query: Query, join: dict):
        if join["type"] == "inner":
        
            return query.join(join["table"], join["conn"])
        
        elif join["type"] == "left":
        
            return query.outerjoin(join["table"], join["conn"])

    
    def _get_list_filter(self, table_column: Column, values: list):

        return table_column.in_(values)
    

    def _get_query_info_from_file(
            self, file_path: str, query_name: str) -> dict:
        with open(file_path, "r") as f:
            query_file = json.load(f)
        query_info = query_file[query_name]
        query_info = self._resolve_mapper(query_info=query_info)
        
        return query_info
    

    def _resolve_mapper(self, query_info: str) -> dict:
        query_info["base_table"] = MODEL_MAP[query_info["base_table"]]

        query_info["selected_cols"] = [
            eval(col, MODEL_MAP) for col in query_info["selected_cols"]
            ]

        if "joins" in query_info:
            query_info["joins"] = [
                {
                    "table": MODEL_MAP[j["table"]], 
                    "conn": eval(j["conn"], MODEL_MAP),
                    "type": j["type"]
                } 
                for j in query_info["joins"]
            ]

        if "filters" in query_info:
            query_info["filters"] = [
                eval(f, MODEL_MAP) for f in query_info["filters"]
                ]
            
        return query_info
    
    
    def _log_query(self, query):
        compiled_query = query.statement.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
        logger.debug("Executed SQL: %s", str(compiled_query))