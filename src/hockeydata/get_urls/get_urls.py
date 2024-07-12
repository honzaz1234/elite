import re 
import requests
import scrapy
from datetime import datetime, timedelta
from hockeydata.constants import *


class LeagueUrlDownload():
        
    PATHS = {
        "league": "/league",
        "all_leagues": "/leagues",
            "stats": "/stats",
        "league_names_ref": "//div[preceding-sibling::header[contains(@id, '-men')]]//a[@class='TextLink_link__3JbdQ TableBody_link__MNtRl']/@href",
        "league_name": "//div[preceding-sibling::header[contains(@id, '-men')]]//a[@class='TextLink_link__3JbdQ TableBody_link__MNtRl']/text()",
        "season_refs": "//a[@style='font-weight: 800;']/@href",
        "standings": "/standings/",
        "year_list": "//div[@id='standings']//option[position()>1]/text()",
        "last_year": "//ul[preceding-sibling::h4[contains(text(), 'List of "
                      "Champions')]]/li[1]/a[1]/text()",
        "first_year": "//ul[preceding-sibling::h4[contains(text(), 'List of "
                      "Champions')]]/li[last()]/a[1]/text()"
    }
    
    def __init__(self):
         pass
        
    def get_league_names_dict(self) -> dict:

        """method that creates dictionary, where keys are leagues that can be found on the elite prospects website
        and values are their respective urls"""

        dict_leagues = {}
        path_all_leagues = ELITE_URL + LeagueUrlDownload.PATHS["all_leagues"]
        html_leagues = requests.get(path_all_leagues).content
        leagues_sel = scrapy.Selector(text=html_leagues)
        leagues_ref = leagues_sel.xpath(LeagueUrlDownload.PATHS["league_names_ref"]).getall()
        leagues_names = leagues_sel.xpath(LeagueUrlDownload.PATHS["league_name"]).getall()
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
    
    def get_player_refs(self, league: str, years: list) -> dict:
        """downloads player urls based on league and list of  years
            output: dictionary: season -> (players-goalies) -> urls
        """
        if years == None:
            url = ELITE_URL + LEAGUE_URLS[league]
            league_page_html = requests.get(url).content
            sel_league = scrapy.Selector(text=league_page_html)
            first_year = int((sel_league
                        .xpath(LeagueUrlDownload.PATHS["first_year"])
                        .getall()[0])) - 1
            last_year = int((sel_league
            .xpath(LeagueUrlDownload.PATHS["last_year"])
            .getall()[0]))
            years = [year for year in range(first_year, last_year)]
        elif years == []:
                return
        list_seasons = []
        dict_player_ref = {}
        for year in years:
            season_string = self.create_season_string(year)
            list_seasons.append(season_string)
        print(list_seasons)
        season_getter = SeasonUrlDownload()
        for season in list_seasons:
            season_dict = season_getter.get_player_season_refs(league=league,
                                                                season=season)
            if season_dict != {"goalies": [], "players": []}:
                dict_player_ref[season] = season_dict
        return dict_player_ref
    
    def get_team_refs(self, league: str) -> list:
        """downloads references to team pages based on the league selected"""

        league_team_refs = []
        season_getter = SeasonUrlDownload()
        league_path = ELITE_URL + LEAGUE_URLS[league]
        league_page_html = requests.get(league_path).content
        sel_league = scrapy.Selector(text=league_page_html)
        season_list = (sel_league
                       .xpath(LeagueUrlDownload.PATHS["year_list"])
                       .getall())
        season_list = [season.strip() for season in season_list]
        for season in season_list:
            season_refs = season_getter.get_team_season_refs(
                season=season, league=league, ref_list=league_team_refs)
            season_refs = [value for value in season_refs if type(value) == str]
            if season_refs != []:
                league_team_refs = league_team_refs + season_refs
                league_team_refs = list(set(league_team_refs))
        return league_team_refs


