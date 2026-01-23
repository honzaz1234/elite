import math
import multiprocessing

from abc import ABC, abstractmethod
from playwright.sync_api import Browser
from typing import Any, Callable, Generator

from hockeydata.entity_data.playwright_setup.playwright_setup import PlaywrightSetUp
from hockeydata.management.scrape.unit_management import PlayerScraperUnitManager
from hockeydata.management.scrape.unit_management import PlayerURLScraperUnitManager
from hockeydata.logger.logging_config import logger


def player_scrape_worker(
        args: tuple[dict[str, str]]) -> list[Any]:
    url_mapper = args
    playwright = PlaywrightSetUp()
    manager = PlayerScraperUnitManager(
        url_mapper=url_mapper,
        page=playwright.page
    )
    scraped_data = manager.scrape_data()

    return scraped_data


def player_url_scrape_worker(
        args: tuple[list[str], str]) -> list[Any]:
    seasons, league_uid = args
    playwright = PlaywrightSetUp()
    manager = PlayerURLScraperUnitManager(
        seasons=seasons,
        league_uid=league_uid,
        page=playwright.page
    )
    scraped_data = manager.scrape_data()
    playwright.close()

    return scraped_data


class MultiScrapeManager(ABC):


    SCRAPER_WORKER: Callable


    def __init__(
            self, data, max_workers: int=4):
        self.max_workers = max_workers
        self.data = data
        self.chunk_size = None
        self._set_chunk_size()
    

    @abstractmethod
    def _set_chunk_size(self) -> None:
        pass


    @abstractmethod
    def _chunk_uids(self) -> Generator:
        pass


    def scrape_data(self) -> list:
        chunks = list(self._chunk_uids())
        args = self._get_arguments(chunks=chunks)
        with multiprocessing.Pool(processes=self.max_workers) as pool:
            scraped_entities_nested = pool.map(type(self).SCRAPER_WORKER, args)
        scraped_entities = [
            entity for sublist in scraped_entities_nested 
            for entity in sublist
            ]

        return scraped_entities
    

    @abstractmethod
    def _get_arguments(self) -> list[tuple]:
        pass


class MultiPlayerScrapeManager(MultiScrapeManager):


    SCRAPER_WORKER = player_scrape_worker
    

    def _set_chunk_size(self, data: list) -> None:
        self.chunk_size = math.ceil(len(data) / self.max_workers)
        logger.info(
            'Data will be divided between %s chunks of size %s', 
            self.max_workers,
            self.chunk_size
            )
    

    def _chunk_uids(self) -> Generator[dict[str, int], None, None]:
        keys = list(self.data.keys())
        for i in range(0, len(keys), self.chunk_size):
            chunk_keys = keys[i:i + self.chunk_size]
            yield {k: self.data[k] for k in chunk_keys}


    def _get_arguments(
            self,
              chunks: list[list[dict[str, str]]]) -> tuple[dict[str, str]]:
        args = []
        for chunk in chunks:
            tuple_ = (chunk,)
            args.append(tuple_)

        return args
    

class PlayerURLMultiScrapeManager(MultiScrapeManager):


    SCRAPER_WORKER = player_url_scrape_worker


    def _set_chunk_size(self) -> None:
        self.chunk_size = (
            math.ceil(len(self.data["seasons"]) / self.max_workers)
            )
        logger.info(
            'Data will be divided between %s chunks of size %s', 
            self.max_workers,
            self.chunk_size
            )
        

    def _chunk_uids(self) -> Generator[list[str], None, None]:
        for i in range(0, len(self.data["seasons"]), self.chunk_size):
            yield self.data["seasons"][i : i + self.chunk_size]


    def _get_arguments(
            self,
              chunks: list[list[str]]) -> tuple[dict[str, str]]:
        args = []
        for chunk in chunks:
            tuple_ = (chunk, self.data["league_uid"])
            args.append(tuple_)

        return args