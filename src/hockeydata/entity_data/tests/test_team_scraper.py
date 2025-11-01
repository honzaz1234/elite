import entity_data.tests.test_class as test_class 
import unittest

from entity_data.scraper.team_scraper import *
from constants import *


data_loader = test_class.TestDataLoader()
pst_o = ps.PlaywrightSetUp()

#players urls
URL_MELNIK = "https://www.eliteprospects.com/team/3271/hc-junior-melnik"
URL_ZEMGALE = "https://www.eliteprospects.com/team/1392/zemgale"
URL_TORONTO = "https://www.eliteprospects.com/team/8178/toronto-marlboros-u16-aaa"
URL_PRAHA = "https://www.eliteprospects.com/team/162/hc-slavia-praha"


TEAM_NAMES = ["melnik", "zemgale", "toronto", "praha"] 
PATH_TEST_FILES = "./src/hockeydata/tests/test_data/scraper/team_scraper/"

#json file names
json_name_list = data_loader.get_names_with_formats(TEAM_NAMES, "json")

#json files 
json_file_list = data_loader.load_data("json",
                                        PATH_TEST_FILES,
                                        json_name_list,
                                        TEAM_NAMES)


class TestTeamScraper(unittest.TestCase):


    def test_get_info_melnik(self):
        playerscraper = TeamScraper(url=URL_MELNIK, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["melnik"])

    def test_get_info_zemgale(self):
        playerscraper = TeamScraper(url=URL_ZEMGALE, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["zemgale"])

    def test_get_info_toronto(self):
        playerscraper = TeamScraper(url=URL_TORONTO, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["toronto"])

    def test_get_info_praha(self):
        playerscraper = TeamScraper(url=URL_PRAHA, page=pst_o.page)
        dict_team = playerscraper.get_info()
        self.assertDictEqual(dict_team, json_file_list["praha"])


if __name__ == "__main__":
    unittest.main()
        


                








