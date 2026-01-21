import re

from scrapy import Selector

import hockeydata.common_functions as cf

from hockeydata.constants import *
from hockeydata.decorators import time_execution
from hockeydata.logger.logging_config import logger

    
class PlayerParser:
    """Class for parsing information from players htmls obtained by player 
       scraper;
       includes one method which wraps around methods from classes for downloading 
       individual subparts of player web page:
       a) general info (name, position, age...)
       b) player  season stats 
       c) player achievements 
    """

    
    def __init__(self, scraped_data: dict,  player_uid: int):
        """Arguments:
        scraped_data - dict with htmls obtained in previous step
        parsed_data - dict with resulting parsed data
        """

        self.scraped_data = scraped_data
        self.player_uid = player_uid
        self.parsed_data = dict.fromkeys(
            (PLAYER_FACTS, ACHIEVEMENTS, SEASON_STATS), {}
            )


    def get_info_all(self, years: list=None) -> dict:
        """Arguments: years - list of years for which data is parsed"""
        logger.info(
            'Parsing of new player info %s started', 
            self.player_uid
            )
        self._parse_player_facts()
        self._parse_achievements(years=years)
        self._parse_stats(years=years)

        return self.parsed_data


    def _parse_player_facts(self) -> None:
        facts_o = PlayerFactsParser(
            facts_html=self.scraped_data[PLAYER_FACTS],
            player_uid=self.player_uid
            )
        self.parsed_data[PLAYER_FACTS] = facts_o.parse_data()


    def _parse_achievements(self, years: list) -> None:
        """
        Arguments: 
        years - list of years for which the achievements should be scraped
        """

        achiev_o = AchievementsParser(
            acheivements_html=self.scraped_data[ACHIEVEMENTS]
            )
        
        self.parsed_data[ACHIEVEMENTS] = achiev_o.parse_data(years=years)


    def _parse_stats(self, years: list) -> None:
        """
        Arguments: 
        years - list of years for which the achievements should be scraped
        """
        
        stats_o = self.stats_factory()
        self.parsed_data[SEASON_STATS] = stats_o.parse_data(
            years=years
            )
    

    def stats_factory(self) -> type['StatsParser']:
        """given that attaining stats for goalies and players differ
        they are divided into separate classes
        """

        if GOALIE_PLAYER in self.parsed_data['player_facts'][POSITION]:
            stats_object = GoalieStatsParser(
                type_player=GOALIE_PLAYER,
                stats_dict=self.scraped_data['stats']
                )
        else:
            stats_object = SkaterStatsParser(
                type_player=OTHER_PLAYER,
                stats_dict=self.scraped_data['stats']
                )
            
        return stats_object


