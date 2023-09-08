import scrapy
import requests
import re

from constants import *


class LeagueScrapper():

    """class used for scrapping data from the league webpage on elite browser website, 
    data downloaded consists of league name, standings of teams in individual seasons and list of achievements (trophies) - most points...
    """

    PATHS = {
        "achievements": "//ul[@class='column-2']/li/a/text()",
        "league_refs": "//a[@style='font-weight: 800;']/@href",
        "long_name": "//h1[@class='plytitle text-center text-sm-left m-0']"
                     "/text()"
    }

    SEASON_URL_REGEX = "standings/(.+)"

    def __init__(self, url):
        """url is the web address of league on elite prospect website"""

        self.url = url
        self.html = requests.get(url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_league_data(self):
        """method that creates dictionary of all data that is available to scrap with this class
        """

        league_dict = {}
        league_dict[UID] = self._get_uid()
        league_dict[LEAGUE_NAME] = self.get_name()
        league_dict[LEAGUE_ACHIEVEMENTS] = self.get_achievements()
        league_dict[SEASON_STANDINGS] = self.get_season_data()
        return league_dict

    def _get_uid(self):
        """method for accessing uid of league from url"""

        u_id = re.findall(LEAGUE_UID_REGEX, self.url)[0]
        return u_id

    def get_name(self):
        """method for scraping league name"""

        long_name = self.selector.xpath(
            LeagueScrapper.PATHS["long_name"]).getall()
        long_name = long_name[0].strip()
        return long_name

    def get_achievements(self):
        """method for scraping list of achievements(trophies):
        most points, goals in the season etc."""

        achievements_list = self.selector.xpath(
            LeagueScrapper.PATHS["achievements"]).getall()
        achievements_list = [achievement.strip()
                             for achievement in achievements_list]
        return achievements_list

    def get_season_data(self):
        """method for creating dictionary with season standings of teams for all years that are availiable on the website
        """

        ref_list = self.selector.xpath(
            LeagueScrapper.PATHS["league_refs"]).getall()
        league_standings_dict = {}
        for link in ref_list:
            season_name = re.findall(LeagueScrapper.SEASON_URL_REGEX, link)[0]
            league_season_o = LeagueSeasonScraper(url=link)
            season_dict = league_season_o.get_season_standings()
            league_standings_dict[season_name] = season_dict
        return league_standings_dict


class LeagueSeasonScraper():

    """class grouping methods for scraping data from one season standings table"""

    PATHS = {
        "table_section_l": "//table[@class = 'table standings table-sortable']"
                         "//tbody[count(./tr/*)>1]",
        "table_section_r": "/tr[not(@class = 'title')]",
        "table_section_names": "//table[@class = 'table standings"
                               " table-sortable']//tr[@class='title']"
                               "/td//text()",
        "table_row": "//table[@class = 'table standings"
                          " table-sortable']//tr",
        "one_row_r": "/td//text()",
        "team_url_r": "/td[@class='team']//a/@href"
        }
    
    STAT_NAMES = [LEAGUE_POSITION, TEAM, GP, W, T, L,
                    OTW, OTL, GOALS_FOR, GOALS_AGAINST, PLUS_MINUS, TOTAL_POINTS, POSTSEASON]
    
    REGEX_SEASON = "(.+)\/[0-9]{4}\-[0-9]{4}$"

    def __init__(self, url):
        self.url = url
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_season_standings(self):
        """method for downloading season stadnings data from one season"""

        section_names = self.selector.xpath(
            LeagueSeasonScraper.PATHS["table_section_names"]).getall()
        section_names = [name.strip() for name in section_names]
        n_sections = len(self.selector.xpath(
            LeagueSeasonScraper.PATHS["table_section_l"]).getall())
        if n_sections > len(section_names):
            section_names = ["main"] + section_names
        dict_season = {}
        for section_ind in range(1, n_sections + 1):
            dict_season[section_names[section_ind - 1]] = self.get_section(
                section_ind=section_ind)
        return dict_season
    

    def get_section(self, section_ind):
        """wraper method for downloading season standings data from one section of season standings table
        """

        path_section = (LeagueSeasonScraper.PATHS["table_section_l"] 
                            + "[" 
                            + str(section_ind) 
                            + "]" 
                            + LeagueSeasonScraper.PATHS["table_section_r"])
        dict_section = self.get_section_standings(
                path_section=path_section)
        return dict_section


    def get_section_standings(self, path_section):
        """method for downloading season standings data from one section of season standings table
        """

        n_rows = len(self.selector.xpath(path_section).getall())
        dict_section = {}
        for row_ind in range(1, n_rows + 1):
            row_dict = self.get_one_row(
                path_section=path_section, row_ind=row_ind)
            print(row_dict)
            dict_section[row_dict[LEAGUE_POSITION]] = row_dict
        return dict_section
    
    def get_one_row(self, path_section, row_ind):
        """method for downloading one row from season stadndings table"""

        dict_row = {}
        dict_row[TEAM_URL] = self.get_team_url(
            path_section=path_section, row_ind=row_ind)
        row_stats = self.get_row_stats(path_section=path_section, row_ind=row_ind)
        for ind in range(len(row_stats)):
            dict_row[LeagueSeasonScraper.STAT_NAMES[ind]
                        ] = row_stats[ind].strip()
        return dict_row

    def get_row_stats(self, path_section, row_ind):
         """methods for downloading indvidiual attributes from one row of season standings table (total points, goals, goals against...)"""

         one_row_path = (path_section 
                        + "[" 
                        + str(row_ind) 
                        + "]" 
                        + LeagueSeasonScraper.PATHS["one_row_r"])
         row_data = self.selector.xpath(one_row_path).getall()
         row_data = [value.strip()
                    for value in row_data if value.strip() != ""]
         return row_data

    def get_team_url(self, path_section, row_ind):
        """method for accessing team uid form url of team website"""

        path_url = (path_section 
                        + "[" 
                        + str(row_ind) 
                        + "]" 
                        +  LeagueSeasonScraper.PATHS["team_url_r"])
        url_season = self.selector.xpath(path_url).getall()[0]
        url_general = re.findall(
            LeagueSeasonScraper.REGEX_SEASON, url_season)[0]
        return url_general