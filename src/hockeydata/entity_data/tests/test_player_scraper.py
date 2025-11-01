import hockeydata.entity_data.tests.test_class as test_class 
import os
import unittest

from hockeydata.entity_data.scraper.player_scraper import *
from hockeydata.constants import *


data_loader = test_class.TestDataLoader()
pst_o = ps.PlaywrightSetUp()

#players urls
URL_ZOHORNA = "https://www.eliteprospects.com/player/190526/radim-zohorna"
URL_MCDAVID = "https://www.eliteprospects.com/player/183442/connor-mcdavid"
URL_ORR = "https://www.eliteprospects.com/player/19145/bobby-orr"
URL_HOWE = "https://www.eliteprospects.com/player/20605/gordie-howe"
URL_HASEK = "https://www.eliteprospects.com/player/8665/dominik-hasek"
URL_VASILEVKSY = "https://www.eliteprospects.com/player/70424/andrei-vasilevsky"

PLAYER_NAMES = ["howe", "mcdavid", "orr", "zohorna", 
                #"hasek", "vasilevsky"
                ] 
PATH_TEST_FILES = "./src/hockeydata/tests/test_data/scraper/player_scraper/"
NHL_URL = "https://www.eliteprospects.com/league/nhl"

#html file names for testing of scraping methods not depending on the changes on the current webpage
html_name_list = data_loader.get_names_with_formats(PLAYER_NAMES, "html")

#json file names
json_name_list = data_loader.get_names_with_formats(PLAYER_NAMES, "json")

#html files
html_file_list = data_loader.load_data("html", 
                                        PATH_TEST_FILES, 
                                        html_name_list,
                                        PLAYER_NAMES)

#json files 
json_file_list = data_loader.load_data("json",
                                        PATH_TEST_FILES,
                                        json_name_list,
                                        PLAYER_NAMES)

#selectors
selector_list = data_loader.create_selectors(html_file_list, PLAYER_NAMES)


class TestPlayerScraper(unittest.TestCase):


    def test_get_info_all_zohorna(self):
        playerscraper = PlayerScraper(url=URL_ZOHORNA, page=pst_o.page)
        dict_player = playerscraper.get_info_all()
        self.assertDictEqual(dict_player, json_file_list["zohorna"])

    def test_get_info_all_mcdavid(self):
        playerscraper = PlayerScraper(url=URL_MCDAVID, page=pst_o.page)
        dict_player = playerscraper.get_info_all()
        self.assertDictEqual(dict_player, json_file_list["mcdavid"])

    def test_get_info_all_orr(self):
        playerscraper = PlayerScraper(url=URL_ORR, page=pst_o.page)
        dict_player = playerscraper.get_info_all()
        self.assertDictEqual(dict_player, json_file_list["orr"])

    def test_get_info_all_howe(self):
        playerscraper = PlayerScraper(url=URL_HOWE, page=pst_o.page)
        dict_player = playerscraper.get_info_all()
        self.assertDictEqual(dict_player, json_file_list["howe"])

    #def test_get_info_all_hasek(self):
    #    playerscraper = PlayerScraper(url=URL_HASEK, page=pst_o.page)
    #    dict_player = playerscraper.get_info_all()
    #    self.assertDictEqual(dict_player, json_file_list["hasek"])

    #def test_get_info_all_vasilevsky(self):
    #    playerscraper = PlayerScraper(url=URL_VASILEVKSY, page=pst_o.page)
    #    dict_player = playerscraper.get_info_all()
    #    self.assertDictEqual(dict_player, json_file_list["vasilevsky"])