class PlayerFactsParser():
    

    #list of xpaths that are used to access information on player

    PATHS = {
        "player_name": "//header[contains(@class, 'LineupCard_header')]"
                        "/h2/text()[1]",
        "gi_left": "//section[@id='player-facts']//dt"
                     "[normalize-space(text())='",
        "gi_right": "']/following-sibling::"
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
    
    def __init__(self, facts_html: bytes, player_uid: int):
        """attribute: facts_html - part of the page html with player facts data
        """

        self.selector = Selector(text=facts_html.decode("utf-8"))
        self.player_uid = player_uid


    def parse_data(self) -> dict:
        """wrapper method for attaining all available info on player"""
        parsed_data = self._get_info_wrapper()
        parsed_data[PLAYER_NAME] = self._get_name()
        parsed_data[PLAYER_UID] = self.player_uid

        return parsed_data


    def _get_name(self) -> str:
        """method for attaining player's name"""

        name = (self.selector
                .xpath(self.PATHS["player_name"])
                .getall())
        name = [string.strip() for string in name if string != ""]

        return name[0].strip()


    def _get_info_wrapper(self) -> dict:
        """wrapper method for downloading all general info from facts table"""

        dict_gi = {}
        for info_name in self.INFO_NAMES:
            keep_list = False
            key_name = self.PROJECT_MAPPING[info_name][0]
            if info_name in self.KEEP_LIST:
                keep_list = True
            dict_gi[key_name] = self._get_info(info_name=info_name,
                                                keep_list=keep_list)
        return dict_gi


    def _get_info(self, info_name: str, keep_list: bool) -> int|str|list:
        """method for getting one value from general info table on player's webpage
        """

        info_path_val = (self.PATHS["gi_left"]
                         + info_name
                         + self.PATHS["gi_right"]
                         + "dd//text()")
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


    def __init__(self, selector: Selector):
        """selector - original selector
           relations_regex - regex for extracting relation types from  
                             text on webpage
           relation_url_regex - regex for extracting url of relations 
        """
        
        self.selector = selector
        self.relations_regex = ("("
                                 + self.RELATION_REGEX
                                 + ")"
                                 + ":")
        self.relation_url_regex = ":(.+)(:|$)"


    def _get_individual_relations(self) -> dict:
        """creates dictionary in which the keys are the relations that exist for the player and values are the html code in which uids of these relations can be found
        """

        text = (self.selector
                .xpath(self.PATHS["whole_text"])
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
        logger.debug("Relation Dict: %s", relations_uid)

        return relations_uid


class StatsParser():
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
            self, type_player: str, stats_dict: dict):

        self.type_player = type_player
        self.stats_dict = stats_dict
        self.default_selector = None


    def get_selectors(self) -> None:
        pass


    def parse_data(self, years: list=None) -> dict:
        """wrapper method for downloading stats from both league and tournament tables
        """

        dict_stats = {}
        dict_stats["league"] = self._get_table_stats_wrapper(
            years=years, table_type="league"
            )
        
        dict_stats["tournament"] = self._get_table_stats_wrapper(
            years=years, table_type="tournament"
            )
        logger.debug("Stats Dict: %s", dict_stats)

        return dict_stats
    

    def _get_table_stats_wrapper(
            self, table_type: str, years: list=None) -> dict:
        is_empty = all(
           subdict is None for subdict in self.sel_dict[table_type].values()
            )
        if is_empty:
            logger.info(
                "Table for type: %s is not available in the storage DB",
                table_type
                )
            return {}
        dict_type = self._get_table_stats_wrapper_type(
            years=years, 
            table_type=table_type
            )

        return dict_type
    
    
    def _get_table_stats_wrapper_type(
            self, table_type: str, years: list=None) -> dict:
        
        list_years = self._get_years_list(self.PATHS["stat_years"])
        dict_stats = self._get_table_stats(
            list_years=list_years, 
            years=years, 
            table_type=table_type
            )
        logger.debug(
            "Dict with stats for all season for Type: %s "
            "succesfully scraped"
            )
        
        return dict_stats
    

    def _merge_league_dict(self, old_dict: dict, new_dict: dict) -> dict:
        
        """merges season dictionary with new stat row dictionary - needed because sometimes player changes team in one competition over the season
        """

        new_merged_dict = old_dict.copy()
        for league in new_dict:
            if  league in old_dict:
                logger.debug(
                    "League: %s is already present in the dictionary",
                    league
                    )
                new_merged_dict[league] = {
                    **old_dict[league], **new_dict[league]
                }
                logger.debug(
                    "Old and new dictionary succesfully merged: %s",
                    new_merged_dict
                    )
            else:
                new_merged_dict[league] = new_dict[league]

        return new_merged_dict
        

    def _get_years_list(self, path_year: str) -> list:
        """get a list of season, replaces empty strings with last 
           preceding season
        """

        list_seasons = []
        n_rows = len(
            cf.get_list_xpath_values(
                sel=self.default_selector,
                xpath=path_year,
                optional=False
                )
            )
        for index in range(1, n_rows + 1):
            xpath = (path_year 
                     + '[' 
                     + str(index) 
                     + ']/td[1]//text()')
            season = cf.get_single_xpath_value(
                sel=self.default_selector,
                xpath=xpath,
                optional=True
        )
            if season is not None:
                current_season = season
            list_seasons.append(current_season)

        return list_seasons
    

    def _get_table_stats(
            self, list_years: list, table_type: str, years: list=None) -> dict:
        
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
                season_dict=dict_stats[season], ind=ind, table_type=table_type)
            logger.debug("Stats Dict (Season: %s, Type: %s): %s" 
                        f"{dict_stats[season]}", season, table_type,
                        dict_stats[season]
                        )
            
        return dict_stats
    
    
    def _get_season_stats_wrapper(self, season_dict: dict, ind: int, table_type: str) -> dict:
        
        new_season_dict = {}
        sub_dict = self._get_season_stats(ind=ind, table_type=table_type)
        new_season_dict = self._merge_league_dict(
                old_dict=season_dict, new_dict=sub_dict)
        
        return new_season_dict
    
    
    def _get_season_stats(self, ind: int, table_type: str) -> dict:
        """adds one row from stat table to stat dictionary"""

        row_o = self.onerow_factory(
            ind=ind, table_type=table_type)
        sub_dict = row_o._get_stat_dictionary()

        return sub_dict
    
  
    def onerow_factory(
            self, ind: int, table_type: str
            ) -> 'OneRowStat':

        if self.type_player == 'G':
            onerow_object = OneRowGoalieStat(
                ind=ind, 
                selectors=self.sel_dict[table_type]
                )

        else:
            onerow_object = OneRowSkaterStat(
                ind=ind, 
                selector=self.sel_dict[table_type]
                )
            
        return onerow_object
    

