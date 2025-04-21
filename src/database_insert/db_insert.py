from constants import *
from logger.logging_config import logger

from sqlalchemy import update
from sqlalchemy.orm import Session


class DatabaseMethods():

    """class containg operations for dealing with the data in the database"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.query = Query(self.db_session)
        pass

    def _input_data(self, table, **kwargs) -> int:
        """method for adding a row to a table
           Parameters: table - to which table should data be inputted
                       **kwargs - column value pairs to be inputted
        """

        query_insert = self.query._create_table_entry(table=table, 
                                                        **kwargs)
        self.db_session.add(query_insert)
        self.db_session.commit()
        id = query_insert.id
        logger.debug(f"Index of the new data inserted in table"
                     f" {table.__tablename__} with query {query_insert}"
                     f" is {id}")
        return id
    

    def _input_unique_data_NA_excluded(
            self, table, non_condition, **kwargs) -> int:
        if non_condition == None:
            return None
        id = self._input_unique_data(table=table, **kwargs)
        return id
    
        
    def _input_unique_data(self, table, **kwargs) -> int:
        """inputs data into database when it is not there already 
            and returns the id of entry
            Parameters: table - to which table should data be inputted
                       **kwargs - column value pairs to be inputted
        """

        id = self.query._find_id_in_table(table=table, **kwargs)
        if id is None:
            logger.debug(f"Data is not in db in table {table.__tablename__}"
                         f" yet, data insert will follow")
            id = self._input_data(table=table, **kwargs)
        else:
            logger.debug(f"Data is already in db in table"
                         f" {table.__tablename__} at index {id}")
        return id
    

    def _update_data(self, table, where_col, where_val, **kwargs):
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
        self.db_session.commit()
        logger.debug(f"Update query for table {table.__tablename__}" 
                     f" {update_query}  commited")
        

    def _input_uid(self, table, uid_val, **kwargs) -> int:
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
            logger.debug(f"UID {uid_val} not found in table"
                         f" {table.__tablename__}, added at index {id}")
        else:
            logger.debug(f"UID {uid_val} already found in table"
                         f" {table.__tablename__}, at index {id}")
        return id
        

class Query():

    """class containing basic operations for the database"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        
    def _create_table_entry(self, table, **kwargs):
        """method for creating new row in selected table
        parameters:    table - to which table should data be inputted
                       **kwargs - column value pairs which should be inserted
        """

        entry = table(**kwargs)
        return entry
    

    def _find_id_in_table(self, table, **kwargs) -> int:
        """method for finding id of row in a table based on arbitrary column value pairs from the table
        parameters:  table - from which table id should be extracted
                     **kwargs - column value pairs by which row should be found
        """

        row_data = self.db_session.query(table.id).filter_by(**kwargs).first()
        if row_data is None:
            return None
        else: 
            return row_data.id
        

    def _update_entry(self, table, where_col, where_val, **kwargs):
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