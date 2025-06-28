import hockeydata.playwright_setup.playwright_setup as ps
import playwright.sync_api as sync_api
import re
import scrapy
import time

import common_functions as cf

from constants import *
from decorators import time_execution
from logger.logging_config import logger


class PlayerScraper:
    """Class for downloading information from individual players webpages;
       includes one method which wraps around methods from classes for downloading 
       individual subparts of player web page:
       a) general info (name, position, age...)
       b) player  season stats 
       c) player achievements 
    """


    TABLE_ROW_XPATH = ("//section[@id='player-statistics']"
                      + "//tr[@class='SortTable_tr__L9yVC']")


    def __init__(self, url: str, page: sync_api.Page):
        """Arguments:
        url - url of webpage with player's information
        html - html code of player profile webpage
        selector - selector object created from html of player's webpage   
                   used for attaining individual pieces of information
        """

        self.url = url
        self.page = page
        self.selector = None


    @time_execution
    def get_info_all(self, years: list=None) -> dict:
        """Wrapper method containing all individual methods for scrapping data 
            Output: dictionary used  for storing data on a player
                    Stats - keys: individual seasons -> (league - team) -> regular_season_playoff -> stats (list)
                            structure of list with data for one season: 
                            a) for player - games played, goals, assists, total points, PIM, plus-minus
                            b) for goalie - games played, gd?, goal against average, save percentage, 
                                            goals against, shots saved, shutouts, wins, looses, ties, toi
                    Info - one level dictionary with general info of player 
                    Keys: name, height - (cm/f,inch), weight - (kg/lbs), 
                    nation, Shoots - (L, R), youth team, contract - (season),
                    cap hit, nhl rights - (team, signed), drafed - (string with year, round and position)
                    Achievements  - keys are seasons, values are lists with award names
            Arguments: years - list of years for which data is downloaded 
            """
        logger.info(f'Scraping of new player info at web adress: {self.url}'
                    f' started')
        ps.go_to_page_wait_selector(
            page=self.page, url=self.url,
            sel_wait=PlayerScraper.TABLE_ROW_XPATH)
        self.selector = scrapy.Selector(text=self.page.content())
        dict_player = {}
        gi_o = PlayerGeneralInfo(selector=self.selector,
                                 url=self.url)
        dict_player[GENERAL_INFO] = gi_o._get_general_info()
        a_o = PlayerAchievements(selector=self.selector)
        #f_r_o = FamilyRelations(selector=self.selector)
        #dict_player[RELATIONS] = f_r_o._get_relation_dict()
        dict_player[ACHIEVEMENTS] = a_o._get_achievements()
        stats_object = self.stats_factory(
            general_info=dict_player[GENERAL_INFO])
        dict_player[SEASON_STATS] = stats_object._get_all_stats(years=years)
        logger.debug(f"player dict: {dict_player}")
        logger.info(f"Dict from player with name " 
                    f"{dict_player[GENERAL_INFO][PLAYER_NAME]} "
                    f"({dict_player[GENERAL_INFO][PLAYER_UID]})"
                    f" succesfully scraped")
        return dict_player
    
    def stats_factory(self, general_info: dict) -> 'Stats':
        """given that attaining stats for goalies and players differ
        they are divided into separate classes
        """

        if GOALIE_PLAYER in general_info[POSITION]:
            stats_object = GoalieStats(
                type_player=GOALIE_PLAYER, selector=self.selector,
                page=self.page)
        else:
            stats_object = SkaterStats(
                type_player=OTHER_PLAYER, selector=self.selector)
        return stats_object


