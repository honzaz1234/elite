from abc import ABC, abstractmethod


class Parser(ABC):


    def __init__(self, scraped_data):
        self.scraped_data = scraped_data


    @abstractmethod
    def get_data(self):
        pass