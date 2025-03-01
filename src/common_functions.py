import common_functions

import requests
import scrapy

from errors import EmptyReturnXpathValueError
from decorators import repeat_request_until_success
from logger.logging_config import logger


def convert_season_format(season):
    """
    Converts a season string from 'yyyy-yy' to 'yyyy-yyyy' or returns it unchanged 
    """
    try:
        if (len(season) == 9 
            and season[4] == '-' 
            and season[:4].isdigit() 
            and season[5:].isdigit()):
            return season  # Return unchanged

        # If in 'yyyy-yy' format, convert to 'yyyy-yyyy'
        if (len(season) == 7 
            and season[4] == '-' 
            and season[:4].isdigit() 
            and season[5:].isdigit()):
            start_year, end_suffix = season.split('-')
            start_year = int(start_year)
            end_year = int(f"{start_year // 100}{end_suffix}")
            return f"{start_year}-{end_year}"
    except ValueError:
        error_message = (
           "Invalid season format. Expected 'yyyy-yy'"
            " or 'yyyy-yyyy'." 
        )
        common_functions.log_and_raise(error_message)


@repeat_request_until_success
def get_valid_request(url: str, return_type: str, params: dict=None, 
    headers: dict=None) -> requests.Response:
    response = requests.get(url, params=params, headers=headers)
    assert response.status_code == 200
    if return_type=="json":

        return response.json()
    elif return_type=="content":

        return response.content
    

def get_single_xpath_value(
        sel: scrapy.Selector, xpath: str, optional: bool) -> str|int:

    return_val = sel.xpath(xpath).get()
    if return_val is None:
        if optional:
            logger.debug(f"Value for xpath: {xpath} is {None}")
        else:
            error_message = (
                f"Error: play_type is None – XPath ({xpath}) extraction"
                f" failed."
            )
            log_and_raise(
                error_message, EmptyReturnXpathValueError,
                    xpath=xpath, value=None)
    
    return return_val


def get_list_xpath_values(
        sel: scrapy.Selector, xpath: str, optional: bool) -> list:
    return_vals = sel.xpath(xpath).getall()
    if return_vals == []:
        if optional:
            logger.debug(f"Value for Xpath: {xpath} is []")
        else:
            error_message =  (
                f"Extracted value from XPath ({xpath}) is []"
                f".Extraction failed"
                )
            log_and_raise(
                error_message, EmptyReturnXpathValueError,
                    xpath=xpath, value="[]")
    
    return return_vals


def convert_to_seconds(time_string: str) -> int:
    try:
        minutes, seconds = map(int, time_string.split(":"))
        
        return  minutes * 60 + seconds
    except ValueError as e: 
        error_message = (
            f"Invalid time format: '{time_string}'. Expected"      
            f" format: MM:SS"    
        )
        log_and_raise(error_message, ValueError)
    

def log_and_raise(
        error_message: str, exception_class: type[Exception], **kwargs) -> None:
    logger.error(error_message)
    try:
        raise exception_class(error_message, **kwargs)
    except TypeError:
        raise exception_class(**kwargs)
