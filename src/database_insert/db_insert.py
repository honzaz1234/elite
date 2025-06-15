from constants import *
from decorators import sql_executor
from database_insert import logger

from sqlalchemy import update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.schema import Table


class DatabaseMethods():

    """class containg operations for dealing with the data in the database"""


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.query = Query(self.db_session)
        pass


    def get_compulsory_table_id(self, table: Table, value, **kwargs) -> int:
        if value is not None:
            table_id =  self._input_unique_data(
                table=table, **kwargs)
        else:
            table_id = None

        return table_id


    @sql_executor
    def _input_data(self, table: Table, **kwargs) -> int:
        """method for adding a row to a table
           Parameters: table - to which table should data be inputted
                       **kwargs - column value pairs to be inputted
        """

        query_insert = self.query._create_table_entry(table=table, 
                                                        **kwargs)
        self.db_session.add(query_insert)
        self.db_session.flush()
        id = query_insert.id
        logger.debug(
            "Index of the new data inserted in table %s with query %s is %s",
            table.__tablename__, query_insert, id
            )
        return id
    

    @sql_executor
    def _input_unique_data_NA_excluded(
            self, table: Table, non_condition, **kwargs) -> int:
        if non_condition == None:
            return None
        id = self._input_unique_data(table=table, **kwargs)
        return id
    

    @sql_executor    
    def _input_unique_data(self, table: Table, **kwargs) -> int:
        """inputs data into database when it is not there already 
            and returns the id of entry
            Parameters: table - to which table should data be inputted
                       **kwargs - column value pairs to be inputted
        """

        id = self.query._find_id_in_table(table=table, **kwargs)
        if id is None:
            logger.debug(
                "Data is not in db in table %s yet, data insert will follow",
                table.__tablename__
                )
            id = self._input_data(table=table, **kwargs)
        else:
            logger.debug(
                "Data is already in db in table %s at index %s",
                table.__tablename__, id
                )
            
        return id
    

    @sql_executor
    def _update_data(self, table: Table, where_col, where_val, **kwargs):
        """ method for updating value of already existing  
            row in table
            Parameters: table - table in which the row is updated
            where_col - column based on which the row is selected
            where_val - value of where_col based on which the   
                        row is selected
            **kwargs - key value pairs, where keys are columns 
                        and values are new updated values
        """

        update_query = self.query._update_entry(
            table=table, where_col=where_col, where_val=where_val, **kwargs)
        self.db_session.execute(update_query)
        logger.debug(
            "Update query for table %s %s committed", 
                     table.__tablename__, update_query
                     )
        

    @sql_executor
    def _input_uid(self, table: Table, uid_val, **kwargs) -> int:
        """method for inputing uid in database
           Parameters: table - table in which uid is inputted
                       uid_val - inputted uid
                       **kwargs -uid=uid_val ad other column value pairs of the table, all of them need to be specified
        """
        if uid_val == None:
            return None
        id = self.query._find_id_in_table(table=table, uid=uid_val)
        if id is None:
            id = self._input_unique_data_NA_excluded(
                table=table, non_condition=uid_val, **kwargs)
            logger.debug(
                "UID %s not found in table %s, added at index %s", 
                uid_val, table.__tablename__, id
                )

        else:
            logger.debug(
                "UID %s already found in table %s, at index %s", 
                uid_val, table.__tablename__, id
                )

        return id
    

    def insert_update_or_ignore_on_conflict(
            self, table: Table, data: dict, update=False, 
            index_cols=[], return_id=False) -> int|None:
        insert_query = self._get_insert_query(table, data, update, index_cols)
        if return_id:
            insert_query = insert_query.returning(table.id)
        result = self.db_session.execute(insert_query)
        if return_id:
            row = result.fetchone()
            if row:
                return row[0]
            else:
                # If row was NOT inserted/updated (e.g. "do nothing"), fetch manually
                return self.query._find_id_in_table(
                    table, **{col: data[col] for col in index_cols}
                    )

        return None
    

    def insert_update_or_ignore_on_conflict_bulk(
            self, table: Table, data: list, update=False, 
            index_cols=[]) -> None:
        insert_query = self._get_insert_query(table, data, update, index_cols)
        self.db_session.execute(insert_query)

    
    def _get_insert_query(
            self, table: Table, data: list|dict, update: bool, 
            index_cols: list) -> Insert:
        insert_query = sqlite_insert(table).values(data)
        if update:
            update_cols = {
                col: insert_query.excluded[col] for col in data 
                if col not in index_cols
                }
            insert_query = insert_query.on_conflict_do_update(
                index_elements=index_cols,
                set_=update_cols
                )
        else:
            insert_query = insert_query.on_conflict_do_nothing(
                index_elements=index_cols
                )

        return insert_query


class Query():
    """class containing basic operations for the database"""


    def __init__(self, db_session: Session):
        self.db_session = db_session

        
    def _create_table_entry(self, table: Table, **kwargs):
        """method for creating new row in selected table
        parameters:    table - to which table should data be inputted
                       **kwargs - column value pairs which should be inserted
        """

        entry = table(**kwargs)

        return entry
    

    def _find_id_in_table(self, table: Table, **kwargs) -> int:
        """method for finding id of row in a table based on arbitrary column value pairs from the table
        parameters:  table - from which table id should be extracted
                     **kwargs - column value pairs by which row should be found
        """

        row_data = self.db_session.query(table.id).filter_by(**kwargs).first()
        if row_data is None:
            return None
        else: 
            return row_data.id
        

    def _update_entry(self, table: Table, where_col, where_val, **kwargs):
        """method for creating query for updating value of already existing  
           row in a table
           Parameters: table - table in which the row is updated
                       where_col - column based on which the row is selected
                       where_val - value of where_col based on which the   
                                   row is selected
                       **kwargs - key value pairs, where keys are columns 
                                  and values are new updated values
        """

        update_query = (update(table)
                       .where(where_col == where_val)
                       .values(**kwargs))
        return update_query
    

    def _get_value_from_table(self, cols: list, **kwargs):
        row_data = self.db_session.query(*cols).filter_by(**kwargs).first()

        return row_data

