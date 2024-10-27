import unittest
from hockeydata.scraper.player_scraper import *
from hockeydata.constants import *
import random
import scrapy
import json
from copy import deepcopy


def get_html_file(path_to_folder, file_name):

    path_file = path_to_folder + file_name
    with open(path_file, "r") as f:
        html_player = f.read()

    return html_player

def get_json_file(path_to_folder, file_name):

    path_file = path_to_folder + file_name
    f = open(path_file)
    dict_player = json.load(f)

    return dict_player


PATH = "./tests/scraper/player_scraper/"

FILE_JSON_HOWE = "howe.json"
FILE_JSON_MCDAVID = "mcdavid.json"
FILE_JSON_ORR = "orr.json"
FILE_JSON_ZOHORNA = "zohorna.json"

FILE_HTML_HOWE = "howe.html"
FILE_HTML_MCDAVID = "mcdavid.html"
FILE_HTML_ORR = "orr.html"
FILE_HTML_ZOHORNA = "zohorna.html"

NHL_URL = 'https://www.eliteprospects.com/league/nhl'

URL_HOWE = "https://www.eliteprospects.com/player/20605/gordie-howe"
URL_MCDAVID = "https://www.eliteprospects.com/player/183442/connor-mcdavid"
URL_ORR = "https://www.eliteprospects.com/player/19145/bobby-orr"
URL_ZOHORNA = "https://www.eliteprospects.com/player/28129/hynek-zohorna"

HTML_HOWE = get_html_file(PATH, FILE_HTML_HOWE)
HTML_MCDAVID = get_html_file(PATH, FILE_HTML_MCDAVID)
HTML_ORR = get_html_file(PATH, FILE_HTML_ORR)
HTML_ZOHORNA = get_html_file(PATH, FILE_HTML_ZOHORNA)

SELECTOR_HOWE = scrapy.Selector(text=HTML_HOWE)
SELECTOR_MCDAVID = scrapy.Selector(text=HTML_MCDAVID)
SELECTOR_ORR = scrapy.Selector(text=HTML_ORR)
SELECTOR_ZOHORNA = scrapy.Selector(text=HTML_ZOHORNA)

DICT_HOWE = get_json_file(PATH, FILE_JSON_HOWE)
DICT_MCDAVID = get_json_file(PATH, FILE_JSON_MCDAVID)
DICT_ORR = get_json_file(PATH, FILE_JSON_ORR)
DICT_ZOHORNA = get_json_file(PATH, FILE_JSON_ZOHORNA)

#Hynek Zohorna
##season test dicts
LEAGUE_DICT_PART_ZOHORNA = deepcopy(DICT_ZOHORNA)
NEW_DICT_ONE_ROW_ZOHORNA = deepcopy(DICT_ZOHORNA)
LEAGUE_DICT_ZOHORNA = deepcopy(DICT_ZOHORNA)
NEW_DICT_ONE_ROW_ZOHORNA = NEW_DICT_ONE_ROW_ZOHORNA[SEASON_STATS]["leagues"]["2013-2014"]
del NEW_DICT_ONE_ROW_ZOHORNA["Czechia"]
del NEW_DICT_ONE_ROW_ZOHORNA["Czechia2"]["SK Horácká Slavia Třebíč"]
LEAGUE_DICT_PART_ZOHORNA = LEAGUE_DICT_PART_ZOHORNA[SEASON_STATS]["leagues"]["2013-2014"]
del LEAGUE_DICT_PART_ZOHORNA["Czechia"]
del LEAGUE_DICT_PART_ZOHORNA["Czechia2"]["HC Havlíčkův Brod"]
LEAGUE_DICT_ZOHORNA = LEAGUE_DICT_ZOHORNA[SEASON_STATS]["leagues"]["2013-2014"]
del LEAGUE_DICT_ZOHORNA["Czechia"]

# Connor Mcdavid
#dicts for season stat tests
DICT_SEASON_MCDAVID = deepcopy(DICT_MCDAVID)
DICT_SEASON_PART_MCDAVID = deepcopy(DICT_MCDAVID)
DICT_SEASON_MCDAVID = DICT_SEASON_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
DICT_SEASON_PART_MCDAVID = DICT_SEASON_PART_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
del DICT_SEASON_PART_MCDAVID['WJC-20']["Canada U20"]

