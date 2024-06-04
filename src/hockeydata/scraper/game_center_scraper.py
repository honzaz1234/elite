import re
import requests
import scrapy
from hockeydata.constants import *

XPATHS = {
    "game_summary": "//a[contains(text(), 'Game Summary')]",
    "playbyplay_report": "//a[contains(text(), 'Full Play-By-Play')]",
    "faceoff_comparison": "//a[contains(text(), 'Faceoff Comparison')]",
    "faceoff_summary": "//a[contains(text(), 'Faceoff Summary')]",
}


class GetGameStats():

    def __init__(self, url):
        self.url = url
        self.html = requests.get(url).content
        self.sel = scrapy.Selector(text=self.html)
        self.url_dict = {}

    def get_urls(self):
        self.url_dict["game_summary"] = self.sel(XPATHS["game_summary"])
        self.url_dict["playbyplay"] = self.sel(XPATHS["playbyplay_report"])
        self.url_dict["faceoff_comparison"] = self.sel(
            XPATHS["faceoff_comparison"])
        self.url_dict["playbyplay_report"] = self.sel(
            XPATHS["playbyplay_report"])


    def get_info_all(self):
        dict_all = {}
        plays_o = GetPlays()
        dict_plays = plays_o.get_all_plays(
            base_url=self.url_dict["playbyplay"])
        dict_all["plays"] = dict_plays


class GetPlays():

    XPATHS = {
        "home_team": "//table[@id='Home']//td[@align='center'][3]//@alt",
        "away_team": "//table[@id='Visitor']//td[@align='center'][3]//@alt",

        }

    def __init__(self, base_url):

        self.url = base_url
        self.htm = requests.get(base_url)
        self.sel = scrapy.Selector(text=self.htm)
        self.dict_info = {}
        self.dict_info["id"] = re.findall('\/(.+).HTM$')

    
    def get_general_info(self):
        g_info_dict = {}
        g_info_dict["home_team"] = self.get_home_team()
        g_info_dict["away_team"] = self.get_away_team()
        g_info_dict["arena"] = self.get_away_team()

    
    def get_home_team(self):
        
        home_team = self.sel.xpath(
            GetPlays.XPATHS["home_team"]).get()
        home_team = home_team.capitalize()
        return home_team
    
    def get_away_team(self):
        
        home_team = self.sel.xpath(
            GetPlays.XPATHS["away_team"]).get()
        home_team = home_team.capitalize()
        return home_team
    
    def get_arena_name(self):
        
        home_team = self.sel.xpath(
            GetPlays.XPATHS["away_team"]).get()
        home_team = home_team.capitalize()
        return home_team


        
