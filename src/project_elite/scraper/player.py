import requests
import scrapy
import re


class PlayerScraper:

    #names of player attributes that are downloaded but should excluded 
    names_exclude = ["PREMIUM", "Agency", "Highlights"]

    #names of values of attributes of playes that are downloaded but should be excluded
    values_exclude = ["", "Powered by"]

    #names of all categories of attributes regarding downloading of stats for indivdual seasons
    stat_names = ["regular_season", "play_off", "leadership", "league"]

    #all paths used to acces data on individual player profile webpage
    paths = { "path_league": "//div[@id='league-stats']",
             "path_tournament": "//div[@id='cup-stats']",
            "stats_table_l": "//table[contains(@class,'table table-condensed table-sortable')]//tr[",
            "stats_table_r": "]/td",
             "stat_years": "//table[contains(@class,'table table-condensed table-sortable')]/tbody/tr/@data-season",
            "stat_league": "[@class = 'league']/a/text()",
            "url_league": "[@class = 'league']/a/@href",
            "url_team": "[@class = 'team']//a[1]/@href",
             "stat_team": "[@class = 'team']/span/a[1]/text()",
             "stat_leadership": "[@class = 'team']/span/a[2]/text()",
             "stat_league": "[@class = 'league']/a/text()",
             "stat_regular": "[contains(@class,'regular')]/text()",
             "stat_playoff": "[contains(@class,'postseason ')]/text()",
            "achievements_l": "//li[",
             "achievements_r":"]/div[@class='col-xs-10']//li/a/text()",
             "achievements_years": "//div[@class='col-xs-4 season']/text()",
             "player_name": "//h1[@class = 'ep-entity-header__name']//text()",
             "general_info": "//div[contains(@class, 'ep-list__item--is-compact')]"
            }
    
    def __init__(self, url):

        """Arguments:
        url - url of player profile
        html - html code of player profile webpage
        selector - selector object created from html code used for parsing data for individual values 
        """
        self.url = url
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)
        

    def get_info_all(self, years = None):

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
                    Achievements  - keys are seasons, values are lists with award names"""

        dict_player = {}
        gi_o = PlayerGeneralInfo(selector=self.selector)
        dict_player["info"] = gi_o._get_general_info()
        a_o = PlayerAchievements(selector=self.selector)
        dict_player["achievements"] = a_o.get_achievements()
        s_o = PlayerStats(selector=self.selector)
        dict_player["stats"] = s_o.get_all_stats()
        dict_player["u_id"] = re.findall("player\/([0-9]+)\/", self.url)[0]
        return dict_player
    
class PlayerGeneralInfo():

        paths = {"player_name": "//h1[@class = 'ep-entity-header__name']//text()",
                 "general_info_left": "//div[contains(@class, 'ep-list__item--is-compact')]/div[2][preceding-sibling::div[1][contains(text(), '"}
        

        info_names = ["Date of Birth", "Age", "Place of Birth", 
                      "Nation", "Position", "Height", "Weight", 
                      "Shoots", "Contract", "Cap Hit", "NHL Rights",
                        "Drafted", "Status", "Catches"]

        def __init__(self, selector):
            self.selector = selector

        def _get_general_info(self):
            dict_gi = self._get_info_wraper()
            dict_gi["name"] = self._get_name()
            return dict_gi

        def _get_name(self):
            
            """used to get player name"""

            name = self.selector.xpath(PlayerGeneralInfo.paths["player_name"]).getall()
            name = [string.strip() for string in name]
            name = [string for string in name if string != ""]
            return name[0].strip()
    
        def _get_info_wraper(self):
            dict_gi = {}
            for info_name in PlayerGeneralInfo.info_names:
                keep_list = False
                if info_name == "Drafted":
                    keep_list = True
                dict_gi[info_name] = self._get_info(info_name=info_name, keep_list=keep_list)
            return dict_gi

        def _get_info(self, info_name, keep_list):
            info_path_val = PlayerGeneralInfo.paths["general_info_left"] + info_name + "')]]//text()"
            info_val = self.selector.xpath(info_path_val).getall()
            info_val = [string.strip() for string in info_val]
            info_val = [string for string in info_val if string != ""]
            if info_val == []:
                info_val = [None]
            if keep_list == False:
                return info_val[0]
            else:
                return info_val
            

class PlayerStats():

    paths = {"path_league": "//div[@id='league-stats']",
             "path_tournament": "//div[@id='cup-stats']",
            "stats_table_l": "//table[contains(@class,'table table-condensed table-sortable')]//tr[",
            "stats_table_r": "]/td",
            "stat_years": "//table[contains(@class,'table table-condensed table-sortable')]/tbody/tr/@data-season", 
            "url_league": "[@class = 'league']/a/@href",
            "url_team": "[@class = 'team']//a[1]/@href",
             "stat_team": "[@class = 'team']/span/a[1]/text()",
             "stat_leadership": "[@class = 'team']/span/a[2]/text()",
             "stat_league": "[@class = 'league']/a/text()",
             "stat_regular": "[contains(@class,'regular')]/text()",
             "stat_playoff": "[contains(@class,'postseason ')]/text()"
             }

    def __init__(self, selector):
        self.selector = selector

    def get_all_stats(self, years=None):
        dict_stats = {}
        dict_stats["leagues"] = self.get_stats(years=years, type="league")
        dict_stats["tournaments"] = self.get_stats(years=years, type="tournament")
        return dict_stats
    
    def get_stats(self, type, years=None):
        if type == "league":
            path_type = PlayerStats.paths["path_league"]
        elif type == "tournament":
            path_type = PlayerStats.paths["path_tournament"]
        dict_stats={}
        path_years = path_type  + PlayerStats.paths["stat_years"]
        list_years = self.selector.xpath(path_years).getall()
        for ind in range(1, len(list_years) + 1):
            season = list_years[ind - 1]
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            if season not in dict_stats:
                dict_stats[season]={}
            path_season = path_type + PlayerStats.paths["stats_table_l"] + str(ind) +  PlayerStats.paths["stats_table_r"]
            sub_dict = self.get_season_stats_from_table(path=path_season, season=season)
            dict_stats[season] = {**dict_stats[season], **sub_dict}
        return dict_stats
    
    def get_season_stats_from_table(self, path, season):
        dict_season = {}
        path_reg = path + PlayerStats.paths["stat_regular"]
        path_playoff = path + PlayerStats.paths["stat_playoff"]
        path_team = path + PlayerStats.paths["stat_team"]
        path_leadership = path + PlayerStats.paths["stat_leadership"]
        path_league = path + PlayerStats.paths["stat_league"]
        path_url_team = path + PlayerStats.paths["url_team"]
        path_url_league = path + PlayerStats.paths["url_league"]
        team_name = self.selector.xpath(path_team).getall()
        team_name = [string.strip() for string in team_name]
        if team_name == []:
            return {}
        team_name = team_name[0]
        league_name = self.selector.xpath(path_league).getall()
        league_name = [string.strip() for string in league_name]
        if league_name == []:
            league_name = None
        else:
            league_name = league_name[0]
        leadership = self.selector.xpath(path_leadership).getall()
        leadership = [string.strip() for string in leadership]
        stat_playoff = self.selector.xpath(path_playoff).getall()
        stat_playoff = [string.strip() for string in stat_playoff]
        stat_regular = self.selector.xpath(path_reg).getall()
        stat_regular = [string.strip() for string in stat_regular]
        url_team = self.extract_general_url(path=path_url_team, regex="(.+)\/[^\/]+$")
        if league_name is not None:
            url_league = self.extract_general_url(path=path_url_league, regex="(.+)\/stats")
        else: 
            url_league = None
        dict_season[league_name] = {}
        dict_season[league_name][team_name] = {}
        dict_season[league_name][team_name]["regular_season"] = stat_regular
        dict_season[league_name][team_name]["play_off"] = stat_playoff
        dict_season[league_name]["url"] = url_league
        dict_season[league_name][team_name]["url"] = url_team
        if leadership != []:
            leadership = leadership[0]
            dict_season[league_name][team_name]["leadership"] = leadership
        return dict_season
    
    def extract_general_url(self, path, regex):
        list_data = self.selector.xpath(path).getall()
        orig_url = list_data[0]
        url_list = re.findall(regex, orig_url)
        url = url_list[0]
        return url
    
class PlayerAchievements():

    paths = {"achievements_l": "//li[",
             "achievements_r":"]/div[@class='col-xs-10']//li/a/text()",
             "achievements_years": "//div[@class='col-xs-4 season']/text()",}

    def __init__(self, selector):
        self.selector = selector
        
    def get_achievements(self, years=None):

        """method for downloading achievements of player into dictionary """

        dict_achiev = {}
        list_years = self.selector.xpath(PlayerAchievements.paths["achievements_years"]).getall()
        list_years = [string.strip() for string in list_years]
        for ind in range(1, len(list_years) + 1):
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            path = PlayerAchievements.paths["achievements_l"] + str(ind) + PlayerAchievements.paths["achievements_r"]
            award = self.selector.xpath(path).getall()
            dict_achiev[list_years[ind - 1]] = award
        return dict_achiev

    
    


    
            
            



            




        
        