#Bobby Orr
##test values for stat dictionary
ONE_ROW_TEST_PATH_ORR = "//div[@id='league-stats']//table[contains(@class,'table table-condensed table-sortable')]//tr[8]/td"
ONE_ROW_TEST_STAT_DICT = DICT_ORR[SEASON_STATS]["leagues"]["1969-1970"]
ONE_ROW_TEST_STAT_DICT_LEAGUE = ONE_ROW_TEST_STAT_DICT["NHL"]
ONE_ROW_TEST_STAT_DICT_TEAM = ONE_ROW_TEST_STAT_DICT_LEAGUE["Boston Bruins"]
STAT = "leadership"
ONE_ROW_TEST_STAT_DICT_LEADERSHIP = ONE_ROW_TEST_STAT_DICT_TEAM[LEADERSHIP]


class TestPlayerScraper(unittest.TestCase):

    def setUp(self):

        self.player_zohorna = PlayerScraper(url=URL_ZOHORNA)
        self.player_mcdavid = PlayerScraper(url=URL_MCDAVID)
        self.player_orr = PlayerScraper(url=URL_ORR)
        self.player_howe = PlayerScraper(url=URL_HOWE)

    def test_get_info_all(self):

        self.assertEqual(self.player_zohorna.get_info_all(), DICT_ZOHORNA)
        self.assertEqual(self.player_mcdavid.get_info_all(), DICT_MCDAVID)
        self.assertEqual(self.player_orr.get_info_all(), DICT_ORR)
        self.assertEqual(self.player_howe.get_info_all(), DICT_HOWE)

class TestPlayerGeneralInfo(unittest.TestCase):

    @staticmethod   
    def get_general_info_dict(dict_player):

        gi_dict = deepcopy(dict_player)
        gi_dict  = gi_dict[GENERAL_INFO]
        del gi_dict[PLAYER_NAME]
        del gi_dict[PLAYER_UID]
        
        return gi_dict

    @classmethod
    def setUpclass(cls):

        #players gi objects
        cls.player_zohorna = PlayerGeneralInfo(
            selector=SELECTOR_ZOHORNA, url=URL_ZOHORNA)
        cls.player_mcdavid = PlayerGeneralInfo(
            selector=SELECTOR_HOWE, url=URL_HOWE)
        cls.player_orr = PlayerGeneralInfo(
            selector=SELECTOR_MCDAVID, url=URL_MCDAVID)
        cls.player_howe = PlayerGeneralInfo(
            selector=SELECTOR_ORR, url=URL_ORR)
        
        #players dict
        cls.gi_zohorna = TestPlayerGeneralInfo.get_general_info_dict(
            DICT_ZOHORNA)
        cls.gi_mcdavid = TestPlayerGeneralInfo.get_general_info_dict(
            DICT_MCDAVID)
        cls.gi_orr = TestPlayerGeneralInfo.get_general_info_dict(
            DICT_ORR)
        cls.gi_howe = TestPlayerGeneralInfo.get_general_info_dict(
            DICT_HOWE)

    def test_get_general_info(self):

        self.assertEqual(
            TestPlayerGeneralInfo.player_zohorna.get_general_info(), DICT_ZOHORNA[GENERAL_INFO])
        self.assertEqual(
            TestPlayerGeneralInfo.player_howe.get_general_info(), 
            DICT_HOWE[GENERAL_INFO])
        self.assertEqual(
            TestPlayerGeneralInfo.player_mcdavid.get_general_info(), DICT_MCDAVID[GENERAL_INFO])
        self.assertEqual(
            TestPlayerGeneralInfo.player_orr.get_general_info(), 
            DICT_ORR[GENERAL_INFO])


    def test_get_name(self):

        self.assertEqual(TestPlayerGeneralInfo.player_zohorna._get_name(),
                         DICT_ZOHORNA[GENERAL_INFO][PLAYER_NAME])

    def test_get_info_wrapper(self):

        self.assertEqual(
            TestPlayerGeneralInfo.player_mcdavid._get_info_wrapper(), TestPlayerGeneralInfo.gi_mcdavid)
        
    def test_get_info(self):

        for info in DICT_MCDAVID[GENERAL_INFO].keys():
            print('Testing info: ' + str(info))
            keep_list = False
            if info in TestPlayerGeneralInfo.player_mcdavid.KEEP_LIST:
                keep_list = True
            self.assertEqual(
            TestPlayerGeneralInfo.player_mcdavid._get_info(
                 info_name=info, keep_list=keep_list), 
                 DICT_MCDAVID[GENERAL_INFO][TestPlayerGeneralInfo.player_mcdavid.PROJECT_MAPPING[info]])

    
