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
        
    
    def get_info_all(self, years=None):

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
        dict_player["Info"] = self.get_general_info()
        dict_player["Achievements"] = self.get_achievements(years=years)
        dict_player["Stats"] = self.get_all_stats(years=years)
        dict_player_wrap = {}
        dict_player_wrap[dict_player["Info"]["u_id"]]  = dict_player
        return dict_player_wrap
    
    def get_general_info(self):
        dict_info = self._name_values_combiner()
        print(dict_info)
        dict_info["name"] = self._get_name()
        dict_info["u_id"] = re.findall("player\/([0-9]+)\/", self.url)[0]
        return dict_info
    
    def _name_values_combiner(self):

        """function that combines general info about player into dictionary where keys are attribute names 
            and values are respective values (Nationality:Finland etc.)"""
        names = self.selector.xpath(PlayerScraper.paths["general_info"]).getall()
        dict_info = {}
        for ind in range(1, len(names)+1):
            matcher_one = PlayerScraper.paths["general_info"] + "[" + str(ind) + "]"
            names_matcher = matcher_one + "/div[1]//text()"
            values_matcher = matcher_one + "/div[2]//text()"
            name = self.selector.xpath(names_matcher).getall()
            name = [string.strip() for string in name][0]
            if name in PlayerScraper.names_exclude:
                continue
            value = self.selector.xpath(values_matcher).getall()
            value = [string.strip() for string in value]
            value = [string for string in value if string != ""]
            value = "".join(value)
            dict_info[name] = value
        return dict_info

    def _get_name(self):

        """used to get player name"""

        name = self.selector.xpath(PlayerScraper.paths["player_name"]).getall()
        print(name)
        name = [string.strip() for string in name]
        name = [string for string in name if string != ""]
        return name[0].strip()
            
    def get_achievements(self, years=None):

        """method for downloading achievements of player into dictionary """

        dict_achiev = {}
        list_years = self.selector.xpath(PlayerScraper.paths["achievements_years"]).getall()
        list_years = [string.strip() for string in list_years]
        for ind in range(1, len(list_years) + 1):
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            path = PlayerScraper.paths["achievements_l"] + str(ind) + PlayerScraper.paths["achievements_r"]
            award = self.selector.xpath(path).getall()
            dict_achiev[list_years[ind - 1]] = award
        return dict_achiev
            
    def get_stats_old(self, years=None):

        """method for downloading stats for individuals seasons  of player into dictionary"""

        dict_stats = {}
        list_years = self.selector.xpath(PlayerScraper.paths["stat_years"]).getall()
        for ind in range(1, len(list_years) + 1):
            season = list_years[ind - 1]
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            if season not in dict_stats:
                dict_stats[season]={}
            path = PlayerScraper.paths["stats_table_l"] + str(ind) +  PlayerScraper.paths["stats_table_r"]
            path_reg = path + PlayerScraper.paths["stat_regular"]
            path_playoff = path + PlayerScraper.paths["stat_playoff"]
            path_team = path + PlayerScraper.paths["stat_team"]
            path_leadership = path + PlayerScraper.paths["stat_leadership"]
            path_league = path + PlayerScraper.paths["stat_league"]
            list_paths = [path_reg, path_playoff, path_leadership, path_league]
            list_results = []
            team_name = self.selector.xpath(path_team).getall()
            team_name = [string.strip() for string in team_name]
            if team_name == []:
                team_name = ["DNP"]
            league_name = self.selector.xpath(path_league).getall()
            league_name = [string.strip() for string in league_name]
            leadership = self.selector.xpath(path_leadership).getall()
            leadership = [string.strip() for string in leadership]
            stat_playoff = self.selector.xpath(path_playoff).getall()
            stat_playoff = [string.strip() for string in stat_playoff]
            stat_regular = self.selector.xpath(path_reg).getall()
            stat_regular = [string.strip() for string in stat_regular]
            for path in list_paths:
                result = self.selector.xpath(path).getall()
                result = [string.strip() for string in result]
                list_results.append(result)
            dict_stats[season][list_results[0][0]] = {}
            for ind in range(1, len(PlayerScraper.stat_names) + 1):
                if ind > 2:
                    if list_results[ind] != []:
                        dict_stats[season][list_results[0][0]][PlayerScraper.stat_names[ind-1]] = list_results[ind][0]
                else:
                    dict_stats[season][list_results[0][0]][PlayerScraper.stat_names[ind-1]] = list_results[ind]
        return dict_stats
    
    def get_all_stats(self, years=None):
        dict_stats = {}
        dict_stats["leagues"] = self.get_stats(years=years, type="league")
        dict_stats["tournaments"] = self.get_stats(years=years, type="tournament")
        return dict_stats
    
    def get_stats(self, type, years=None):
        if type == "league":
            path_type = PlayerScraper.paths["path_league"]
        elif type == "tournament":
            path_type = PlayerScraper.paths["path_tournament"]
        dict_stats={}
        path_years = path_type  + PlayerScraper.paths["stat_years"]
        list_years = self.selector.xpath(path_years).getall()
        for ind in range(1, len(list_years) + 1):
            season = list_years[ind - 1]
            if years is not None:
                if list_years[ind - 1] not in years:
                    continue
            if season not in dict_stats:
                dict_stats[season]={}
            path_season = path_type + PlayerScraper.paths["stats_table_l"] + str(ind) +  PlayerScraper.paths["stats_table_r"]
            sub_dict = self.get_season_stats_from_table(path=path_season, season=season)
            dict_stats[season] = {**dict_stats[season], **sub_dict}
        return dict_stats

    def get_season_stats_from_table(self, path, season):
        dict_season = {}
        path_reg = path + PlayerScraper.paths["stat_regular"]
        path_playoff = path + PlayerScraper.paths["stat_playoff"]
        path_team = path + PlayerScraper.paths["stat_team"]
        path_leadership = path + PlayerScraper.paths["stat_leadership"]
        path_league = path + PlayerScraper.paths["stat_league"]
        path_url_team = path + PlayerScraper.paths["url_team"]
        path_url_league = path + PlayerScraper.paths["url_league"]
        team_name = self.selector.xpath(path_team).getall()
        team_name = [string.strip() for string in team_name]
        if team_name == []:
            return {}
        team_name = team_name[0]
        league_name = self.selector.xpath(path_league).getall()
        league_name = [string.strip() for string in league_name][0]
        leadership = self.selector.xpath(path_leadership).getall()
        leadership = [string.strip() for string in leadership]
        stat_playoff = self.selector.xpath(path_playoff).getall()
        stat_playoff = [string.strip() for string in stat_playoff]
        stat_regular = self.selector.xpath(path_reg).getall()
        stat_regular = [string.strip() for string in stat_regular]
        url_team = self.extract_general_url(path=path_url_team, regex="(.+)\/[^\/]+$")
        url_league = self.extract_general_url(path=path_url_league, regex="(.+)\/stats")
        dict_season[league_name] = {}
        dict_season[league_name][team_name] = {}
        dict_season[league_name][team_name]["regular_season"] = stat_regular
        dict_season[league_name][team_name]["play_off"] = stat_playoff
        dict_season[league_name]["url"] = url_league
        dict_season[league_name][team_name]["url"] = url_team
        if leadership != []:
            leadership = leadership[0]
            dict_season[league_name][team_name]["leadership"] = leadership
        print(dict_season)
        return dict_season

                    
    def extract_general_url(self, path, regex):
        list_data = self.selector.xpath(path).getall()
        orig_url = list_data[0]
        print(orig_url)
        url_list = re.findall(regex, orig_url)
        url = url_list[0]
        print(url)
        return url


        
        