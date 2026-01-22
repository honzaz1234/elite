import math
import multiprocessing 

from abc import ABC, abstractmethod
from typing import Any, Generator

from management.scrape.unit_management import ScraperUnitManager
from management.scrape.unit_management import PlayerScraperUnitManager
from management.scrape.unit_management import PlayerURLScraperUnitManager
from hockeydata.logger.logging_config import logger


def player_scrape_worker(
        url_mapper: tuple[dict[int, str]]) -> list[Any]:
    manager = PlayerScraperUnitManager(
        url_mapper=url_mapper
    )
    manager.initiate_playwright_session()
    processed_data = manager.process()

    return processed_data


def player_url_scrape_worker(
        args: tuple[list[str], str]) -> list[Any]:
    seasons, league_uid = args
    manager = PlayerURLScraperUnitManager(
        seasons=seasons,
        league_uid=league_uid
    )
    manager.initiate_playwright_session()
    processed_data = manager.process()

    return processed_data


class MultiScrapeManager(ABC):


    @property
    @classmethod
    @abstractmethod
    def SCRAPER_MANAGER(cls) -> type[ScraperUnitManager]:
        pass


    @property
    @classmethod
    @abstractmethod
    def SCRAPER_WORKER(cls) -> function:
        pass


    @property
    @classmethod
    @abstractmethod
    def TYPE(cls) -> str:
        pass


    def __init__(
            self, data, max_workers: int=4):
        self.max_workers = max_workers
        self.data = data
        self.chunk_size = None
        self._set_chunk_size(data=data)


    @abstractmethod
    def set_up_manager(self) -> None:
        pass
    
    
    @abstractmethod
    def _set_chunk_size(self, data: list) -> None:
        self.chunk_size = math.ceil(len(data) / self.max_workers)
        logger.info(
            'Data will be divided between %s chunks of size %s', 
            self.max_workers,
            self.chunk_size
            )


    @abstractmethod
    def _chunk_uids(self) -> Generator:
        pass


    def scrape_data(self) -> list:
        mapper_chunks = list(self._chunk_uids())
        args = self._get_arguments(mapper_chunks=mapper_chunks)

        with multiprocessing.Pool(processes=self.max_workers) as pool:
            scraped_entities_nested = pool.map(self.SCRAPER_WORKER, args)
        scraped_entities = [
            entity for sublist in scraped_entities_nested 
            for entity in sublist
            ]

        return scraped_entities
    

    @abstractmethod
    def _get_arguments(self) -> list[tuple]:
        pass


class MultiPlayerScrapeManager(MultiScrapeManager):


    SCRAPER_MANAGER = PlayerScraperUnitManager
    SCRAPER_WORKER = player_scrape_worker
    

    def _chunk_uids(self) -> Generator[dict[str, int], None, None]:
        keys = list(self.data.keys())
        for i in range(0, len(keys), self.chunk_size):
            chunk_keys = keys[i:i + self.chunk_size]
            yield {k: self.data[k] for k in chunk_keys}


    def _get_arguments(
            self,
              mapper_chunks: list[list[dict[str, str]]]) -> tuple[dict[str, str]]:
        return  [
            (mapper_chunk)
            for mapper_chunk in mapper_chunks
            ]
    

class PlayerURLMultiScrapeManager(MultiScrapeManager):


    SCRAPER_MANAGER = PlayerURLScraperUnitManager
    SCRAPER_WORKER = player_url_scrape_worker


    def _chunk_uids(self) -> Generator[list[str], None, None]:
        for i in range(0, len(self.data["seasons"]), self.chunk_size):
            yield self.data["seasons"][i : i + self.chunk_size]


    def _get_arguments(
            self,
              mapper_chunks: list[list[str]]) -> tuple[list[str]]:
        return  [
            (mapper_chunk, self.data["league_uid"])
            for mapper_chunk in mapper_chunks
            ]