class TestFamilyRelations(unittest.TestCase):

    @classmethod
    def setUpclass(cls):

        cls.player_zohorna = FamilyRelations(selector=SELECTOR_ZOHORNA)
        cls.player_mcdavid = FamilyRelations(selector=SELECTOR_MCDAVID)
        cls.player_orr = FamilyRelations(selector=SELECTOR_ORR)
        cls.player_howe = FamilyRelations(selector=SELECTOR_HOWE)

    def _test_get_relation_dict(self):

        self.assertEqual(
            TestFamilyRelations.player_zohorna._get_relation_dict(), 
            DICT_ZOHORNA[RELATIONS])
        self.assertEqual(
            TestFamilyRelations.player_howe._get_relation_dict(), 
            DICT_HOWE[RELATIONS])
        self.assertEqual(
            TestFamilyRelations.player_mcdavid._get_relation_dict(), 
            DICT_MCDAVID[RELATIONS])
        self.assertEqual(
            TestFamilyRelations.player_orr._get_relation_dict(), 
            DICT_ORR[RELATIONS])

    def test_get_indvidual_relations(self):

        html_dict = TestFamilyRelations.player_howe._get_individual_relations()
        self.assertEqual(html_dict.keys(), DICT_HOWE[RELATIONS].keys())
        for relation in DICT_HOWE[RELATIONS]:
            print("Test Relation UID: " + relation)
            for uid in DICT_HOWE[RELATIONS][relation]:
                self.assertIn(uid, html_dict[relation])


class TestPlayerStats(unittest.TestCase):
    maxDiff = True

    @classmethod
    def setUpclass(cls):
         
        cls.player_howe = PlayerStats(selector=SELECTOR_HOWE)
        cls.player_mcdavid = PlayerStats(selector=SELECTOR_MCDAVID)
        cls.player_orr = PlayerStats(selector=SELECTOR_ORR)
        cls.player_zohorna = PlayerStats(Selector=SELECTOR_ZOHORNA)
    
    def test_both_season_types(self, player_o, dict_verify):
        for type in dict_verify[SEASON_STATS]:
            type_stats = player_o._get_stats(type=type)
            self.assertEqual(type_stats, dict_verify[SEASON_STATS][type])

    def test_get_all_stats(self):
        self.assertEqual(
            TestPlayerStats.player_howe.get_all_stats(), 
            DICT_HOWE[SEASON_STATS])
        self.assertEqual(
            TestPlayerStats.player_mcdavid.get_all_stats(), 
            DICT_MCDAVID[SEASON_STATS])
        self.assertEqual(
            TestPlayerStats.player_orr.get_all_stats(), 
            DICT_ORR[SEASON_STATS])
        self.assertEqual(
            TestPlayerStats.player_zohorna.get_all_stats(), 
            DICT_ZOHORNA[SEASON_STATS])

    def test_get_stats(self):
        self.test_both_season_types(
            TestPlayerStats.player_howe, DICT_HOWE)
        self.test_both_season_types(
            TestPlayerStats.player_mcdavid, DICT_MCDAVID)
        self.test_both_season_types(
            TestPlayerStats.player_orr, DICT_ORR)
        self.test_both_season_types(
            TestPlayerStats.player_zohorna, DICT_ZOHORNA)

    def test_get_season_stats(self):
         pfs = PlayerStats(selector=SELECTOR_MCDAVID)
         season_dict = pfs._get_season_stats(
             season_dict=DICT_SEASON_PART_MCDAVID, 
             path_type=PlayerStats.PATHS["path_league"], 
             ind=9)
         self.assertEqual(season_dict, DICT_SEASON_MCDAVID)

    def test_merge_league_dict(self):
        pfs = PlayerStats(selector=SELECTOR_ZOHORNA)
        new_dict = NEW_DICT_ONE_ROW_ZOHORNA
        merged_dict = pfs._merge_league_dict(
            old_dict=LEAGUE_DICT_PART_ZOHORNA, new_dict=new_dict)
        self.assertEqual(
            merged_dict, LEAGUE_DICT_ZOHORNA
            )


