import requests
import scrapy
import re

from hockeydata.constants import *


class PlayerScraper:

    """Class for downloading information from individual players webpages;
       includes one method which wraps around methods from classes for downloading 
       individual subparts of player web page:
       a) general info (name, position, age...)
       b) player  season stats 
       c) player achievements 
    """

    def __init__(self, url):
        """Arguments:
        url - url of player profile
        html - html code of player profile webpage
        selector - selector object created from html code used for parsing data for individual values 
        """
        self.url = url
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_info_all(self, years=None):
        """Wrapper function containing all individual methods for scrapping data into self.info_dict
            Output: dictionary used  for storing data on a player
                    Stats - keys: individual seasons -> (league - team) -> regular_season_playoff -> stats (list)
                            structure of list with data for one season: 
                            a) for player - games played, goals, assists, total points, PIM, plus-minus
                            b) for goalie - games played, gd?, goal against average, save percentage, 
                                            goals against, shots saved, shutouts, wins, looses, ties, toi
                    Info - one level dictionary with general info of player 
                    Keys: name, height - (cm/f,inch), weight - (kg/lbs), 
                    nation, Shoots - (L,R), youth team, contract - (year/year),
                    cap hit, nhl rights - (team, signed), drafed - (year, round, position)
                    Achievements  - keys are seasons, values are lists with award names
            Arguments: years - 
            """
        dict_player = {}
        gi_o = PlayerGeneralInfo(selector=self.selector,
                                 url=self.url)
        dict_player[GENERAL_INFO] = gi_o.get_general_info()
        a_o = PlayerAchievements(selector=self.selector)
        f_r_o = FamilyRelations(selector=self.selector)
        dict_player[RELATIONS] = f_r_o._get_relation_dict()
        dict_player[ACHIEVEMENTS] = a_o.get_achievements()
        s_o = PlayerStats(selector=self.selector)
        dict_player[SEASON_STATS] = s_o.get_all_stats(years=years)
        return dict_player


class PlayerGeneralInfo():

    PATHS = {"player_name": "//h1[@class ="
                            "'ep-entity-header__name']//text ()",
             "gi_l": "//div[contains(@class,"
                    "'ep-list__item--is-compact')]"
                    "/div[2][preceding-sibling::div[1]"
                    "[contains(text(), '",
             "gi_r": "')]]//text()"
    }

    INFO_NAMES = [
        "Date of Birth", "Age", "Place of Birth", "Nation", "Position", "Height", "Weight", "Shoots", "Contract", "Cap Hit", "NHL Rights",
        "Drafted", "Status", "Catches"
    ]

    KEEP_LIST = ["Drafted", "Nation"]

    PROJECT_MAPPING = {
        "Date of Birth": BIRTH_DATE, 
        "Age": AGE,
        "Place of Birth": BIRTH_PLACE_STRING, 
        "Nation": NATIONALITY, 
        "Position": POSITION,
        "Height": HEIGHT,
        "Weight": WEIGHT,
        "Shoots": SHOOTS,
        "Catches": CATCHES,
        "Contract": CONTRACT_END,
        "Cap Hit": CAP_HIT,
        "NHL Rights": NHL_RIGHTS,
        "Drafted": DRAFT_LIST,
        "Status": ACTIVE,
    } 
    

    def __init__(self, selector, url):
        """attribute: selector - selector created from html of whole player webpage"""

        self.selector = selector
        self.url = url

    def get_general_info(self):
        dict_gi = self._get_info_wraper()
        dict_gi[PLAYER_NAME] = self._get_name()
        dict_gi[PLAYER_UID] = re.findall(PLAYER_UID_REGEX,
                                         self.url)[0]
        return dict_gi

    def _get_name(self):
        """used to get player name"""

        name = (self.selector
                .xpath(PlayerGeneralInfo.PATHS["player_name"])
                .getall())
        name = [string.strip() for string in name]
        name = [string for string in name if string != ""]
        return name[0].strip()

    def _get_info_wraper(self):
        """wraper method for downloading individual all info information from facts table"""

        dict_gi = {}
        for info_name in PlayerGeneralInfo.INFO_NAMES:
            keep_list = False
            key_name = PlayerGeneralInfo.PROJECT_MAPPING[info_name]
            if info_name in PlayerGeneralInfo.KEEP_LIST:
                keep_list = True
            dict_gi[key_name] = self._get_info(info_name=info_name,
                                                keep_list=keep_list)
        return dict_gi

    def _get_info(self, info_name, keep_list):
        "method for getting one info value from Facts table on player's webpage"

        info_path_val = (PlayerGeneralInfo.PATHS["gi_l"]
                         + info_name
                         + PlayerGeneralInfo.PATHS["gi_r"])
        info_val = self.selector.xpath(info_path_val).getall()
        info_val = [string.strip() for string in info_val]
        info_val = [string for string in info_val if string != ""]
        if info_val == []:
            info_val = [None]
        if keep_list == False:
            return info_val[0]
        else:
            return info_val