class PlayerGeneralInfo():

    #list of xpaths that are used to access information on player

    PATHS = {
        "player_name": "//div[contains(@class, 'Profile_titleWrapper')]"
                             "/h1/text()",
        "gi_left": "//section[@id='player-facts']//li"
                     "/span[contains(text(), '",
        "gi_right": "')]/following-sibling::"
    }

    #list of attributes that can be found in the table with general #information on player's page

    INFO_NAMES = [
        "Date of Birth", "Age", "Place of Birth", "Nation", "Position", "Height", "Weight", "Shoots", "Contract", "Cap Hit", "NHL Rights",
        "Drafted", "Status", "Catches"
    ]

    #list of attributes from INFO_NAMES list which values should be kept in 
    #form of list

    KEEP_LIST = ["Drafted", "Nation"]

    #mapping of names of attributes on the webpage into names in scrapped #dictionary

    PROJECT_MAPPING = {
        "Date of Birth": [BIRTH_DATE, "a/text()"], 
        "Age": [AGE, "text()"],
        "Place of Birth": [BIRTH_PLACE_STRING, "a/text()"],
        "Nation": [NATIONALITY, "div//text()"], 
        "Position": [POSITION, "text()"],
        "Height": [HEIGHT, "text()"],
        "Weight": [WEIGHT, "text()"],
        "Shoots": [SHOOTS, "text()"],
        "Catches": [CATCHES, "text()"],
        "Contract": [CONTRACT_END, "text()"],
        "Cap Hit": [CAP_HIT, "div//text()"],
        "NHL Rights": [NHL_RIGHTS, "a/text()"],
        "Drafted": [DRAFT_LIST, "div/a/node()"],
        "Status": [ACTIVE, "text()"],
    } 
    
    def __init__(self, selector: scrapy.Selector, url: str):
        """attribute: selector - selector created from html of
                                 player's webpage"
                      url - url of player's webpage            
        """

        self.selector = selector
        self.url = url

    def _get_general_info(self) -> dict:
        """wrapper method for attaining all available info on player"""
        
        dict_gi = self._get_info_wrapper()
        dict_gi[PLAYER_NAME] = self._get_name()
        dict_gi[PLAYER_UID] = re.findall(PLAYER_UID_REGEX,
                                         self.url)[0]
        logger.debug(f"player dict: {dict_gi}")
        logger.debug(f"Dictionary with general info of player " 
                    f"{dict_gi[PLAYER_NAME]}"
                    f" succesfully scraped")
        return dict_gi

    def _get_name(self) -> str:
        """method for attaining player's name"""

        name = (self.selector
                .xpath(PlayerGeneralInfo.PATHS["player_name"])
                .getall())
        name = [string.strip() for string in name if string != ""]
        logger.debug(f"Name of player:" 
                    f" {name[0]}"
                    f" succesfully scraped")
        return name[0].strip()

    def _get_info_wrapper(self) -> dict:
        """wrapper method for downloading all general info from facts table"""

        dict_gi = {}
        for info_name in PlayerGeneralInfo.INFO_NAMES:
            keep_list = False
            key_name = PlayerGeneralInfo.PROJECT_MAPPING[info_name][0]
            if info_name in PlayerGeneralInfo.KEEP_LIST:
                keep_list = True
            dict_gi[key_name] = self._get_info(info_name=info_name,
                                                keep_list=keep_list)
        return dict_gi

    def _get_info(self, info_name: str, keep_list: bool) -> int|str|list:
        """method for getting one value from general info table on player's webpage
        """

        info_path_val = (PlayerGeneralInfo.PATHS["gi_left"]
                         + info_name
                         + PlayerGeneralInfo.PATHS["gi_right"]
                         + PlayerGeneralInfo.PROJECT_MAPPING[info_name][1]
                         + "[not(self::comment())]")
        info_val = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=info_path_val,
            optional=True
        )
        info_val = (
            [info.strip() for info in info_val if info != ""] 
            if info_val is not None else None 
            )
        if info_name == 'Drafted':
            info_val = self.get_drafts(info_val)
        if info_val == []:
            info_val = [None]
        logger.debug(f"Info ({info_name}):" 
                     f"with value {info_val}"
                     f" succesfully scraped")
        if keep_list == False:
            if info_val[0] is not None:
                return ' '.join(info_val)
        else:
            return info_val

    def get_drafts(self, drafts: list) -> list:
        """method to get  draft strings from  list of string values
        (info about drafts is separated on multiple lines)"""
        
        if drafts == [None]:
            return [None]
        if len(drafts) < 3:
            return drafts
        n_drafts = int(len(drafts) / 7)
        new_drafts = []
        for ind in range(n_drafts):
            draft =  " ".join(drafts[(7*ind):(7*(ind + 1))])
            new_drafts.append(draft)
        return new_drafts