class TestPlayerGeneralInfo(unittest.TestCase):

    GI_PART = data_loader.get_nested_item(
        json_file_list,
        ["howe", GENERAL_INFO]
    )
    data_loader.delete_nested_key(
        GI_PART,
        [PLAYER_NAME])
    data_loader.delete_nested_key(
        GI_PART,
        [PLAYER_UID])


    def test_get_general_info(self):
        pgi = PlayerGeneralInfo(
        selector=selector_list["zohorna"], url=URL_ZOHORNA)
        gi_dict = pgi.get_general_info()
        self.assertDictEqual(gi_dict, json_file_list["zohorna"][GENERAL_INFO])

    def test_get_name(self):
        pgi = PlayerGeneralInfo(
            selector=selector_list["mcdavid"], url=URL_MCDAVID)
        name = pgi._get_name()
        self.assertEqual(name, json_file_list["mcdavid"][GENERAL_INFO][PLAYER_NAME])

    def test_get_info_wrapper(self):
        pgi = PlayerGeneralInfo(
        selector=selector_list["howe"], url=URL_HOWE)
        gi_dict = pgi._get_info_wrapper()
        self.assertDictEqual(gi_dict, TestPlayerGeneralInfo.GI_PART)

    def test_get_info(self):
        pgi = PlayerGeneralInfo(
            selector=selector_list["zohorna"], url=URL_ZOHORNA)
        gi_dict = json_file_list["zohorna"][GENERAL_INFO]
        for info in pgi.INFO_NAMES:
            keep_list = False
            if info in pgi.KEEP_LIST:
                keep_list = True
            info_val = pgi._get_info(info_name=info, keep_list=keep_list)
            self.assertEqual(info_val, gi_dict[pgi.PROJECT_MAPPING[info][0]])

    
#class TestFamilyRelations(unittest.TestCase):


#    def _test_get_relation_dict(self):
#        pfr = FamilyRelations(selector=selector_list["zohorna"])
#        relations_dict = pfr._get_relation_dict()
#        self.assertEqual(relations_dict, json_file_list["zohorna"][RELATIONS])

#    def test_get_indvidual_relations(self):
#        pfr = FamilyRelations(selector=selector_list["howe"])
#        html_dict = pfr._get_individual_relations()
#        self.assertEqual(
#            html_dict.keys(), json_file_list["howe"][RELATIONS].keys())
#        for relation in json_file_list["howe"][RELATIONS]:
#            print("Test Relation UID: " + relation)
#            for uid in json_file_list["howe"][RELATIONS][relation]:
#                self.assertIn(uid, html_dict[relation])


class TestPlayerStats(unittest.TestCase):


    maxDiff = True

    STATS_ONE_ROW_ZOHORNA = data_loader.get_nested_item(
        json_file_list["zohorna"],
        [SEASON_STATS, "leagues", "2018-19"])
    data_loader.delete_nested_key(
        STATS_ONE_ROW_ZOHORNA,
        ["Czechia", "BK Mladá Boleslav"])
    data_loader.delete_nested_key(
        STATS_ONE_ROW_ZOHORNA,
        ["Czechia2"])
    data_loader.delete_nested_key(
        STATS_ONE_ROW_ZOHORNA,
        ["International"])
    
    LEAGUE_DICT_PART_ZOHORNA = data_loader.get_nested_item(
        json_file_list["zohorna"], 
        [SEASON_STATS, "leagues", "2018-19"])
    data_loader.delete_nested_key(
        LEAGUE_DICT_PART_ZOHORNA, 
        ["Czechia2"])
    data_loader.delete_nested_key(
        LEAGUE_DICT_PART_ZOHORNA, 
        ["International"])
    data_loader.delete_nested_key(
        LEAGUE_DICT_PART_ZOHORNA,
        ["Czechia", "HC Kometa Brno"])

    LEAGUE_DICT_ZOHORNA = data_loader.get_nested_item(
        json_file_list["zohorna"],
        [SEASON_STATS, "leagues", "2018-19"])
    
    data_loader.delete_nested_key(
        LEAGUE_DICT_ZOHORNA, 
        ["Czechia2"])
    data_loader.delete_nested_key(
        LEAGUE_DICT_ZOHORNA, 
        ["International"])

    DICT_SEASON_PART_MCDAVID = data_loader.get_nested_item(
        json_file_list["mcdavid"], 
        [SEASON_STATS, "leagues", "2014-15"])
    
    data_loader.delete_nested_key(
        DICT_SEASON_PART_MCDAVID,
        ["OHL"])
    
    PATH_SEASON_MCDAVID = (Stats.PATHS["path_league"]
                            + SkaterStats.PATHS["stats_table_l"]
                            + str(9)
                            + SkaterStats.PATHS["stats_table_r"])

    def test_get_all_stats(self):
        pfs = SkaterStats(
            type_player="S",
            selector=selector_list["mcdavid"])
        stat_dict = pfs.get_all_stats()
        self.assertDictEqual(stat_dict, json_file_list["mcdavid"][SEASON_STATS])

    def test_get_stats(self):
        pfs = SkaterStats(
            type_player="S",
            selector=selector_list["mcdavid"])
        for type_ in json_file_list["mcdavid"][SEASON_STATS]:
            print(type_)
            type_stats = pfs._get_table_stats_wrapper(type_=type_)
            self.assertDictEqual(
                type_stats, json_file_list["mcdavid"][SEASON_STATS][type_])

    def test_get_season_stats(self):
         pfs = SkaterStats(
             type_player="S",
             selector=selector_list["mcdavid"])
         season_dict = pfs._get_season_stats(
             path_season=TestPlayerStats.PATH_SEASON_MCDAVID)
         self.assertDictEqual(
            season_dict, 
            TestPlayerStats.DICT_SEASON_PART_MCDAVID)

    def test_merge_league_dict(self):
        pfs = SkaterStats(
            type_player="S",
            selector=selector_list["zohorna"])
        new_dict = TestPlayerStats.STATS_ONE_ROW_ZOHORNA
        merged_dict = pfs._merge_league_dict(
            old_dict=TestPlayerStats.LEAGUE_DICT_PART_ZOHORNA, new_dict=new_dict)
        self.assertDictEqual(
            merged_dict, TestPlayerStats.LEAGUE_DICT_ZOHORNA
            )


