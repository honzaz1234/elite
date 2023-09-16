import unittest
from hockeydata.scraper.player_scraper import *
from hockeydata.constants import *
import scrapy
import json
from copy import deepcopy

PATH = "./tests/scraper/player_scraper/"

FILE_HTML_ZOHORNA = "zohorna.html"
FILE_JSON_ZOHORNA = "zohorna.json"

FILE_HTML_MCDAVID = "mcdavid.html"
FILE_JSON_MCDAVID = "mcdavid.json"

FILE_HTML_ORR = "orr.html"
FILE_JSON_ORR = "orr.json"

FILE_HTML_HOWE = "howe.html"
FILE_JSON_HOWE = "howe.json"


NHL_URL = 'https://www.eliteprospects.com/league/nhl'

#Hynek Zohorna

URL_ZOHORNA = "https://www.eliteprospects.com/player/28129/hynek-zohorna"
PATH_FILE = PATH + FILE_HTML_ZOHORNA
with open(PATH_FILE, "r") as f:
    HTML_ZOHORNA = f.read()

SELECTOR_ZOHORNA = scrapy.Selector(text=HTML_ZOHORNA)

PATH_FILE = PATH + FILE_JSON_ZOHORNA
f = open(PATH_FILE)
DICT_ZOHORNA = json.load(f)


##achievement test
ACHIEV_DICT_ZOHORNA = deepcopy(DICT_ZOHORNA)
ACHIEV_DICT_ZOHORNA = ACHIEV_DICT_ZOHORNA[ACHIEVEMENTS]
ACHIEV_IND = 1
ACHIEV_SEASON_ZOHORNA = ACHIEV_DICT_ZOHORNA['2011-2012']

##season test
LEAGUE_DICT_PART_ZOHORNA = deepcopy(DICT_ZOHORNA)
NEW_DICT_ONE_ROW_ZOHORNA = LEAGUE_DICT_PART_ZOHORNA[SEASON_STATS]["leagues"]["2013-2014"]["Czechia2"]["HC Havlíčkův Brod"]
LEAGUE_DICT_PART_ZOHORNA = LEAGUE_DICT_PART_ZOHORNA[SEASON_STATS]["leagues"]["2013-2014"]["Czechia2"]
del LEAGUE_DICT_PART_ZOHORNA["HC Havlíčkův Brod"]

# Connor Mcdavid

URL_MCDAVID = "https://www.eliteprospects.com/player/183442/connor-mcdavid"

PATH_FILE = PATH + FILE_HTML_MCDAVID
with open(PATH_FILE, "r") as f:
    HTML_MCDAVID = f.read()

SELECTOR_MCDAVID = scrapy.Selector(text=HTML_MCDAVID)

PATH_FILE = PATH + FILE_JSON_MCDAVID
f = open(PATH_FILE)
DICT_MCDAVID = json.load(f)

DICT_SEASON_MCDAVID = deepcopy(DICT_MCDAVID)
DICT_SEASON_MCDAVID = DICT_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
DICT_SEASON_PART_MCDAVID = DICT_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
del DICT_SEASON_PART_MCDAVID['WJC-20']["Canada U20"]

#Bobby Orr

URL_ORR = "https://www.eliteprospects.com/player/19145/bobby-orr"

PATH_FILE = PATH + FILE_HTML_ORR
with open(PATH_FILE, "r") as f:
    HTML_ORR = f.read()

SELECTOR_ORR = scrapy.Selector(text=HTML_ORR)

PATH_FILE = PATH + FILE_JSON_ORR
f = open(PATH_FILE)
DICT_ORR = json.load(f)

##test values for stat dictionary
ONE_ROW_TEST_PATH_ORR = "//div[@id='league-stats']//table[contains(@class,'table table-condensed table-sortable')]//tr[8]/td"
ONE_ROW_TEST_STAT_DICT = DICT_ORR[SEASON_STATS]["leagues"]["1969-1970"]
ONE_ROW_TEST_STAT_DICT_LEAGUE = ONE_ROW_TEST_STAT_DICT["NHL"]
ONE_ROW_TEST_STAT_DICT_TEAM = ONE_ROW_TEST_STAT_DICT_LEAGUE["Boston Bruins"]
STAT = "leadership"
ONE_ROW_TEST_STAT_DICT_LEADERSHIP = ONE_ROW_TEST_STAT_DICT_TEAM[LEADERSHIP]
# Gordie Howe

URL_HOWE = "https://www.eliteprospects.com/search/player?q=gordie+howe"

PATH_FILE = PATH + FILE_HTML_HOWE
with open(PATH_FILE, "r") as f:
    HTML_HOWE = f.read()

SELECTOR_HOWE = scrapy.Selector(text=HTML_HOWE)

PATH_FILE = PATH + FILE_JSON_HOWE
f = open(PATH + FILE_JSON_HOWE)
DICT_HOWE = json.load(f)

GI_ORIG  = DICT_HOWE[GENERAL_INFO]
del GI_ORIG[PLAYER_NAME]
del GI_ORIG[PLAYER_UID]

RELATION_KEYS = ['Brother', 'Son', 'Grandson']






