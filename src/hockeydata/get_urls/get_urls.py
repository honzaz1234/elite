import json
import re 
import scrapy
import time

import common_functions as cf 
import hockeydata.playwright_setup.playwright_setup as ps

from constants import *
from decorators import time_execution
from logger.logging_config import logger


with open("leagues.json") as f:
    LEAGUE_URLS = json.load(f)


class LeagueUrlDownload():

    SLEEP = 120
    WAIT_LEAGUE_PAGE = (
        "//ul[preceding-sibling::header[./h2[contains(text(),"
        "'Champions')]]]/li[last()]/a[1]"
    )
        
    PATHS = {
        "league": "/league",
        "all_leagues": "/leagues",
            "stats": "/stats",
        "league_names_ref": "//div[preceding-sibling::header[contains(@id, '-men')]]//a[@class='TextLink_link__3JbdQ TableBody_link__MNtRl']/@href",
        "league_name": "//div[preceding-sibling::header[contains(@id, '-men')]]//a[@class='TextLink_link__3JbdQ TableBody_link__MNtRl']/text()",
        "season_refs": "//a[@style='font-weight: 800;']/@href",
        "standings": "/standings/",
        "year_list": "//ul[preceding-sibling::header[./h2[contains(text()"
                     ", 'Champions')]]]/li/a[1]/@href",
        "last_year": "//ul[preceding-sibling::header[./h2[contains(text()"
                      ",'Champions')]]]/li[1]/a[1]/text()",
        "first_year": "//ul[preceding-sibling::header[./h2[contains(text()"
                      ",'Champions')]]]/li[last()]/a[1]/text()"
    }


    def __init__(self, page=None):
         self.page = page
         pass
        
    def get_league_names_dict(self) -> dict:

        """method that creates dictionary, where keys are leagues that can be found on the elite prospects website
        and values are their respective urls"""

        dict_leagues = {}
        path_all_leagues = ELITE_URL + LeagueUrlDownload.PATHS["all_leagues"]
        html_leagues = cf.get_valid_request(path_all_leagues, return_type="content")
        leagues_sel = scrapy.Selector(text=html_leagues)
        leagues_ref = cf.get_list_xpath_values(
            sel=leagues_sel, 
            xpath=self.PATHS["league_names_ref"], 
            optional=False)
        leagues_names =  cf.get_list_xpath_values(
            sel=leagues_sel, 
            xpath=self.PATHS["league_name"], 
            optional=False)
        for ind in range(len(leagues_ref)):
            dict_leagues[leagues_names[ind]] = leagues_ref[ind]
        return dict_leagues
    
    def create_season_string(self, year: str, preceeding: bool=True) -> list:

        """creates season from year
            2011 => 2011-2012 etc."""
        
        if preceeding == True:
            year_plus = int(year) + 1
            season_string = str(year) + "-" +  str(year_plus)
        else:
            year_minus = int(year) - 1
            season_string = str(year_minus) + "-" + str(year)
        return season_string
    
    def create_season_list(self, min: int, max: int) -> list:
         """create list of season strings"""

         range_years = [*range(min, max, 1)]
         list_seasons = []
         for year in range_years:
            season1 = self.create_season_string(year)
            list_seasons.append(season1)
         return list_seasons
    

    def get_player_refs(
            self, league_uid: str, url_dict: dict={}, seasons: list=[]) -> dict:
        """downloads player urls based on league and list of  years
            output: dictionary: season -> (players-goalies) -> urls
        """
        if "season_range" not in url_dict[league_uid]:
            self._add_season_range(
                league_uid=league_uid, url_dict=url_dict
                )
        season_range = url_dict[league_uid]["season_range"]
        all_years = range(season_range['start'], season_range['finish'] + 1)
        seasons_to_get = self.create_list_of_seasons(years=all_years)
        if seasons != []:
            seasons_to_get = [
                season for season in seasons_to_get if season in seasons
                ]
        seasons_to_download = [
            season for season in seasons_to_get 
            if season not in url_dict[league_uid]
            ]
        if seasons_to_download == []:
            logger.info("All required seasons are already downloaded.")

            return
        logger.info("Urls for players from league %s for seasons %s "
                    "are not yet in the dict and will be downloaded now.",
                        league_uid, seasons_to_download
                        )
        dict_player_ref = self.get_player_urls(
            list_seasons=seasons_to_download, league=league_uid
            )
        logger.info("Urls for players from league %s for seasons %s "
                    "were succesfully downloaded.",
                        league_uid, seasons_to_download
                        )
        
        
        return dict_player_ref
    

    def _add_season_range(self, league_uid: str, url_dict: dict) -> None:
        url = ELITE_URL + LEAGUE_URLS[league_uid]
        list_seasons = self.get_list_of_years(url=url)
        season_range = {
            'start': int(list_seasons[0]),
            'finish': int(list_seasons[-1])
            }
        url_dict[league_uid]["season_range"] = season_range

        
    def create_list_of_seasons(self, years: list) -> list:
        season_list = []
        for year in years:
            season_string = self.create_season_string(year)
            season_list.append(season_string)

        return season_list
    
    
    def get_list_of_years(self, url: str) -> list:
        
        block_check = True
        while block_check is not None:
                ps.go_to_page_wait_selector(
                    page=self.page, 
                    url=url, 
                    sel_wait=self.WAIT_LEAGUE_PAGE
                              )
                sel_league = scrapy.Selector(text=self.page.content())
                block_check = cf.get_single_xpath_value(
                    sel=sel_league, xpath=BLOCK_SELECTOR, optional=True
                    )
                if block_check is not None:
                    logger.info("Limit for pages scraped achieved. Timeout"
                                " will follow...")
                    time.sleep(LeagueUrlDownload.SLEEP)
        first_year = int((sel_league
                    .xpath(LeagueUrlDownload.PATHS["first_year"])
                    .getall()[0])) - 1
        last_year = int((sel_league
            .xpath(LeagueUrlDownload.PATHS["last_year"])
            .getall()[0]))
        years = [year for year in range(first_year, last_year)]

        return years


    @time_execution
    def get_player_urls(self, list_seasons: list, league: str) -> dict:
        logger.info(f"Process of obtaining player urls for league"
                    f" {league} started")
        dict_player_ref = {}
        season_getter = SeasonUrlDownload()
        for season in list_seasons:
            season_dict = False
            while season_dict == False:
                season_dict = season_getter.get_player_season_refs_wraper(
                    league=league,
                    season=season)
                if season_dict == False:
                    logger.info("Limit for pages scraped achieved. Timeout"
                                " will follow...")
                    time.sleep(LeagueUrlDownload.SLEEP)
            dict_player_ref[season] = season_dict
        logger.info(f"Process of obtaining player urls for league"
                    f" {league} finished")
        logger.info(f"By scraping, {len(dict_player_ref)} seasons of player"
                    " urls were obtained")
        return dict_player_ref

    @time_execution
    def get_team_refs(self, league: str) -> list:
        """downloads references to team pages based on the league selected"""

        logger.info(f"Process of obtaining team urls for league"
                    f" {league} started")
        league_team_refs = []
        season_getter = SeasonUrlDownload()
        league_url = ELITE_URL + LEAGUE_URLS[league]
        self.page.goto(league_url)
        sel_league = scrapy.Selector(text=self.page.content())
        season_ref_list = (sel_league
                       .xpath(LeagueUrlDownload.PATHS["year_list"])
                       .getall())
        season_ref_list = [season.strip() for season in season_ref_list]
        for season_ref in season_ref_list:
            season_refs = season_getter.get_team_season_refs(
                season_ref=season_ref, 
                ref_list=league_team_refs)
            season_refs = [value for value in season_refs if type(value) == str]
            if season_refs != []:
                league_team_refs = league_team_refs + season_refs
                league_team_refs = list(set(league_team_refs))
        logger.info(f"Process of obtaining team urls for league"
                    f" {league} finished")
        logger.info(f"By scraping, {len(league_team_refs)} seasons of team"
                    " urls were obtained")
        return league_team_refs


