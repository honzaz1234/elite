import scrapy
import json
from copy import deepcopy
from hockeydata.constants import *

PATH = "./data/test_data/scraper/player/"

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
with open(PATH + FILE_HTML_ZOHORNA, "r") as f:
    HTML_ZOHORNA = f.read()

SELECTOR_ZOHORNA = scrapy.Selector(text=HTML_ZOHORNA)

f = open(PATH + FILE_JSON_ZOHORNA)
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

with open(PATH + FILE_HTML_MCDAVID, "r") as f:
    HTML_MCDAVID = f.read()

SELECTOR_MCDAVID = scrapy.Selector(text=HTML_MCDAVID)

f = open(PATH + FILE_JSON_MCDAVID)
DICT_MCDAVID = json.load(f)

DICT_SEASON_MCDAVID = deepcopy(DICT_MCDAVID)
DICT_SEASON_MCDAVID = DICT_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
DICT_SEASON_PART_MCDAVID = DICT_MCDAVID[SEASON_STATS]["leagues"]["2014-2015"]
del DICT_SEASON_PART_MCDAVID['WJC-20']["Canada U20"]

#Bobby Orr

URL_ORR = "https://www.eliteprospects.com/player/19145/bobby-orr"

with open(PATH + FILE_HTML_ORR, "r") as f:
    HTML_ORR = f.read()

SELECTOR_ORR = scrapy.Selector(text=HTML_ORR)

f = open(PATH + FILE_JSON_ORR)
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

with open(PATH + FILE_HTML_HOWE, "r") as f:
    HTML_HOWE = f.read()

SELECTOR_HOWE = scrapy.Selector(text=HTML_HOWE)

f = open(PATH + FILE_JSON_HOWE)
DICT_HOWE = json.load(f)

GI_ORIG  = DICT_HOWE[GENERAL_INFO]
del GI_ORIG[PLAYER_NAME]
del GI_ORIG[PLAYER_UID]

RELATION_KEYS = ['Brother', 'Son', 'Grandson']

