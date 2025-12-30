import playwright.sync_api as sp
import requests
import ssl
import time

from functools import wraps
from sqlalchemy.exc import SQLAlchemyError

from hockeydata.logger.logging_config import logger


MAX_ATTEMPT = 15


def repeat_request_until_success(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < MAX_ATTEMPT:
            try:
                result = func(*args, **kwargs)
                return result
            except AssertionError as e:
                logger.info("Attempt %s executing function  %s "
                            "failed: %s", attempt, {func.__name__}, e)
                time.sleep(10)
            except (ConnectionError, requests.Timeout, ssl.SSLError, OSError):
                logger.info("Attempt %s executing function %s "
                            "failed: %s", attempt, {func.__name__}, e)
                time.sleep(120)
            except(sp.TimeoutError):
                time.sleep(60)
        logger.info('Max attempt (%s) was reached', attempt)
        raise

    return wrapper 
                
                
def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time() 
        result = func(*args, **kwargs)  
        end_time = time.time() 
        execution_time = end_time - start_time  
        logger.info("Execution time of %s: %.6f seconds", 
                    func.__name__, execution_time)
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
            logger.error("Error in executing SQL code. Initiallizing DB "
                         "rollback")
            self.db_session.rollback()
            logger.info("Rollback initialized")
            raise e

    return wrapper
                 




