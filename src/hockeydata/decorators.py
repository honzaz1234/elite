import playwright.sync_api as sp
import requests
import ssl
import time


from . import logger


MAX_ATTEMPT = 15


def repeat_request_until_success(function):
    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < MAX_ATTEMPT:
            try:
                result = function(*args, **kwargs)
                return result
            except AssertionError as e:
                logger.info(f"Attempt {attempt} failed: {e}")
                time.sleep(10)
            except (ConnectionError, requests.Timeout, ssl.SSLError, OSError):
                logger.info(f"Attempt {attempt} failed: {e}")
                time.sleep(120)
            except(sp.TimeoutError):
                time.sleep(60)
            except:
                logger.info(f"Attempt {attempt} failed: {e}")
                attempt += 1
        logger.info('Max attempt was reached')
        raise
    return wrapper 
                

                 




