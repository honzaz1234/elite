import re
import requests
import scrapy
from hockeydata.constants import *


class GetGameStats():

    XPATHS = {
        "game_summary": "//a[contains(text(), 'Game Summary')]",
        "playbyplay_report": "//a[contains(text(), 'Full Play-By-Play')]",
        "faceoff_comparison": "//a[contains(text(), 'Faceoff Comparison')]",
        "faceoff_summary": "//a[contains(text(), 'Faceoff Summary')]",
    }

    def __init__(self, url):
        self.url = url
        self.html = requests.get(url).content
        self.sel = scrapy.Selector(text=self.html)
        self.url_dict = {}

    def get_urls(self):
        self.url_dict["game_summary"] = self.sel.xpath(GetGameStats.XPATHS["game_summary"]).get()
        print(self.url_dict)
        self.url_dict["playbyplay"] = self.sel.xpath(GetGameStats.XPATHS["playbyplay_report"]).get()
        self.url_dict["faceoff_comparison"] = self.sel.xpath(
            GetGameStats.XPATHS["faceoff_comparison"]).get()
        self.url_dict["playbyplay_report"] = self.sel.xpath(
            GetGameStats.XPATHS["playbyplay_report"]).get()

    def get_info_all(self):
        dict_all = {}
        plays_o = GetPlays(self.url)
        dict_plays = plays_o.get_all_plays(
            base_url=self.url_dict["playbyplay"])
        dict_all["plays"] = dict_plays


class GetPlays():

    XPATHS = {
        "home_team": "//table[@id='Home']//td[@align='center'][3]//@alt",
        "away_team": "//table[@id='Visitor']//td[@align='center'][3]//@alt",
        "date": "//table[@id='GameInfo']/tbody/tr[4]",
        "venue_attendance": "//table[@id='GameInfo']/tbody/tr[4]",
        "start_end": "//table[@id='GameInfo']/tbody/tr[6]"
    }

    def __init__(self, base_url):

        self.url = base_url
        self.htm = requests.get(base_url).content
        self.sel = scrapy.Selector(text=self.htm)
        self.dict_info = {}
        self.dict_info["id"] = re.findall('\/(.+).HTM$')

    
    def get_general_info(self):

        g_info_dict = {}
        g_info_dict["home_team"] = self.get_home_team()
        g_info_dict["away_team"] = self.get_away_team()
        g_info_dict["arena"] = self.get_away_team()
        g_info_dict["arena"] = self.get_away_team()
        g_info_dict["attendance"] = self.get_away_team()
        g_info_dict["start_time"] = self.get_away_team()
        g_info_dict["time_zone"] = self.get_away_team()
        g_info_dict["end_time"] = self.get_away_team()

    def get_plays(self):
        
        play_parser_o = PlayParser(selector=self.sel)
        plays_dict = play_parser_o.parse_plays()
        return plays_dict

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
        
        arena_name = self.sel.xpath(
            GetPlays.XPATHS["venue_attendance"]).get()
        arena_name = re.findall("at\s(.+)$", arena_name)
        arena_name = arena_name.capitalize()
        return arena_name
    
    def get_attendance(self):
        
        attendance = self.sel.xpath(
            GetPlays.XPATHS["venue_attendance"]).get()
        attendance = re.findall("at\s(.+)$", attendance)
        attendance = attendance.replace(",", "")
        return attendance
    
    def get_start_time(self):
        
        start_time = self.sel.xpath(
            GetPlays.XPATHS["start_end"]).get()
        start_time = re.findall("Start\s(.+)\s", start_time)
        return start_time
    
    def get_time_zone(self):
        
        time_zone = self.sel.xpath(
            GetPlays.XPATHS["start_end"]).get()
        time_zone = re.findall("\s(.+);", time_zone)
        return time_zone
    
    def get_end_time(self):
        
        end_time = self.sel.xpath(
            GetPlays.XPATHS["start_end"]).get()
        end_time = re.findall("End\s(.+)\s", end_time)
        return end_time
        
class PlayParser():

    XPATHS = {
        "play_selector": "//tr[contains(@id, 'PL')]",
        "play_type": "//td[5]/text()",
        "game_time": "//td[4]/text()"
    }

    def __init__(self, selector):
        self.sel = selector

    def parse_plays(self):
        dict_plays = {}
        list_sel_plays = self.sel(PlayParser.XPATHS["play_selector"]).getall()
        count = 0
        for sel_play in list_sel_plays:
            count += 1
            dict_plays[count] = self.parse_play(selector=sel_play)
        return dict_plays
    
    def parse_play(self):

        dict_play = {}
        play_type = self.sel(PlayParser.XPATHS["play_type"]).get()
        dict_play["play_type"] = play_type
        dict_play["play_info"] = self.parse_play_string(play_type=play_type)

    def parse_play_string(self, play_type):

        dict_play_string = {}
        if play_type == "HIT":
            dict_play_string = self.parse_hit_string()
        elif play_type == "SHOT":
            dict_play_string = self.parse_shot_string()
       # else if play_type == "STOP":

    #def get_game_time(self):

     #   dict_play["game_time"] = 




        



        
