import requests
import scrapy
import re

class TeamScraper():

    PATHS = {
        "team_facts_names" : "//div[@class='facts' and "
                             "preceding-sibling::div[text()='Team Facts']]"
                             "/span[@class='lbl']/text()", 
        "team_facts_value_leagues" : "//div[@class='facts' and preceding" 
                                     "-sibling::div[text()='Team Facts']]"
                                     "/strong[@class='value']/a/text()", 
        "team_facts_value_others": "//div[@class='facts' and prece"
                                   "ding-sibling::div[text()='Team Facts']]"
                                   "/span[@class='value']//text()",
        "stadium_facts_names": "//div[@class='facts' and preceding-sibling"
                               "::div[text()='Team Captains'][1]]"
                               "/span[@class='lbl']/text()", 
        "stadium_facts_values": "//div[@class='facts' and preceding::"
                                "div[text()='Team Captains'][1]]"
                                "/strong[@class='value']//text()",
        "affiliated_team_values": "//strong[@class='value'"
                                  " and preceding-sibling::span"
                                  "[text()='Affiliated Team(s)']]//@href", 
        "retired_num_values": "//ul[preceding-sibling::h4"
                              "[text()='Retired Numbers']]//a[1]/",
        "history_table": "//table[@class ='table table-striped"
                         " team-history-and-standings'][1]",
        "history_names": "//tr[@class='title']/td/text()",
        "history_seasons": "//td[@class='season']/a/text()",
        "path_season_left": "(//div[@class='content_left']//"
                            "table[@class ='table table-striped "
                            "team-history-and-standings'])[1]/tbody/tr[",
        "path_season_right": "]/td[@class='season']/a/text()",
        "num_titles": "count((//table[@class ='table table-striped"
                      " team-history-and-standings'])[1]/tbody"
                      "/tr[@class='title'])",
        "path_titles": "(//table[@class ='table table-striped"
                       " team-history-and-standings'])[1]"
                       "/tbody/tr[@class='title']/td/text()",
        "path_left": "count((//div[@class='content_left']"
                     "//table[@class ='table table-striped "
                     "team-history-and-standings'])[1]"
                     "/tbody/tr[@class='title'][",
        "path_right": "]/following-sibling::tr)",
        "num_tr": "count((//div[@class='content_left']"
                  "//table[@class ='table table-striped "
                  "team-history-and-standings'])[1]/tbody/tr)",
        "short_name": "//h1[@class='semi-logo']/text()",
        "arena_name": "//strong[preceding::span[1]"
                      "[contains(text(), 'Arena Name')]]/text()",
        "place": "//strong[preceding::span[1]"
                 "[contains(text(), 'Location')]]/text()",
        "capacity": "//strong[preceding::span[1]"
                    "[contains(text(), 'Capacity')]]/text()",
        "construction_year": "//strong[preceding::span[1]"
                             "[contains(text(), 'Construction Year')]]"
                             "/text()",
        "general_info_left": "//div[@class='league-title clearfix']"
                             "//*[@class='value' and preceding-sibling::"
                             "span[contains(text(),'", 
        "general_info_right": "')]/text()"
    }

    url_parts = {
        "history": "?team-history=complete#team-history"
    }

    info_names = ["Plays in", "Team colours", "Town", "Founded", "Full name"]

    def __init__(self, url):
        self.url = url + TeamScraper.url_parts["history"]
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_info(self):
        dict_info = {}
        dict_info["general_info"] = self.get_general_info()
        dict_info["stadium_info"] = self.get_stadium_info()
        dict_info["affiliated_teams"] = self.get_affiliated_teams()
        dict_info["retired_numbers"] = self.get_retired_numbers()
        dict_info["titles"] = self.get_historic_names()
        dict_info["general_info"]["u_id"] = int(re.findall("team\/([0-9]+)\/",
                                                           self.url)[0])
        return dict_info
    
    def get_general_info(self):
        dict_gi = {}
        for info_name in TeamScraper.info_names:
            dict_gi[info_name] = self._get_info(info_name=info_name,
                                                 keep_list=False)
        dict_gi["short_name"] = self._get_short_name()
        return dict_gi
        
    def _get_short_name(self):
        short_name = (self.selector.xpath(TeamScraper.PATHS["short_name"])
                      .getall())
        if short_name == []:
            raise Exception("html not downloaded")
        else:
            short_name = short_name[0].strip()
        return short_name


    def _get_info(self, info_name, keep_list):
            info_path_val = TeamScraper.PATHS["general_info_left"] + info_name + "')]]//text()"
            info_val = self.selector.xpath(info_path_val).getall()
            info_val = [string.strip() for string in info_val]
            info_val = [string for string in info_val if string != ""]
            if info_val == []:
                info_val = [None]
            if keep_list == False:
                return info_val[0]
            else:
                return info_val
    
    def get_stadium_info(self):
        dict_si = {}
        for path_name in ["arena_name", "place", "capacity", "construction_year"]:
            value = self.selector.xpath(TeamScraper.PATHS[path_name]).getall()
            if value ==[]:
                dict_si[path_name] = None
            else:
                dict_si[path_name] = value[0]
        return dict_si

    def get_affiliated_teams(self):
        dict_at = {}
        dict_at = (self.selector
                   .xpath(TeamScraper.PATHS["affiliated_team_values"])
                   .getall())
        return dict_at
    
    def get_retired_numbers(self):
        dict_num = {}
        path_url = TeamScraper.PATHS["retired_num_values"] + "@href"
        path_num = TeamScraper.PATHS["retired_num_values"] + "text()"
        urls = self.selector.xpath(path_url).getall()
        numbers = self.selector.xpath(path_num).getall()
        for ind in range(len(urls)):
            dict_num[urls[ind]] = numbers[ind].strip()
        return dict_num
    
    def get_historic_names(self):
        n_names = (self.selector
                  .xpath(TeamScraper.PATHS["num_titles"])
                  .getall()[0])
        n_names = int(float(n_names))
        n_tr = self.selector.xpath(TeamScraper.PATHS["num_tr"]).getall()[0]
        n_tr = int(float(n_tr))
        title_positions = []
        titles = self.selector.xpath(TeamScraper.PATHS["path_titles"]).getall()
        titles = [title.strip() for title in titles]
        for ind in range(1, n_names + 1):
            path1 = (TeamScraper.PATHS["path_left"] 
                     + str(ind) 
                     + TeamScraper.PATHS["path_right"])
            n_following = self.selector.xpath(path1).getall()[0]
            n_following =  int(float(n_following))
            title_position = n_tr - n_following
            title_positions.append(title_position)
        if title_positions == []:
            n_names = 1
            titles = ["-"]
            title_positions = [0]
        title_positions.append(n_tr + 1)
        dict_titles = {}
        count = title_positions[0]
        for ind in range(1, n_names + 1):
            list_years = []
            while True:
                count += 1
                if count in title_positions:
                    break
                path_season = (TeamScraper.paths["path_season_left"] 
                               + str(count) 
                               + TeamScraper.paths["path_season_right"])
                season = self.selector.xpath(path_season).getall()
                if season != []:
                    list_years.append(season[0])
            if list_years == []:
                continue
            dict_titles[titles[ind-1]] = {}
            dict_titles[titles[ind-1]]["min"] = list_years[0]
            dict_titles[titles[ind-1]]["max"] = list_years[len(list_years)-1]
        return dict_titles