class SeasonUrlDownload():

    #xpaths used in the process of downloading players and team's urls  

    PATHS = {
        "player_ref": "//table[@id='export-skater-stats-table']"
                      "//td[@class='player']//a/@href",
        "goalie_ref": "//table[@id='export-goalie-stats-table']//td"
                      "[@class='player']//a/@href",
        "last_page_players": "//span[@class = 'hidden-xs']/a/@href",
        "last_page_goalies": "//span[@class = 'hidden-xs']/a/@href",
        "team_url": "//td[@class='team']//@href",
        "stats": "/stats",
        "page_goalie": "?sort-goalie-stats=svp&page-goalie="
    }
    
    GOALIES_REG = "[0-9]+#goalies$"
    GOALIES_REG_MATCH = "([0-9]+)#goalies$"

    def __init__(self):
        pass

    def _page_player(self, path: str, index: int) -> list:
        """downloads urls of player profiles from 1 page of seasonal statistic board"""

        subpage_path = path + "?page=" + str(index)
        subpage_html = requests.get(subpage_path).content
        selector_subpage = scrapy.Selector(text=subpage_html)
        player_refs = selector_subpage.xpath(
            SeasonUrlDownload.PATHS["player_ref"]).getall()
        return player_refs

    def _page_goalie(self, path: str, index: int) -> list:
        """downloads urls of goalie profiles from 1 page of seasonal statistic board"""

        subpage_path = (path 
                        + SeasonUrlDownload.PATHS["page_goalie"] 
                        + str(index))
        subpage_html = requests.get(subpage_path).content
        selector_subpage = scrapy.Selector(text=subpage_html)
        goalies_refs = selector_subpage.xpath(
            SeasonUrlDownload.PATHS["goalie_ref"]).getall()
        return goalies_refs

    def get_player_season_refs(self, league: str, season: str) -> dict:
        """downloads urls of player profiles for one season of one league from the webpage with statistics
            output dictionary: (players-goalies) -> urls"""

        league_stats_path = (ELITE_URL
                             + LEAGUE_URLS[league] 
                             + SeasonUrlDownload.PATHS["stats"] 
                             + "/" 
                             + season)
        dict_season = {}
        page_html = requests.get(league_stats_path).content
        selector_players = scrapy.Selector(text=page_html)
        ref_last_page = selector_players.xpath(
            SeasonUrlDownload.PATHS["last_page_players"]).getall()
        number_of_pages_players = [re.findall(
            "([0-9]+)$", string) for string in ref_last_page if re.search("[0-9]+$", string)]
        number_of_pages_goalies = [re.findall(
            SeasonUrlDownload.GOALIES_REG_MATCH, string)
            for string in ref_last_page if re.search(
                SeasonUrlDownload.GOALIES_REG, string)]
        sublist_players = []
        if number_of_pages_players == []:
            number_of_pages_players = 1
        else:
            number_of_pages_players = number_of_pages_players[0][0]
        for index in range(1, int(number_of_pages_players) + 1):
            player_refs = self._page_player(league_stats_path, index)
            sublist_players = sublist_players + player_refs
        if number_of_pages_goalies == []:
            number_of_pages_goalies = 1
        else:
            number_of_pages_goalies = number_of_pages_goalies[0][0]
        sublist_goalies = []
        for index in range(1, int(number_of_pages_goalies) + 1):
            goalies_refs = self._page_goalie(league_stats_path, index)
            sublist_goalies = sublist_goalies + goalies_refs
        dict_season["goalies"] = sublist_goalies
        dict_season["players"] = sublist_players
        return dict_season

    def get_team_season_refs(
            self, season: str, league: str, ref_list: list=[]
            ) -> list:
        """downloads team's urls for one  season"""

        url_season = (ELITE_URL 
                      + LEAGUE_URLS[league] 
                      + TEAM_STANDINGS 
                      + "/" 
                      + season)
        season_html = requests.get(url_season).content
        sel_season = scrapy.Selector(text=season_html)
        team_refs = sel_season.xpath(
            SeasonUrlDownload.PATHS["team_url"]).getall()
        for team_ref in team_refs:
            team_ref_wo_season = re.findall(
                "(.+)\/[0-9]{4}\-[0-9]{4}$", team_ref)
            if team_ref_wo_season == []:
                team_ref_wo_season = team_ref
            else:
                team_ref_wo_season = team_ref_wo_season[0]
            ref_list.append(team_ref_wo_season)
        return ref_list
    

def generate_date_list(start_date, end_date):

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    date_list = []
    current_date = start_date_dt
    while current_date <= end_date_dt:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return date_list

class GameApiIDDownload():
    """class contains methods for downloading ids of individual game centers of
      NHL games that are needed for URLS of API requests"""

    API_BASE = "https://api-web.nhle.com/v1/score/"
    GC_ID_REG = "\/([0-9]+)$"

    def __init__(self):
        pass

    def get_all_ids(self):
        """downloads game center ids for the whole history of the NHL"""

        dict_ids = {}
        for season in SEASON_DATE_RANGES:
            print(season)
            season_ids = self.get_season_ids(season)
            dict_ids[season] = season_ids
            print("Number of ids (games) in season " 
                  + season + ": "  
                  + str(len(season_ids)))
        return dict_ids

    def get_season_ids(self, season):
        """downloads game center ids for one season of NHL"""
        
        date_range = SEASON_DATE_RANGES[season]
        season_ids = self.get_range_dates_ids(date_range[0], date_range[1])
        return season_ids

    def get_range_dates_ids(self, start_date, end_date):
        """downloads game center ids for one date
           the date must be in the format y-m-d 
        """

        dict_ids = {}
        date_list = generate_date_list(
            start_date=start_date, 
            end_date=end_date)
        for date in date_list:
            date_ids = self.get_date_id(date)
            dict_ids[date] = date_ids
        return dict_ids

    def get_date_id(self, date_string):
        """for a given date downloads game center ids"""

        api_url_date = GameApiIDDownload.API_BASE + date_string
        response_dict = requests.get(api_url_date).json()
        date_ids = self.get_game_center_ids(response_dict)
        return date_ids

    def get_game_center_ids(self, date_dict):
        """parses dictionary with information about nhl games on a given date
           and extracts the game center ids
        """

        date_ids = []
        for game_dict in date_dict['games']:
            gc_link = game_dict['gameCenterLink']
            gc_id = re.findall(GameApiIDDownload.GC_ID_REG, gc_link)[0]
            date_ids.append(gc_id)
        return date_ids
