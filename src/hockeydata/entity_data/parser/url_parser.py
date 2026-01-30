from abc import abstractmethod
from scrapy import Selector


import common_functions as cf


from hockeydata.entity_data.parser.base import Parser
from hockeydata.logger.logging_config import logger


class URLParser(Parser):


    @property
    @classmethod
    @abstractmethod
    def URL_XPATH(cls) -> str:
        pass


    def __init__(self, scraped_data: bytes):
        self.scraped_data = scraped_data
        self.parsed_data: dict[str, int|list[str]|str] = {
            "league_uid": self.scraped_data["league_uid"],
            "scrape_id": self.scraped_data["scrape_id"],
            "season": self.scraped_data["season"],
            "urls": []
        }


    def get_data(self) -> dict:
        """Arguments: years - list of years for which data is parsed"""
        sel = Selector(text=self.scraped_data["html"])
        self.parsed_data["urls"] = cf.get_list_xpath_values(
                sel=sel,
                xpath=self.URL_XPATH
        )

        return self.parsed_data
    

class PlayerURLParser(URLParser):


    URL_XPATH = "//td[@class='player']/span/a/@href"


class TeamURLParser(URLParser):


    URL_XPATH = "//a[contains(@href, 'team')]/@href"