import hockeydata.tests.test_class as test_class 
import unittest

from hockeydata.scraper.league_scraper import *
from hockeydata.constants import *


data_loader = test_class.TestDataLoader()
pst_o = ps.PlaywrightSetUp()

#players urls
URL_NHL = "https://www.eliteprospects.com/league/nhl"
URL_EXTRALIGA = "https://www.eliteprospects.com/league/czechia"
URL_LIIGA = "https://www.eliteprospects.com/league/liiga"

LEAGUE_NAMES = ["nhl", "extraliga", "liiga"] 
PATH_TEST_FILES = "./src/hockeydata/tests/test_data/scraper/league_scraper/"

#json file names
json_name_list = data_loader.get_names_with_formats(LEAGUE_NAMES, "json")

#json files 
json_file_list = data_loader.load_data("json",
                                        PATH_TEST_FILES,
                                        json_name_list,
                                        LEAGUE_NAMES)


class TestLeagueScraper(unittest.TestCase):


    def test_get_info_nhl(self):
        playerscraper = LeagueScrapper(url=URL_NHL, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["nhl"])

    def test_get_info_extraliga(self):
        playerscraper = LeagueScrapper(url=URL_EXTRALIGA, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["extraliga"])

    def test_get_info_liiga(self):
        playerscraper = LeagueScrapper(url=URL_LIIGA, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["liiga"])


if __name__ == "__main__":
    unittest.main()
        


                