class FamilyRelations():

    """class for creating dictionary with u_ids of players that are related to the the player for which the info is downloaded;
    for each type of family connection there is one key with a list of uids"""

    PATHS = {
        "whole_text": "//p[@class='ep-text mb-2']"
    }

    RELATION_REGEX = ("($|son|grandson|brother|father|uncle|"
                      "cousin|paternal\sgrandfather|maternal\sgrandfather|" "nephew|great\smaternal\sgrandfather|" "great\spaternal\sgrandfather|brother\-in\-law|" "brothers\-in\-law|son\-in\-law|sons\-in\-law|" "fathers\-in\-law|father\-in\-law|uncle\-in\-law|" "uncles\-in\-law|cousin\-in\-law|cousins\-in\-law|" "great\snephew|great\suncle)s{0,1}")
    
    URL_UID_REGEX = "player\=([0-9]+)"

    def __init__(self, selector):
        self.selector = selector
        self._relations_regex = ("("
                                 + FamilyRelations.RELATION_REGEX
                                 + ")"
                                 + ":")
        self._relation_url_regex = ":(.+)(:|$)"

    def _get_individual_relations(self):
        """creates dictionary in which the keys are the relations that exist for the player and values are the html code in which u_ids of these relations can be found
        """

        text = (self.selector
                .xpath(FamilyRelations.PATHS["whole_text"])
                .getall())
        if text == []:
            return {}
        else:
            text = text[0]
        r_list = re.findall(self._relations_regex, text, flags=re.IGNORECASE)
        data_list = re.findall(self._relation_url_regex,
                               text,
                               flags=re.IGNORECASE)
        data_list = re.split(":", text, flags=re.IGNORECASE)
        data_list.pop(0)
        print(r_list)
        print(data_list)
        dict_strings = {}
        for ind in range(len(r_list)):
            dict_strings[r_list[ind][1]] = data_list[ind]
        return dict_strings

    def _get_relation_dict(self):
        relations_uid = {}
        player_string_dict = self._get_individual_relations()
        for relation in player_string_dict:
            list_uid = re.findall("player\=([0-9]+)",
                                  player_string_dict[relation])
            if list_uid == []:
                continue
            relations_uid[relation] = list_uid
        print(relations_uid)
        return relations_uid


class PlayerStats():

    """class for downloading season data from stat tables on player webpage"""

    # paths to access statistics in league and tournament tables on player webpage
    PATHS = {
        "path_league": "//div[@id='league-stats']",
        "path_tournament": "//div[@id='cup-stats']",
        "stats_table_l": "//table[contains(@class,'table table-"
                         "condensed table-sortable')]//tr[",
        "stats_table_r": "]/td",
        "stat_years": "//table[contains(@class,'table table-condensed table-sortable')]/tbody/tr/@data-season"
    }

    def __init__(self, selector):
        """attribute: selector - selector created from html of whole player webpage"""

        self.selector = selector

    def get_all_stats(self, years=None):
        """wrapper function for downloading stats from both league and tournament tables"""

        dict_stats = {}
        dict_stats["leagues"] = self._get_stats(years=years, type="league")
        dict_stats["tournaments"] = self._get_stats(years=years,
                                                    type="tournament")
        return dict_stats

    def _get_stats(self, type, years=None):
        
        """function for downloading data from the whole table (league, tournament) with the player season statistics
        """

        if type == "league":
            path_type = PlayerStats.PATHS["path_league"]
        elif type == "tournament":
            path_type = PlayerStats.PATHS["path_tournament"]
        dict_stats = {}
        path_years = path_type + PlayerStats.PATHS["stat_years"]
        list_years = self.selector.xpath(path_years).getall()
        for ind in range(1, len(list_years) + 1):
            season = list_years[ind - 1]
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            if season not in dict_stats:
                dict_stats[season] = {}
            dict_stats[season] = self._update_season_stats(
                season_dict=dict_stats[season], path_type=path_type, ind=ind)
        return dict_stats
    
    def _update_season_stats(self, season_dict, path_type, ind):

        """adds one row from stat table to stat dictionary"""

        new_season_dict = {}
        path_season = (path_type
                        + PlayerStats.PATHS["stats_table_l"]
                        + str(ind)
                        + PlayerStats.PATHS["stats_table_r"])
        row_o = OneRowStat(path=path_season, selector=self.selector)
        sub_dict = row_o._get_stat_dictionary()
        new_season_dict = self._merge_season_dict(
                old_dict=season_dict, new_dict=sub_dict)
        return new_season_dict

    def _merge_season_dict(self, old_dict, new_dict):
        
        """merges season dictionary with new stat row dictionary - needed because sometimes player changes team in one competition over the season
        """

        new_merged_dict = old_dict.copy()
        for league in new_dict:
            if  league in old_dict:
                new_merged_dict[league] = {
                    **old_dict[league], **new_dict[league]
                }
            else:
                new_merged_dict[league] = new_dict[league]
        return new_merged_dict
        

