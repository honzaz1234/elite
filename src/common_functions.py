import requests
import scrapy

from decorators import repeat_request_until_success
from logger.logger import logger


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
        raise ValueError
    except ValueError:
        raise ValueError("Invalid season format. Expected 'yyyy-yy'"
                         " or 'yyyy-yyyy'.")

def convert_to_seconds(time_str):
    """converts TOI from format mintues::seconds to just seconds"""
    
    minutes, seconds = map(int, time_str.split(":"))
    return minutes * 60 + seconds


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
            logger.error("Error: play_type is None – XPath extraction"
                            " failed.")
            raise ValueError("play_type is None – unable to extract play"
                                " type from XPath.")
    
    return return_val


def get_list_xpath_values(
        sel: scrapy.Selector, xpath: str, optional: bool) -> list:
    return_vals = sel.xpath(xpath).getall()
    if return_vals == []:
        if optional:
            logger.debug(f"Value for Xpath: {xpath} is []")
        else:
            logger.error(f"Extracted value from XPath ({xpath}) is []"
                        f".Extraction failed")
            raise ValueError(f"Extracted value from XPath ({xpath}) is []."
                             f".Extraction failed")
    
    return return_vals