class SkaterStatsParser(StatsParser):


    def __init__(self, type_player: str, stats_dict: dict):
        super().__init__(type_player=type_player, stats_dict=stats_dict)
        self.sel_dict = {
            "league": None,
            "tournament": None
        }
        self.get_selectors()


    def get_selectors(self) -> None:
        for competition_type in self.stats_dict:
            self.sel_dict[competition_type] = Selector(
                text=self.stats_dict[competition_type]
                )
        self.default_selector = self.sel_dict["league"]


class GoalieStatsParser(StatsParser):


    def __init__(self, type_player: str, stats_dict: dict):
        super().__init__(type_player=type_player, stats_dict=stats_dict)
        self.sel_dict = {
            "league": {
                "regular": None,
                "play_off": None
            },
            "tournament": {
                "regular": None,
                "play_off": None
            },
        }
        self.get_selectors()


    def get_selectors(self) -> None:
        for competition_type in self.stats_dict:
            for season_type in self.stats_dict[competition_type]:
                if not self.stats_dict[competition_type][season_type]:
                    continue
                self.sel_dict[competition_type][season_type] = Selector(
                    text=self.stats_dict[competition_type][season_type]
                    )
        self.default_selector = self.sel_dict["league"]["regular"]


class OneRowStat():


    """class containing methods for downloading data from one row of stat table
    """
    #paths to access different types of statistics in table with players's statistics


    PATHS = None


    #regexes used to access team and league uid in url
    REGEX = {
        "team": "(.+)\/[^\/]+$",
        "league": "(.+)\/stats"
    }

    #value in a row, where projected statistics for a season are mentioned
    PROJECTED = "Projected"

    def __init__(self, ind: int):

        self.path_to_row = (
            self.PATHS["stats_table_l"] + str(ind) + self.PATHS["stats_table_r"]
        )
    

    def _get_stat_dictionary(self) -> dict:
        """method for getting stat dictionary of one row of stat table"""

        dict_stat = {}
        league = self._get_stat_atribute_wrapper(
            xpath_key="league", 
            keep_list=False
            )
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
        team = self._get_stat_atribute_wrapper(
            xpath_key="team", 
            keep_list=False
            )
        if team is None or team == OneRowStat.PROJECTED:
            logger.debug(
                "League dict equal to %s given the team name " 
                "is equal to None", {}
                )
            return {}
        league_dict[team] = self._get_team_dict()
        league_dict[LEAGUE_URL] = self._get_league_url(league=league)

        return league_dict
    

    def _get_team_dict(self) -> dict:
        """get dict with information regarding the team from one row of stat table
        """

        dict_team = {}
        regular_stats, play_off_stats = self.get_stats()
        leadership = self._get_stat_atribute_wrapper(
            xpath_key="leadership", 
            keep_list=False
            )
        team_url = self._get_stat_atribute_wrapper(
            xpath_key="url_team", 
            keep_list=False, 
            optional=False
            )
        dict_team[REGULAR_SEASON] = regular_stats
        dict_team[PLAY_OFF] = play_off_stats
        dict_team[LEADERSHIP] = leadership
        dict_team[TEAM_URL] = team_url

        return dict_team
    

    def get_stats(self) -> tuple:

        pass


    def _get_league_url(self, league: str) -> str:
        """wrapper method for getting league url"""

        if league is not None:
            league_url = self._get_stat_atribute_wrapper(
            xpath_key="url_league", 
            keep_list=False, 
            optional=False
            )
            logger.debug(f"League url extracted: {league_url}")
        else:
            league_url = None
            logger.debug(f"League url equal to {league_url}")
        return league_url


    def _get_stat_atribute(
            self, xpath_key: str, sel: Selector, keep_list: bool=False,
            optional: bool=True) -> list|str|int:
        """method for extracting one attribute from stat row (team, league, capitancy, season stats)
        """

        path_stat = self.path_to_row + self.PATHS[xpath_key]
        stat_list = cf.get_list_xpath_values(
            sel=sel,
            xpath=path_stat,
            optional=optional
        )
        stat_list = [string.strip() for string in stat_list]
        if stat_list == [] or set(stat_list)=={""}:

            return None
        elif keep_list==True:

            return stat_list
        else:

            return stat_list[0]
    

    def _get_stat_atribute_wrapper(
            self, xpath_key: str, keep_list: bool=False, sel_key: str=None, 
            optional: bool=True
            ) -> list|str|int:
        """wrapper for method for extracting one attribute from stat row (team, league, capitancy, season stats)
            needed because structure of selectors differs between skaters and goalies
        """

        pass

   