class FamilyRelations():
    """class for creating dictionary with u_ids of players that are related to the the player for which the info is downloaded;
    for each type of family connection there is one key with a list of uids
    data on relation are not accessible from the table like general info but instead must be extracted from one paragraph of text on the webpage
    """

    #xpath to acces text in which all of the relations are mentioned on the #webpage

    PATHS = {
        "whole_text": "//div[@class='PlayerFacts_description__ujmxU']"
    }

    #regex used to access relation types

    RELATION_REGEX = ("($|son|grandson|brother|father|uncle|"
                      "cousin|paternal\sgrandfather|maternal\sgrandfather|" "nephew|great\smaternal\sgrandfather|" "great\spaternal\sgrandfather|brother\-in\-law|" "brothers\-in\-law|son\-in\-law|sons\-in\-law|" "fathers\-in\-law|father\-in\-law|uncle\-in\-law|" "uncles\-in\-law|cousin\-in\-law|cousins\-in\-law|" "great\snephew|great\suncle)s{0,1}")
    
    #regex used to acces uids of player's relations

    URL_UID_REGEX = "player\=([0-9]+)"

    def __init__(self, selector: scrapy.Selector):
        """selector - original selector
           relations_regex - regex for extracting relation types from  
                             text on webpage
           relation_url_regex - regex for extracting url of relations 
        """
        
        self.selector = selector
        self.relations_regex = ("("
                                 + FamilyRelations.RELATION_REGEX
                                 + ")"
                                 + ":")
        self.relation_url_regex = ":(.+)(:|$)"

    def _get_individual_relations(self) -> dict:
        """creates dictionary in which the keys are the relations that exist for the player and values are the html code in which uids of these relations can be found
        """

        text = (self.selector
                .xpath(FamilyRelations.PATHS["whole_text"])
                .getall())
        if text == []:
            return {}
        else:
            text = text[0]
        r_list = re.findall(self.relations_regex, text, flags=re.IGNORECASE)
        data_list = re.findall(self.relation_url_regex,
                               text,
                               flags=re.IGNORECASE)
        data_list = re.split(":", text, flags=re.IGNORECASE)
        data_list.pop(0)
        dict_strings = {}
        for ind in range(len(r_list)):
            dict_strings[r_list[ind][1]] = data_list[ind]
        return dict_strings

    def _get_relation_dict(self) -> dict:
        """wrapper method for creating dictionary with types of relations and uids of players
        """

        relations_uid = {}
        player_string_dict = self._get_individual_relations()
        for relation in player_string_dict:
            list_uid = re.findall("player\=([0-9]+)",
                                  player_string_dict[relation])
            if list_uid == []:
                continue
            relations_uid[relation] = list_uid
        logger.debug(f"Relation Dict: {relations_uid}")
        return relations_uid