class SeasonUrlDownload():

    #xpaths used in the process of downloading players and team's urls  

    PATHS = {
        "player_ref": "//table[@id='export-skater-stats-table']"
                      "//td[@class='player']/span[@class='txt-blue']/a/@href",
        "goalie_ref": "//table[@id='export-goalie-stats-table']//td"
                      "[@class='player']/span[@class='txt-blue']/a/@href",
        "last_page": "//a[contains(text(),'Last page')]/@href",
        "team_url": "//td[@class='team']//@href",
        "stats": "/stats",
        "page_goalie": "?sort-goalie-stats=svp&page-goalie="
    }
    
    GOALIES_REG = "[0-9]+#goalies$"
    GOALIES_REG_MATCH = "([0-9]+)#goalies$"
    TIMEOUT = 120

    def __init__(self):
        pass

    def get_player_season_refs_wraper(self, league: str, season: str) -> dict:
        """downloads urls of player profiles for one season of one league from the webpage with statistics
            output dictionary: (players-goalies) -> urls"""
        
        logger.info(f"Scraping player's urls for league {league} and season"
                    f" {season} started. ")
        stats_path = (
            ELITE_URL
            + LEAGUE_URLS[league] 
            + SeasonUrlDownload.PATHS["stats"] 
            + "/" 
            + season
            )
        dict_season = {}
        page_html = cf.get_valid_request(stats_path, return_type="content")
        selector_players = scrapy.Selector(text=page_html)
        block_check = cf.get_single_xpath_value(
            sel=selector_players, xpath=BLOCK_SELECTOR, optional=True
            )
        if block_check is not None:
            return False
        dict_season = self.get_player_season_refs(selector=selector_players,
                                                  stats_path=stats_path)
        logger.info(f"Scraping player's urls for league {league} and season"
                    f" {season} finished. ")
        logger.info(f" {len(dict_season['goalies'])} urls for"
                    f" goalies and {len(dict_season['players'])} urls for"
                    f" skaters were scrapped")
        
        return dict_season
    
    def get_player_season_refs(
            self, selector: scrapy.Selector, 
            stats_path: str) -> dict:
            """downloads urls of player profiles for one season of one league from the webpage with statistics
                output dictionary: (players-goalies) -> urls"""
            
            dict_season = {}
            ref_last_page = cf.get_list_xpath_values(
                sel=selector, xpath=self.PATHS["last_page"],
                optional=True
                )
            dict_season["goalies"] = self.get_goalies_season_refs(
                ref_last_page=ref_last_page,
                stats_path=stats_path
            )
            dict_season["players"] = self.get_skaters_season_refs(
                ref_last_page=ref_last_page,
                stats_path=stats_path
            )
            return dict_season
    
    def get_skaters_season_refs(
            self, ref_last_page: list, stats_path: str) -> list:
        
        sublist_players = []
        number_of_pages_players = [re.findall(
                "([0-9]+)$", string) for string in ref_last_page if re.search("[0-9]+$", string)]
        if number_of_pages_players == []:
            number_of_pages_players = 1
        else:
            number_of_pages_players = number_of_pages_players[0][0]
        for index in range(1, int(number_of_pages_players) + 1):
            player_refs = False
            while player_refs==False:
                player_refs = self._page_player(stats_path, index)
                if player_refs == False:
                    logger.info("Page blocked, timeout will ensue")
                    time.sleep(SeasonUrlDownload.TIMEOUT)
            sublist_players = sublist_players + player_refs        
        return sublist_players
    
    def get_goalies_season_refs(
            self, ref_last_page: list, stats_path: str) -> list:
        
        sublist_goalies = []
        number_of_pages_goalies = [re.findall(
            SeasonUrlDownload.GOALIES_REG_MATCH, string)
            for string in ref_last_page if re.search(
                SeasonUrlDownload.GOALIES_REG, string)]
        if number_of_pages_goalies == []:
            number_of_pages_goalies = 1
        else:
            number_of_pages_goalies = number_of_pages_goalies[0][0]
        for index in range(1, int(number_of_pages_goalies) + 1):
            goalies_refs = False
            while goalies_refs==False:
                goalies_refs = self._page_goalie(stats_path, index)
                if goalies_refs == False:
                    logger.info('Page blocked, timeout will ensue')
                    time.sleep(SeasonUrlDownload.TIMEOUT)    
            sublist_goalies = sublist_goalies + goalies_refs
        return sublist_goalies
    
    def _page_player(self, path: str, index: int) -> list:
        """downloads urls of player profiles from 1 page of seasonal statistic board"""

        subpage_path = path + "?page=" + str(index)
        subpage_html = cf.get_valid_request(subpage_path, return_type="content")
        selector_subpage = scrapy.Selector(text=subpage_html)
        block_check = cf.get_single_xpath_value(
            sel=selector_subpage, xpath=BLOCK_SELECTOR, optional=True
            )
        if block_check is not None:
            return False
        player_refs =  cf.get_list_xpath_values(
            sel=selector_subpage, 
            xpath=self.PATHS["player_ref"],
            optional=False)
        return player_refs

    def _page_goalie(self, path: str, index: int) -> list:
        """downloads urls of goalie profiles from 1 page of seasonal statistic board"""

        subpage_path = (path 
                        + SeasonUrlDownload.PATHS["page_goalie"] 
                        + str(index))
        subpage_html = cf.get_valid_request(subpage_path, return_type="content")
        selector_subpage = scrapy.Selector(text=subpage_html)
        block_check = cf.get_single_xpath_value(
            sel=selector_subpage, xpath=BLOCK_SELECTOR, optional=True
            )
        if block_check is not None:
            return False
        goalies_refs = cf.get_list_xpath_values(
            sel=selector_subpage, 
            xpath=self.PATHS["goalie_ref"],
            optional=False)
        return goalies_refs

    def get_team_season_refs(
            self, season_ref: str, ref_list: list=[]
            ) -> list:
        """downloads team's urls for one  season"""
                
        logger.info(f"Scraping team's urls for url season {season_ref}"
                    " started")
        url_season = (ELITE_URL 
                      + season_ref)
        season_html = cf.get_valid_request(url_season, return_type="content")
        sel_season = scrapy.Selector(text=season_html)
        team_refs = cf.get_list_xpath_values(
            sel=sel_season, 
            xpath=self.PATHS["team_url"],
            optional=False)
        for team_ref in team_refs:
            team_ref_wo_season = re.findall(
                "(.+)\/[0-9]{4}\-[0-9]{4}$", team_ref)
            if team_ref_wo_season == []:
                team_ref_wo_season = team_ref
            else:
                team_ref_wo_season = team_ref_wo_season[0]
            ref_list.append(team_ref_wo_season)
        logger.info(f"Scraping team's urls for url season {season_ref}"
                    f" finished")
        logger.debug(f"{len(ref_list)} downloaded for {season_ref}")
        return ref_list