class TestOneRowStats(unittest.TestCase):

    def test_get_stat_dictionary(self):
        ors = OneRowStat(
        path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        row_stat_dict = ors._get_stat_dictionary()
        self.assertEqual(row_stat_dict, ONE_ROW_TEST_STAT_DICT)

    def test_get_league_dict(self):
        ors = OneRowStat(
            path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        league_dict = ors._get_league_dict(league="NHL")
        self.assertEqual(league_dict, ONE_ROW_TEST_STAT_DICT_LEAGUE)

    def test_get_league_url(self):
        ors = OneRowStat(
            path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        league_url = ors._get_league_url(league="NHL")
        self.assertEqual(league_url, NHL_URL)

    def test_get_team_dict(self):
        ors = OneRowStat(
            path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        team_dict = ors._get_team_dict()
        self.assertEqual(team_dict, ONE_ROW_TEST_STAT_DICT_TEAM)

    def test_get_stat_atribute(self):
        ors = OneRowStat(
            path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        attribute = ors._get_stat_atribute(key=STAT)
        self.assertEqual(attribute, ONE_ROW_TEST_STAT_DICT_LEADERSHIP)

    def test_extract_general_url(self):
        ors = OneRowStat(
            path = ONE_ROW_TEST_PATH_ORR, selector=SELECTOR_ORR
        )
        url = ors._extract_general_url(
            key_path="url_league", key_regex="league")
        self.assertEqual(url, NHL_URL)


class TestPlayerAchievements(unittest.TestCase):
    
    @classmethod
    def setUpclass(cls):
        cls.player_howe = PlayerAchievements(selector=SELECTOR_HOWE)
        cls.player_mcdavid = PlayerAchievements(selector=SELECTOR_MCDAVID)
        cls.player_orr = PlayerAchievements(selector=SELECTOR_ORR)
        cls.player_zohorna = PlayerAchievements(Selector=SELECTOR_ZOHORNA)

    @staticmethod
    def get_season_ind_combination(dict_):
        season_keys = dict_[ACHIEVEMENTS].keys()
        season_key = random.choice(season_keys)
        ind_ = dict_[ACHIEVEMENTS].keys().index(season_key)
        return season_key, ind_

    def test_get_achievements(self):
        self.assertEqual(
            TestPlayerAchievements.player_howe.get_achievements(), 
            DICT_HOWE[ACHIEVEMENTS])
        self.assertEqual(
            TestPlayerAchievements.player_mcdavid.get_achievements(), 
            DICT_MCDAVID[ACHIEVEMENTS])
        self.assertEqual(
            TestPlayerAchievements.player_orr.get_achievements(), 
            DICT_ORR[ACHIEVEMENTS])
        self.assertEqual(
            TestPlayerAchievements.player_zohorna.get_achievements(), 
            DICT_ZOHORNA[ACHIEVEMENTS])

    def test_get_season_achievements(self):
        season, ind_ = TestPlayerAchievements.get_season_ind_combination(
            DICT_ZOHORNA)
        self.assertEqual(TestPlayerAchievements.player_zohorna.get_season_achievements(ind=ind_), 
                         DICT_ZOHORNA[ACHIEVEMENTS[season]])
        season, ind_ = TestPlayerAchievements.get_season_ind_combination(
            DICT_MCDAVID)
        self.assertEqual(TestPlayerAchievements.player_mcdavid. get_season_achievements(ind=ind_), 
                         DICT_MCDAVID[ACHIEVEMENTS[season]])
        season, ind_ = TestPlayerAchievements.get_season_ind_combination(
            DICT_ZOHORNA)
        self.assertEqual(TestPlayerAchievements.player_orr.get_season_achievements(ind=ind_), 
                         DICT_ORR[ACHIEVEMENTS[season]])
        season, ind_ = TestPlayerAchievements.get_season_ind_combination(
            DICT_ZOHORNA)
        self.assertEqual(TestPlayerAchievements.player_howe.get_season_achievements(ind=ind_), 
                         DICT_HOWE[ACHIEVEMENTS[season]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
        


                








