from abc import abstractmethod
from scrapy import Selector


import common_functions as cf


from entity_data.parser.url_parser import PlayerURLScraper
from hockeydata.logger.logging_config import logger


class URLParser():


    @property
    @classmethod
    @abstractmethod
    def URL_XPATH(cls) -> str:
        pass


    def __init__(self, scraped_data: bytes):
        self.scraped_data = scraped_data


    def get_info_all(self) -> dict:
        """Arguments: years - list of years for which data is parsed"""
        sel = Selector(text=self.scraped_data)
        parsed_data = cf.get_list_xpath_values(
                sel=sel,
                xpath=self.URL_XPATH
        )

        return parsed_data
    

class PlayerURLParser(URLParser):


    URL_XPATH = "//td[@class='player']/span/a/@href"


class TeamURLParser(URLParser):


    URL_XPATH = "//a[contains(@href, 'team')]/@href"