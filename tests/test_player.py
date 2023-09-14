import unittest
from scraper.player import *
from elite.tests.test_data_player import *


class TestPlayerScraper(unittest.TestCase):

    def test_get_info_all(self):
        playerscraper = PlayerScraper(url=URL_ZOHORNA)
        dict_player = playerscraper.get_info_all()
        self.assertEqual(dict_player, DICT_URL_ZOHORNA)

class TestPlayerGeneralInfo(unittest.TestCase):
    playergeninfo = PlayerGeneralInfo(selector=)

    def test_get_general_info(self):

        gi_dict = playergeninfo.