class OneRowStat():

    PATHS = {
            "team": "[@class = 'team']/span/a[1]/text()",
            "leadership": "[@class = 'team']/span/a[2]/text()",
            "league": "[@class = 'league']/a/text()",
            "stats_regular": "[contains(@class,'regular')]/text()",
            "stats_playoff": "[contains(@class,'postseason ')]/text()",
            "url_league": "[@class = 'league']/a/@href",
            "url_team": "[@class = 'team']//a[1]/@href",
    }

    REGEX = {
        "team": "(.+)\/[^\/]+$",
        "league": "(.+)\/stats"
    }

    def __init__(self, path, selector):
        self.path_to_row = path
        self.selector = selector

    def _get_stat_dictionary(self):
        """creates stat dicitonary from one row in stat table"""

        team = self._get_stat_atribute(key="team")
        if team is None:
            return {}
        league = self._get_stat_atribute(key="league")
        leadership = self._get_stat_atribute(key="leadership")
        stat_play_off = self._get_stat_atribute(
            key="stats_regular", keep_list=True)
        stat_regular = self._get_stat_atribute(
            key="stats_playoff", keep_list=True)
        if league is not None:
            league_url = self._extract_general_url(
                key_path="url_league", key_regex="league")
        else:
            league_url = None
        team_url = self._extract_general_url(
             key_path="url_team", key_regex="team")
        dict_row = {}
        dict_row[league] = {}
        dict_row[league][LEAGUE_URL] = league_url
        dict_row[league][team] = {}
        dict_row[league][team][REGULAR_SEASON] = stat_regular
        dict_row[league][team][PLAY_OFF] = stat_play_off
        dict_row[league][team][LEADERSHIP] = leadership
        dict_row[league][team][TEAM_URL] = team_url
        return dict_row
    
    def _get_stat_dictionary(self):
        """method for getting stat dictionary of one row of stat table"""

        dict_stat = {}
        league = self._get_stat_atribute(key="league")
        if league is None:
            return {}
        dict_stat[league] = self._get_league_dict(league=league)
        if dict_stat[league] == {}:
            return {}
        else:
            return dict_stat
    
    def _get_league_dict(self, league):
        """method for getting league dictionary of one row of stat table"""

        league_dict = {}
        team = self._get_stat_atribute(key="team")
        if team is None:
            return {}
        league_dict[team] = self._get_team_dict()
        league_dict[LEAGUE_URL] = self._get_league_url(league=league)
        return league_dict

    def _get_league_url(self, league):
        """wrapper method for getting league url"""

        if league is not None:
            league_url = self._extract_general_url(
                key_path="url_league", key_regex="league")
        else:
            league_url = None
        return league_url
    
    def _get_team_dict(self):
        """get dict with information regarding the team from one row of stat table"""

        dict_team = {}
        stat_play_off = self._get_stat_atribute(
            key="stats_playoff", keep_list=True)
        stat_regular = self._get_stat_atribute(
            key="stats_regular", keep_list=True)
        leadership = self._get_stat_atribute(key="leadership")
        team_url = self._extract_general_url(
             key_path="url_team", key_regex="team")
        dict_team[REGULAR_SEASON] = stat_regular
        dict_team[PLAY_OFF] = stat_play_off
        dict_team[LEADERSHIP] = leadership
        dict_team[TEAM_URL] = team_url
        return dict_team

    def _get_stat_atribute(self, key, keep_list=False):

        """method for extracting one attribute from stat row(team, league, capitancy, season stats
        """

        path_stat = self.path_to_row + OneRowStat.PATHS[key]
        stat_list = self.selector.xpath(path_stat).getall()
        stat_list = [string.strip() for string in stat_list]
        if stat_list == [] or set(stat_list)=={""}:
            return None
        elif keep_list==True:
            return stat_list
        else:
            return stat_list[0]
        
    def _extract_general_url(self, key_path, key_regex):

        """method for extracting url of team and league
        to which the statistics are related
        """

        path_url = self.path_to_row + OneRowStat.PATHS[key_path]
        list_data = self.selector.xpath(path_url).getall()
        orig_url = list_data[0]
        url_list = re.findall(OneRowStat.REGEX[key_regex], orig_url)
        url = url_list[0]
        return url

class PlayerAchievements():


    """class grouping methods for extracting achieviements of player"""

    PATHS = {
        "achievements_l": "//li[",
        "achievements_r": "]/div[@class='col-xs-10']//li/a/text()",
        "achievements_years": "//div[@class='col-xs-4 season']/text()"
    }

    def __init__(self, selector):
        self.selector = selector

    def get_achievements(self, years=None):
        """method for downloading achievements of player into dictionary"""

        dict_achiev = {}
        list_years = self.selector.xpath(
            PlayerAchievements.PATHS["achievements_years"]).getall()
        list_years = [string.strip() for string in list_years]
        for ind in range(1, len(list_years) + 1):
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            dict_achiev[list_years[ind - 1]] = self.get_season_achievements(
                ind=ind)
        return dict_achiev
    

    def get_season_achievements(self, ind):
        """method for getting list of achievements in one season"""

        path = (PlayerAchievements.PATHS["achievements_l"]
                    + str(ind)
                    + PlayerAchievements.PATHS["achievements_r"])
        awards = self.selector.xpath(path).getall()
        awards = [award.strip() for award in awards]
        return awards


