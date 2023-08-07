import scrapy
import requests
import re
import src.project_elite.scraper.league.league_season.league_season as league_season

class LeagueScrapper():

    paths = {"achievements": "//ul[@class='column-2']/li/a/text()",
             "league_refs": "//a[@style='font-weight: 800;']/@href",
             "long_name": "//h1[@class='plytitle text-center text-sm-left m-0']/text()"}
    
    def __init__(self, url):
        self.html = requests.get(url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_long_name(self):
        long_name = self.selector.xpath(LeagueScrapper.paths["long_name"]).getall()
        long_name = long_name[0].strip()
        return long_name

    def get_achievements(self):
        achievements_list = self.selector.xpath(LeagueScrapper.paths["achievements"]).getall()
        achievements_list = [achievement.strip() for achievement in achievements_list]
        return achievements_list
    
    def get_season_data(self):
        ref_list = self.selector.xpath(LeagueScrapper.paths["league_refs"]).getall()
        league_standings_dict = {}
        for link in ref_list:
            print(link)
            season_name = re.findall("standings/(.+)", link)[0]
            league_season_o = league_season.LeagueSeasonScraper(url=link)
            season_dict = league_season_o.get_season_standings()
            league_standings_dict[season_name] = season_dict
        return league_standings_dict
    
    def get_league_data(self):
        league_dict = {}
        league_dict["long_name"] = self.get_long_name()
        league_dict["achievements_names"] = self.get_achievements()
        league_dict["season_tables"] = self.get_season_data()
        return league_dict



            