class OneRowSkaterStat(OneRowStat):
    """Child class containing methods specific to the scraping of skaters"""
    

    PATHS = {
            "team": "[2]/span/a[1]/text()",
            "leadership": "[2]/span/span//text()",
            "league": "[3]/a/text()",
            "stats_regular": "[position() >= 4 and position() <= 9]//text()",
            "stats_playoff": "[position() >= 11 and position() <= 16]//text()",
            "stats_table_l": "//tbody//tr[",
            "stats_table_r": "]/td",
            "url_league": "[3]/a/@href",
            "url_team": "[2]/span/a/@href",
    }


    def __init__(self, ind: int, selector: Selector):
        super().__init__(ind=ind)
        self.selector = selector


    def get_stats(self) -> tuple:

        play_off_stats = self._get_stat_atribute_wrapper(
            xpath_key="stats_playoff", 
            keep_list=True
            )
        regular_stats = self._get_stat_atribute_wrapper(
            xpath_key="stats_regular", 
            keep_list=True
            )

        return regular_stats, play_off_stats
    

    def _get_stat_atribute_wrapper(
            self, xpath_key: str,  keep_list: bool=False, optional: bool=True
            ) -> list|str|int:
        """wrapper for method for extracting one attribute from stat row (team, league, capitancy, season stats)
        """

        stat = self._get_stat_atribute(
            xpath_key=xpath_key, 
            sel=self.selector, 
            keep_list=keep_list, 
            optional=optional
            )

        return stat
    

class OneRowGoalieStat(OneRowStat):
    """Child class containing methods specific to the scraping of goalie rows of stats
    """


    PATHS = {
            "team": "[2]/span/a[1]/text()",
            "leadership": "[2]/span/span//text()",
            "league": "[3]/a/text()",
            "stats_regular": "[position() >= 4 and position() <= 12]//text()",
            "stats_playoff": "[position() >= 4 and position() <= 12]//text()",
            "stats_table_l": "//tbody//tr[",
            "stats_table_r": "]/td",
            "url_league": "[3]/a/@href",
            "url_team": "[2]/span/a/@href",
    }


    def __init__(self, ind: int, selectors: dict):
        super().__init__(ind=ind)
        self.selectors = selectors
        self.default_selector = selectors['regular']


    def get_stats(self) -> tuple:

        play_off_stats = self._get_stat_atribute_wrapper(
            xpath_key="stats_playoff", 
            keep_list=True, 
            sel_key="play_off"
            )
        regular_stats = self._get_stat_atribute_wrapper(
            xpath_key="stats_regular", 
            keep_list=True, 
            sel_key="regular"
            )

        return regular_stats, play_off_stats
    

    def _get_stat_atribute_wrapper(
            self, xpath_key: str, keep_list: bool=False, sel_key: str=None,
            optional: bool=True
            ) -> list|str|int:
        """wrapper for method for extracting one attribute from stat row (team, league, capitancy, season stats)
        """

        if sel_key is None:
            sel = self.default_selector
        else:
            sel = self.selectors[sel_key]
        stat = self._get_stat_atribute(
            xpath_key=xpath_key, 
            sel=sel, 
            keep_list=keep_list, 
            optional=optional
            )

        return stat
    

class AchievementsParser():
    """class grouping methods for extracting achieviements of player"""

    #xpaths used to access player achievements
    PATHS = {
        "achievements": "//section[@id='career-highlights']",
        "achievements_l": "//header[./h2[contains(., 'Career Highlights')]]"
                          "/following-sibling::div//table/tbody/tr[",
        "achievements_r": "][./td[1][not(text())='']]/td[2]//li/a/text()",
        "achievements_years": "//header[./h2[contains(., 'Career Highlights')]"
                              "]/following-sibling::div//table/tbody/tr[./td[1"
                              "][not(text())='']]/td[1]/text()"

    }

    def __init__(
            self, acheivements_html: bytes):
        """selector - original selector of webpage of player"""
        self.selector = Selector(text=acheivements_html.decode(encoding="utf-8"))


    def parse_data(self, years: list=None) -> dict:
        """method for downloading achievements of player into dictionary"""
        dict_achiev = {}
        list_years = self.selector.xpath(
            AchievementsParser.PATHS["achievements_years"]).getall()
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

        path = (AchievementsParser.PATHS["achievements_l"]
                    + str(ind)
                    + AchievementsParser.PATHS["achievements_r"])
        awards = self.selector.xpath(path).getall()
        awards = [award.strip() for award in awards]
        return awards
    