class TestOneRowStats(unittest.TestCase):

    
    ONE_ROW_TEST_PATH_ORR = (Stats.PATHS["path_league"]
                             + SkaterStats.PATHS["stats_table_l"]
                             + str(8)
                             + SkaterStats.PATHS["stats_table_r"])
    ONE_ROW_TEST_STAT_DICT = data_loader.get_nested_item(
        json_file_list["orr"],
        [SEASON_STATS, "leagues", "1969-70"])
    STAT = "leadership"
    NHL_SEASON_URL = '/league/nhl/stats/1969-1970'


    def test_get_stat_dictionary(self):
        ors = OneRowSkaterStat(
        path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, 
        selector=selector_list["orr"])
        row_stat_dict = ors._get_stat_dictionary()
        self.assertDictEqual(
            row_stat_dict, 
            TestOneRowStats.ONE_ROW_TEST_STAT_DICT)

    def test_get_league_dict(self):
        ors = OneRowSkaterStat(
            path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, selector=selector_list["orr"])
        league_dict = ors._get_league_dict(league="NHL")
        self.assertDictEqual(league_dict, 
                             TestOneRowStats.ONE_ROW_TEST_STAT_DICT["NHL"])

    def test_get_league_url(self):
        ors = OneRowSkaterStat(
            path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, selector=selector_list["orr"])
        league_url = ors._get_league_url(league="NHL")
        self.assertEqual(league_url, TestOneRowStats.NHL_SEASON_URL)

    def test_get_team_dict(self):
        ors = OneRowSkaterStat(
            path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, selector=selector_list["orr"])
        team_dict = ors._get_team_dict()
        self.assertDictEqual(
            team_dict, 
            TestOneRowStats.ONE_ROW_TEST_STAT_DICT["NHL"]["Boston Bruins"])

    def test_get_stat_atribute(self):
        ors = OneRowSkaterStat(
            path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, selector=selector_list["orr"])
        attribute = ors._get_stat_atribute(key=TestOneRowStats.STAT)
        self.assertEqual(
            attribute, 
            TestOneRowStats.ONE_ROW_TEST_STAT_DICT["NHL"]["Boston Bruins"][LEADERSHIP])

    def test_extract_url(self):
        ors = OneRowSkaterStat(
            path = TestOneRowStats.ONE_ROW_TEST_PATH_ORR, selector=selector_list["orr"])
        url = ors._extract_url(
            key_path="url_league", key_regex="league")
        self.assertEqual(url, TestOneRowStats.NHL_SEASON_URL)


class TestPlayerAchievements(unittest.TestCase):


    ACHIEV_IND = 1


    def test_get_achievements(self):
        pa = PlayerAchievements(selector=selector_list["zohorna"])
        achiev_dict = pa.get_achievements()
        self.assertDictEqual(
            achiev_dict, 
            json_file_list["zohorna"][ACHIEVEMENTS])

    def test_get_season_achievements(self):
        pa = PlayerAchievements(selector=selector_list["zohorna"])
        season_achiev = pa.get_season_achievements(
            ind=TestPlayerAchievements.ACHIEV_IND)
        self.assertEqual(season_achiev, 
                             json_file_list["zohorna"][ACHIEVEMENTS]["2016-2017"])


if __name__ == "__main__":
    unittest.main()
        


                