class TestPlayerScraper(unittest.TestCase):

    def test_get_info_all_zohorna(self):
        playerscraper = PlayerScraper(url=URL_ZOHORNA)
        dict_player = playerscraper.get_info_all()
        self.assertEqual(dict_player, DICT_ZOHORNA)

    def test_get_info_all_mcdavid(self):
        playerscraper = PlayerScraper(url=URL_MCDAVID)
        dict_player = playerscraper.get_info_all()
        self.assertEqual(dict_player, DICT_MCDAVID)

    def test_get_info_all_orr(self):
        playerscraper = PlayerScraper(url=URL_ORR)
        dict_player = playerscraper.get_info_all()
        self.assertEqual(dict_player, DICT_ORR)

    def test_get_info_all_howe(self):
        playerscraper = PlayerScraper(url=URL_HOWE)
        dict_player = playerscraper.get_info_all()
        self.assertEqual(dict_player, DICT_HOWE)


class TestPlayerGeneralInfo(unittest.TestCase):

    def test_get_general_info(self):
        pgi = PlayerGeneralInfo(
        selector=SELECTOR_ZOHORNA, url=URL_ZOHORNA)
        gi_dict = pgi.get_general_info()
        self.assertEqual(gi_dict, DICT_HOWE[GENERAL_INFO])


    def test_get_name(self):
        pgi = PlayerGeneralInfo(
            selector=SELECTOR_MCDAVID, url=URL_MCDAVID)
        name = pgi._get_name()
        self.assertEqual(name, DICT_MCDAVID[GENERAL_INFO][PLAYER_NAME])

    def test_get_info_wraper(self):
        pgi = PlayerGeneralInfo(
        selector=SELECTOR_HOWE, url=URL_HOWE
        )
        gi_dict = pgi._get_info_wraper()
        self.assertEqual(gi_dict, GI_ORIG)

    def test_get_info(self):
        pgi = PlayerGeneralInfo(
            selector=SELECTOR_ZOHORNA, url=URL_ZOHORNA
        )
        gi_dict = DICT_ZOHORNA[GENERAL_INFO]
        for info in pgi.INFO_NAMES:
            keep_list = False
            if info in pgi.KEEP_LIST:
                keep_list = True
            info_val = pgi._get_info(info_name=info, keep_list=keep_list)
            self.assertEqual(info_val, gi_dict[pgi.PROJECT_MAPPING[info]])

    
class TestFamilyRelations(unittest.TestCase):

    def _test_get_relation_dict(self):
        pfr = FamilyRelations(selector=SELECTOR_MCDAVID)
        relations_dict = pfr._get_relation_dict()
        self.assertEqual(relations_dict, DICT_HOWE[RELATIONS])

    
    def test_get_indvidual_relations(self):
        pfr = FamilyRelations(selector=SELECTOR_MCDAVID)
        html_dict = pfr._get_individual_relations()
        self.assertEqual(html_dict.keys(), DICT_HOWE[RELATIONS].keys())
        for relation in DICT_HOWE[RELATIONS]:
            print("Test Relation UID: " + relation)
            for uid in DICT_HOWE[RELATIONS][relation]:
                self.assertIn(uid, html_dict[relation])


class TestPlayerStats(unittest.TestCase):

    def test_get_all_stats(self):
        pfs = PlayerStats(selector=SELECTOR_MCDAVID)
        stat_dict = pfs.get_all_stats()
        self.assertEqual(stat_dict, DICT_MCDAVID[SEASON_STATS])

    def test_get_stats(self):
        pfs = PlayerStats(selector=SELECTOR_MCDAVID)
        for type in DICT_MCDAVID[SEASON_STATS]:
            print(type)
            type_stats = pfs._get_stats(type=type)
            self.assertEqual(type_stats, DICT_MCDAVID[SEASON_STATS][type])

    def test_get_season_stats(self):
         pfs = PlayerStats(selector=SELECTOR_ZOHORNA)
         season_dict = pfs._get_season_stats(
             season_dict=DICT_SEASON_PART_MCDAVID, path_type="league", ind=9)
         self.assertEqual(season_dict, DICT_SEASON_MCDAVID)

    def test_merge_season_dict(self):
        pfs = PlayerStats(selector=SELECTOR_ZOHORNA)
        new_dict = NEW_DICT_ONE_ROW_ZOHORNA
        merged_dict = pfs._merge_league_dict(
            old_dict=LEAGUE_DICT_PART_ZOHORNA, new_dict=new_dict)
        self.assertEqual(
            merged_dict, LEAGUE_DICT_PART_ZOHORNA
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
        team_dict = ors._get_league_url(league="NHL")
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

    def test_get_achievements(self):
        pa = PlayerAchievements(selector=SELECTOR_ZOHORNA)
        achiev_dict = pa.get_achievements()
        self.assertEqual(achiev_dict, ACHIEV_DICT_ZOHORNA)


    def test_get_season_achievements(self):
        pa = PlayerAchievements(selector=SELECTOR_ZOHORNA)
        season_achiev = pa.get_season_achievements(ind=ACHIEV_IND)
        self.assertEqual(season_achiev, ACHIEV_SEASON_ZOHORNA)


if __name__ == "__main__":
    unittest.main()
        


                








