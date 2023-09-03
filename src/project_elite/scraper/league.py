import scrapy
import requests
import re


class LeagueScrapper():

    PATHS = {
        "achievements": "//ul[@class='column-2']/li/a/text()",
        "league_refs": "//a[@style='font-weight: 800;']/@href",
        "long_name": "//h1[@class='plytitle text-center text-sm-left m-0']"
                     "/text()"
    }

    def __init__(self, url):
        self.url = url
        self.html = requests.get(url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_u_id(self):
        u_id = re.findall("league\/(.+)", self.url)[0]
        return u_id

    def get_long_name(self):
        long_name = self.selector.xpath(
            LeagueScrapper.PATHS["long_name"]).getall()
        long_name = long_name[0].strip()
        return long_name

    def get_achievements(self):
        achievements_list = self.selector.xpath(
            LeagueScrapper.PATHS["achievements"]).getall()
        achievements_list = [achievement.strip()
                             for achievement in achievements_list]
        return achievements_list

    def get_season_data(self):
        ref_list = self.selector.xpath(
            LeagueScrapper.PATHS["league_refs"]).getall()
        league_standings_dict = {}
        for link in ref_list:
            season_name = re.findall("standings/(.+)", link)[0]
            league_season_o = LeagueSeasonScraper(url=link)
            season_dict = league_season_o.get_season_standings()
            league_standings_dict[season_name] = season_dict
        return league_standings_dict

    def get_league_data(self):
        league_dict = {}
        league_dict["u_id"] = self.get_u_id()
        league_dict["long_name"] = self.get_long_name()
        league_dict["achievements_names"] = self.get_achievements()
        league_dict["season_tables"] = self.get_season_data()
        return league_dict


class LeagueSeasonScraper():

    PATHS = {
        "table_section": "//table[@class = 'table standings table-sortable']"
                         "//tbody[count(./tr/*)>1]",
        "table_section_names": "//table[@class = 'table standings"
                               " table-sortable']//tr[@class='title']"
                               "/td//text()",
        "table_row": "//table[@class = 'table standings"
                          " table-sortable']//tr"
        }
    
    header_names = ["position", "team", "gp", "w", "t", "l",
                    "otw", "otl", "gf", "ga", "plus_minus", "tp", "postseason"]

    def __init__(self, url):
        self.url = url
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_section_standings(self, path_section):
        n_rows = len(self.selector.xpath(path_section).getall())
        dict_section = {}
        for row_ind in range(1, n_rows + 1):
            dict_row = {}
            one_row_path = (path_section 
                            + "[" 
                            + str(row_ind) 
                            + "]" 
                            + "/td//text()")
            one_row_html = (path_section 
                            + "[" 
                            + str(row_ind) 
                            + "]" 
                            + "/td[@class='team']//a/@href")
            row_data = self.selector.xpath(one_row_path).getall()
            url_team_season = self.selector.xpath(one_row_html).getall()[0]
            url_team_general = re.findall(
                "(.+)\/[0-9]{4}\-[0-9]{4}$", url_team_season)[0]
            row_data = [value.strip()
                        for value in row_data if value.strip() != ""]
            for ind in range(1, len(row_data)):
                dict_row[LeagueSeasonScraper.header_names[ind]
                         ] = row_data[ind].strip()
            dict_row["url"] = url_team_general
            dict_section[row_data[0]] = dict_row
        return dict_section

    def get_season_standings(self):
        section_names = self.selector.xpath(
            LeagueSeasonScraper.PATHS["table_section_names"]).getall()
        section_names = [name.strip() for name in section_names]
        n_sections = len(self.selector.xpath(
            LeagueSeasonScraper.PATHS["table_section"]).getall())
        if n_sections > len(section_names):
            section_names = ["main"] + section_names
        dict_season = {}
        for part_ind in range(1, n_sections + 1):
            path_section = (LeagueSeasonScraper.PATHS["table_section"] 
                            + "[" 
                            + str(part_ind) 
                            + "]" 
                            + "/tr[not(@class = 'title')]")
            dict_section = self.get_section_standings(
                path_section=path_section)
            dict_season[section_names[part_ind - 1]] = dict_section
        return dict_season