class Stats():
    """class for downloading season data from stat tables on player webpage"""

    # xpaths to access statistics in league and tournament tables on player webpage

    PATHS = {
        "path_league": "//section[@id='player-statistics' "
                       "and not(contains(., 'No Data Found'))]",
        "path_tournament": "//section[@id='tournament-statistics' "
                           "and not(contains(., 'No Data Found'))]",
        "stats_table_l": "//tbody//tr[",
        "stats_table_r": "]/td",
        "stat_years": "//tbody/tr"
    }

    def __init__(
            self, type_player: str, selector: scrapy.Selector, 
            page: sync_api.Page=None):
        """attribute: selector - original selector of whole webpage of player
                      page - playwright page object with loaded webpage of  
                             a player
        """

        self.type_player = type_player
        self.selector = selector
        self.page = page
        self.season_type = None


    def _get_all_stats(self, years: list=None) -> dict:
        """wrapper method for downloading stats from both league and tournament tables
        """

        dict_stats = {}
        dict_stats["leagues"] = self._get_table_stats_wrapper(
            years=years, type_="leagues"
            )
        
        dict_stats["tournaments"] = self._get_table_stats_wrapper(
            years=years, type_="tournaments"
            )
        logger.debug(f"Stats Dict: {dict_stats}")
        assert len(dict_stats["leagues"]) > 0, 'League dictionary is empty'

        return dict_stats
    

    def _get_table_stats_wrapper(self, type_: str, years: list=None) -> dict:
        path_type = self._get_path_type(type_=type_)
        table_sel =  cf.get_single_xpath_value(
            sel=self.selector, xpath=path_type, optional=True
            )
        if type_ == "tournaments":
            print(table_sel)
        if table_sel is None:
            logger.info(
                "Table for type: %s is not present on the page of the player",
                type_
                )
            return {}
        dict_type = self._get_table_stats_wrapper_type(
            type_=type_, path_type=path_type, years=years
            )

        return dict_type
    
    
    def _get_table_stats_wrapper_type(
            type_: str, path_type: str, years: list=None) -> dict:
        pass


    def _get_path_type(self, type_: str) -> str:

        if type_ == "leagues":
            path_type = Stats.PATHS["path_league"]
        elif type_ == "tournaments":
            path_type = Stats.PATHS["path_tournament"]
    
        return path_type
    

    def get_path_years(self, path_type: str) -> str:
    
        return path_type + Stats.PATHS["stat_years"]
    

    def _merge_league_dict(self, old_dict: dict, new_dict: dict) -> dict:
        
        """merges season dictionary with new stat row dictionary - needed because sometimes player changes team in one competition over the season
        """

        new_merged_dict = old_dict.copy()
        for league in new_dict:
            if  league in old_dict:
                logger.debug(f"League: {league} is already present in"
                             "the dictionary")
                new_merged_dict[league] = {
                    **old_dict[league], **new_dict[league]
                }
                logger.debug(f"Old and new dictionary succesfully merged: "
                             f"{new_merged_dict}")
            else:
                new_merged_dict[league] = new_dict[league]
        return new_merged_dict
        
    def _get_years_list(self, path_year: str) -> list:
        """get a list of season, replaces empty strings with last 
           preceding season
        """

        list_seasons = []
        n_rows = len(cf.get_list_xpath_values(
            sel=self.selector,
            xpath=path_year,
            optional=False
        ))
        for index in range(1, n_rows + 1):
            xpath = (path_year 
                     + '[' 
                     + str(index) 
                     + ']/td[1]//text()')
            season = cf.get_single_xpath_value(
                sel=self.selector,
                xpath=xpath,
                optional=True
        )
            if season is not None:
                current_season = season
            list_seasons.append(current_season)
        return list_seasons
    
    def _get_table_stats(
            self, path_type: str, list_years: list, years: list=None) -> dict:
        
        """method for downloading data from the whole table (league, tournament) with the player season statistics
        """

        dict_stats = {}
        for ind in range(1, len(list_years) + 1):
            season = list_years[ind - 1]
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            if season not in dict_stats:
                dict_stats[season] = {}
            dict_stats[season] = self._get_season_stats_wrapper(
                season_dict=dict_stats[season], path_type=path_type, ind=ind)
            logger.debug(f"Stats Dict (Season: {season}, Type: {path_type}):" 
                        f"{dict_stats[season]}")
        return dict_stats
    
    def _get_season_stats_wrapper(
            self, season_dict: dict, path_type: str, ind: int) -> dict:
        
        new_season_dict = {}
        path_season = (path_type
                        + SkaterStats.PATHS["stats_table_l"]
                        + str(ind)
                        + SkaterStats.PATHS["stats_table_r"])
        sub_dict = self._get_season_stats(
            path_season=path_season)
        new_season_dict = self._merge_league_dict(
                old_dict=season_dict, new_dict=sub_dict)
        return new_season_dict
    
    def _get_season_stats(
            self, path_season: str) -> dict:
        """adds one row from stat table to stat dictionary"""

        row_o = self.onerow_factory(
            path_season=path_season)
        sub_dict = row_o._get_stat_dictionary()
        return sub_dict
  
    def onerow_factory(
            self, path_season: str) -> 'OneRowStat':

        if self.type_player == 'G':
            onerow_object = OneRowGoalieStat(path=path_season, 
                                             selector=self.selector,
                                             season_type=self.season_type)

        else:
            onerow_object = OneRowSkaterStat(
                path=path_season, selector=self.selector)
        return onerow_object
    

class SkaterStats(Stats):
    """class for downloading season data from stat tables on player webpage"""

    # xpaths to access statistics in league and tournament tables on player webpage

    def __init__(self, type_player: str, selector: scrapy.Selector):
        """attribute: selector - original selector of whole webpage of player
        """

        super().__init__(type_player=type_player, selector=selector)

    
    def _get_table_stats_wrapper_type(
            self, type_: str, path_type: str, years: list=None) -> dict:

        path_years = self.get_path_years(path_type=path_type)
        list_years = self._get_years_list(path_years)
        dict_stats = self._get_table_stats(path_type, list_years, years)
        logger.debug(f"Dict with stats for all season for Type: {type_} "
                    f"succesfully scraped")
        
        return dict_stats
    
        
