import playwright.sync_api as sp
import requests
import ssl
import time

from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

from logger.logging_config import logger


MAX_ATTEMPT = 15


def repeat_request_until_success(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < MAX_ATTEMPT:
            try:
                result = func(*args, **kwargs)
                return result
            except AssertionError as e:
                logger.info(f"Attempt {attempt} executing function "
                            f"{func.__name__} failed: {e}")
                time.sleep(10)
            except (ConnectionError, requests.Timeout, ssl.SSLError, OSError):
                logger.info(f"Attempt {attempt} executing function "
                            f"{func.__name__} failed: {e}")
                time.sleep(120)
            except(sp.TimeoutError):
                time.sleep(60)
        logger.info(f'Max attempt ({attempt}) was reached')
        raise

    return wrapper 
                
                
def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time() 
        result = func(*args, **kwargs)  
        end_time = time.time() 
        execution_time = end_time - start_time  
        logger.info(f"Execution time of {func.__name__}: " 
                    f"{execution_time:.6f} seconds")
        return result
      
    return wrapper


def sql_executor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            return result
        except SQLAlchemyError as e:
            print(f"args: {args}")
            print(f"kwargs: {kwargs}")
            logger.error(f"Error in executing SQL code. Initiallizing DB "
                         f"rollback")
            self.db_session.rollback()
            logger.info("Rollback initialized. DB session closed")
            raise e

    return wrapper
                 




