import math
import multiprocessing

from abc import ABC, abstractmethod
from typing import Callable, Generator

from hockeydata.management.parsing.unit_management import PlayerURLParserUnitManager
from hockeydata.logger.logging_config import logger


def player_url_parse_worker(
        args: tuple[list[dict[str, bytes|int|str]]]
        ) -> list[dict[str, int|list|str]]:
    pages = args
    manager = PlayerURLParserUnitManager(
        scraped_data=pages
    )
    parsed_data = manager.parse_data()

    return parsed_data


class MultiParseManager(ABC):


    SCRAPER_WORKER: Callable


    def __init__(
            self, scraped_data, max_workers: int=4):
        self.max_workers = max_workers
        self.scraped_data = scraped_data
        self.parsed_data = []
        self.chunk_size = None
        self._set_chunk_size()
    

    @abstractmethod
    def _set_chunk_size(self) -> None:
        pass


    @abstractmethod
    def _chunk_uids(self) -> Generator:
        pass


    def parse_data(self) -> dict[str, str|dict[str, dict[str, list[bytes]]]]:
        chunks = list(self._chunk_uids())
        args = self._get_arguments(chunks=chunks)
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            scraped_entities_nested = pool.map(type(self).SCRAPER_WORKER, args)
        for chunk in scraped_entities_nested:
            self.parsed_data.extend(chunk)

        return self.parsed_data
    

    @abstractmethod
    def _get_arguments(self) -> list[tuple]:
        pass
    

class PlayerURLMultiParseManager(MultiParseManager):


    SCRAPER_WORKER = player_url_parse_worker


    def _set_chunk_size(self) -> None:
        self.chunk_size = (
            math.ceil(len(self.scraped_data) / self.max_workers)
            )
        logger.info(
            'Data will be divided between %s chunks of size %s', 
            self.max_workers,
            self.chunk_size
            )
        

    def _chunk_uids(self) -> Generator[list[str], None, None]:
        for i in range(0, len(self.scraped_data), self.chunk_size):
            yield self.scraped_data[i : i + self.chunk_size]


    def _get_arguments(
            self,
              chunks: list[list[str]]) -> tuple[dict[str, str]]:
        args = []
        for chunk in chunks:
            tuple_ = (chunk)
            args.append(tuple_)

        return args