class GoalieStats(Stats):

    TYPE = {
        'regular': 'Regular Season (Complete Stats)', 
        'play_off': 'Postseason (Complete Stats)'
        }

    PATHS = {
        "season_scroll": "//div[contains(@class,"       
                         "'PlayerStatistics_selectorWrapper')]"
                         "/div[./*[contains(@id," 
                         "'player-statistics-default-season')]]",
        "season_selection": "//div[contains(@id,'default-season-selector')]"
                            "/div",
    }

    def __init__(
            self, page: sync_api.Page, type_player: str, 
            selector: scrapy.Selector):

        super().__init__(page=page, type_player=type_player, selector=selector)

    def _get_table_stats_wrapper_type(
            self, type_: str, path_type: str, years: list=None) -> dict:
        """wrapper for selecting different types of tables for stats - 
        regual season vs play off table, which is specific for the goalies
        """

        dict_stats = {}
        path_years = self.get_path_years(path_type=path_type)
        list_years = self._get_years_list(path_years)
        for season_type in GoalieStats.TYPE:
            self._select_season_type(path_type=path_type,
                                     season_type=season_type)
            self.season_type = season_type
            dict_stats_type = self._get_table_stats(path_type, list_years, years)
            dict_stats = merge_dicts(dict_stats, dict_stats_type)


        return dict_stats
    
    def _select_season_type(self, path_type: str, season_type: str) -> None:
        button_path = (path_type 
                        + GoalieStats.PATHS['season_scroll'])
        ps.click_on_button(self.page, button_path)
        selection_path = (path_type 
                        + GoalieStats.PATHS['season_selection']
                        + "[contains(text(), '" 
                        + GoalieStats.TYPE[season_type]
                        + "')]")
        ps.click_on_button(self.page, selection_path)
        self.selector = scrapy.Selector(text=self.page.content())


class OneRowStat():

    """class containing methods for downloading data from one row of stat table
    """
    #paths to access different types of statistics in table with players's statistics

    PATHS = {
            "team": "[2]/span/a[1]/text()",
            "leadership": "[2]/span/span//text()",
            "league": "[3]/a/text()",
            "stats_regular": "[position() >= 4 and position() <= 9]//text()",
            "stats_playoff": "[position() >= 11 and position() <= 16]//text()",
            "stats_goalie": "[position() >= 4 and position() <= 12]//text()",
            "url_league": "[3]//a/@href",
            "url_team": "[2]//a/@href",
    }

    #regexes used to access team and league uid in url
    REGEX = {
        "team": "(.+)\/[^\/]+$",
        "league": "(.+)\/stats"
    }

    #value in a row, where projected statistics for a season are mentioned
    PROJECTED = "Projected"

    def __init__(self, path: str, selector: scrapy.Selector):
        """path - xpath to acces specifix row in table with statistics
           selector
           selector - original selector of webpage of player
        """
        self.path_to_row = path
        self.selector = selector
    
    def _get_stat_dictionary(self) -> dict:
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
    
    def _get_league_dict(self, league: str) -> dict:
        """method for getting league dictionary of one row of stat table"""

        league_dict = {}
        team = self._get_stat_atribute(key="team")
        if team is None or team == OneRowStat.PROJECTED:
            logger.debug(f"League dict equal to {{}} given the team name" 
                         f"is equal to None")
            return {}
        league_dict[team] = self._get_team_dict()
        league_dict[LEAGUE_URL] = self._get_league_url(league=league)
        logger.debug(f"League dict extracted: {league_dict}")
        return league_dict

    def _get_league_url(self, league: str) -> str:
        """wrapper method for getting league url"""

        if league is not None:
            league_url = self._extract_url(key_path="url_league", 
                                                   key_regex="league")
            logger.debug(f"League url extracted: {league_url}")
        else:
            league_url = None
            logger.debug(f"League url equal to {league_url}")
        return league_url
    
    def _get_team_dict(self):
        pass

    def _get_stat_atribute(
            self, key: str, keep_list: bool=False
            ) -> list|str|int:
        """method for extracting one attribute from stat row (team, league, capitancy, season stats)
        """

        path_stat = self.path_to_row + OneRowStat.PATHS[key]
        stat_list = cf.get_list_xpath_values(
            sel=self.selector,
            xpath=path_stat,
            optional=True
        )
        stat_list = [string.strip() for string in stat_list]
        if stat_list == [] or set(stat_list)=={""}:
            logger.debug(f"Attribute {key} equal to None")
            return None
        elif keep_list==True:
            logger.debug(f"Attribute {key} extracted: {stat_list}")
            return stat_list
        else:
            logger.debug(f"Attribute {key} extracted: {stat_list[0]}")
            return stat_list[0]
        
    def _extract_url(self, key_path: str, key_regex: str) -> str:
        """method for extracting url of team and league
        to which the statistics are related
        """
        
        path_url = self.path_to_row + OneRowStat.PATHS[key_path]
        url = cf.get_single_xpath_value(
            sel=self.selector, xpath=path_url, optional=False)
        logger.debug(f" General url for {key_regex}: {url}")
        return url

   
