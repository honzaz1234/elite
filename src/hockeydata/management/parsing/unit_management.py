from abc import ABC, abstractmethod

import hockeydata.common_functions as cf

from hockeydata.constants import *
from hockeydata.database_creator.database_creator import *
from hockeydata.entity_data.parser.url_parser import PlayerURLParser, URLParser
from hockeydata.logger.logging_config import logger


class ParserUnitManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        pass


    def __init__(self, scrape_data: list):
        self.scrape_data = scrape_data


    @abstractmethod
    def parse_data(self) -> list[dict]:
        pass


class URLParserUnitManager(ParserUnitManager):


    @property
    @classmethod
    @abstractmethod
    def PARSE_CLASS(cls) -> type[URLParser]:
        pass


    def __init__(self, scraped_data: list[dict[str, bytes|int|str]]):
        super().__init__(scrape_data=scraped_data)
        self.parsed_data: list[dict[str, int|list|str]] = []


    def parse_data(self) -> list[dict[str, int|list|str]]:
        for page in self.scrape_data:
            try:
                parsed_data = self.parse_page_data(page=page)
                self.parsed_data.append(parsed_data)
            #add custom exception
            except Exception as e:
                error_message = (
                    "%s URL Parsing failed for league %s (%s): %s",
                    self.TYPE, 
                    page["league_uid"], 
                    page["season"],
                    e
                )
            #    self.db_session.bulk_insert_mappings(
            #        self.db_source.Season, self.scrape_log
            #        )
                cf.log_and_raise(error_message, Exception)
        
        return self.parsed_data
    

    def parse_page_data(
            self, page: dict[str, bytes|int|str]) -> dict[str, int|list|str]:
        parser = self.PARSE_CLASS(
            scraped_data=page
            )

        return parser.get_data()
    

class PlayerURLParserUnitManager(URLParserUnitManager):


    PARSE_CLASS = PlayerURLParser
    TYPE = "Player"