class OneRowSkaterStat(OneRowStat):
    """Child class containing methods specific to the scrapig of skaters"""


    def _get_team_dict(self) -> dict:
        """get dict with information regarding the team from one row of stat table
        """

        dict_team = {}
        stat_play_off = self._get_stat_atribute(key="stats_playoff",
                                                 keep_list=True)
        stat_regular = self._get_stat_atribute(key="stats_regular", 
                                               keep_list=True)
        leadership = self._get_stat_atribute(key="leadership")
        team_url = self._extract_url(
            key_path="url_team", 
            key_regex="team")
        dict_team[REGULAR_SEASON] = stat_regular
        dict_team[PLAY_OFF] = stat_play_off
        dict_team[LEADERSHIP] = leadership
        dict_team[TEAM_URL] = team_url
        logger.debug(f"Dict for team extracted: {dict_team}")
        return dict_team
    
    
class OneRowGoalieStat(OneRowStat):
    """Child class containing methods specific to the scrapig of goalies  rows of stats
    """

    def __init__(self, path: str, selector: scrapy.Selector, season_type: str):
        super().__init__(path=path, selector=selector)
        self.season_type = season_type
    
    def _get_team_dict(self) -> dict:
        """get dict with information regarding the team from one row of stat table
        """

        dict_team = {}
        stats = self._get_stat_atribute(key="stats_goalie", 
                                               keep_list=True)
        leadership = self._get_stat_atribute(key="leadership")
        team_url = self._extract_url(key_path="url_team", 
                                             key_regex="team")
        if self.season_type == 'regular':
            key_stats = REGULAR_SEASON
        elif self.season_type == 'play_off':
            key_stats = PLAY_OFF
        dict_team[key_stats] = stats
        dict_team[LEADERSHIP] = leadership
        dict_team[TEAM_URL] = team_url
        logger.debug(f"Dict for team extracted: {dict_team}")
        return dict_team
    

class PlayerAchievements():
    """class grouping methods for extracting achieviements of player"""

    #xpaths used to access player achievements
    PATHS = {
        "achievements_l": "//header[./h2[contains(., 'Career Highlights')]]"
                          "/following-sibling::div//table/tbody/tr[",
        "achievements_r": "][./td[1][not(text())='']]/td[2]//li/a/text()",
        "achievements_years": "//header[./h2[contains(., 'Career Highlights')]"
                              "]/following-sibling::div//table/tbody/tr[./td[1"
                              "][not(text())='']]/td[1]/text()"

    }

    def __init__(self, selector):
        """selector - original selector of webpage of player"""

        self.selector = selector

    def _get_achievements(self, years: list=None) -> dict:
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
    
    def get_season_achievements(self, ind: int) -> list:
        """method for getting list of achievements in one season"""

        path = (PlayerAchievements.PATHS["achievements_l"]
                    + str(ind)
                    + PlayerAchievements.PATHS["achievements_r"])
        awards = self.selector.xpath(path).getall()
        awards = [award.strip() for award in awards]
        return awards
    

def merge_dicts(dict_a, dict_b):
    """method for merging two nested dicts with the same keys"""

    for key, value in dict_b.items():
        if key in dict_a:
            # If both values are dictionaries, merge them recursively
            if isinstance(dict_a[key], dict) and isinstance(value, dict):
                merge_dicts(dict_a[key], value)
            # If they are not dictionaries, overwrite the value in dict_a
            else:
                dict_a[key] = value
        else:
            # If the key does not exist in dict_a, add it from dict_b
            dict_a[key] = value
    return dict_a


