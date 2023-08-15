import requests
import scrapy
import re

class TeamScraper():

    paths = {
             "team_facts_names" : "//div[@class='facts' and preceding-sibling::div[text()='Team Facts']]/span[@class='lbl']/text()", 
             "team_facts_value_leagues" : "//div[@class='facts' and preceding-sibling::div[text()='Team Facts']]/strong[@class='value']/a/text()", 
             "team_facts_value_others": "//div[@class='facts' and preceding-sibling::div[text()='Team Facts']]/span[@class='value']//text()",
             "stadium_facts_names": "//div[@class='facts' and preceding-sibling::div[text()='Team Captains'][1]]/span[@class='lbl']/text()", 
             "stadium_facts_values": "//div[@class='facts' and preceding::div[text()='Team Captains'][1]]/strong[@class='value']//text()",
             "affiliated_team_values": "//strong[@class='value' and preceding-sibling::span[text()='Affiliated Team(s)']]//@href", 
             "retired_num_values": "//ul[preceding-sibling::h4[text()='Retired Numbers']]//a[1]/",
             "history_table": "//table[@class ='table table-striped team-history-and-standings'][1]",
             "history_names": "//tr[@class='title']/td/text()",
             "history_seasons": "//td[@class='season']/a/text()",
             "path_season_left": "(//div[@class='content_left']//table[@class ='table table-striped team-history-and-standings'])[1]/tbody/tr[",
             "path_season_right": "]/td[@class='season']/a/text()",
             "num_titles": "count((//table[@class ='table table-striped team-history-and-standings'])[1]/tbody/tr[@class='title'])",
             "path_titles": "(//table[@class ='table table-striped team-history-and-standings'])[1]/tbody/tr[@class='title']/td/text()",
             "path_left": "count((//div[@class='content_left']//table[@class ='table table-striped team-history-and-standings'])[1]/tbody/tr[@class='title'][",
             "path_right": "]/following-sibling::tr)",
             "num_tr": "count((//div[@class='content_left']//table[@class ='table table-striped team-history-and-standings'])[1]/tbody/tr)",
             "short_name": "//h1[@class='semi-logo']/text()",
             "arena_name": "//strong[preceding::span[1][contains(text(), 'Arena Name')]]/text()",
             "place": "//strong[preceding::span[1][contains(text(), 'Location')]]/text()",
             "capacity": "//strong[preceding::span[1][contains(text(), 'Capacity')]]/text()",
             "construction_year": "//strong[preceding::span[1][contains(text(), 'Construction Year')]]/text()" 
             }
    url_parts = {"history": "?team-history=complete#team-history"}

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
        dict_info["general_info"]["u_id"] = int(re.findall("team\/([0-9]+)\/", self.url)[0])
        return dict_info
    
    def get_general_info(self):
        dict_gi = {}
        get_info = self.selector.xpath(TeamScraper.paths["team_facts_names"]).getall()
        info_values = []
        get_leagues = self.selector.xpath(TeamScraper.paths["team_facts_value_leagues"]).getall()
        get_leagues = [value.strip() for value in get_leagues]
        get_leagues = ", ".join(get_leagues)
        info_values.append(get_leagues)
        get_values = self.selector.xpath(TeamScraper.paths["team_facts_value_others"]).getall()
        get_values = [value.strip() for value in get_values]
        get_values = [value for value in get_values if value != ""]
        info_values = info_values + get_values
        for ind in range(len(get_info)):
            dict_gi[get_info[ind]] = info_values[ind]
        short_name = self.selector.xpath(TeamScraper.paths["short_name"]).getall()
        if short_name != []:
            dict_gi["short_name"] = short_name[0].strip()
        else:
            dict_gi["short_name"] = None
        return dict_gi
    
    def get_stadium_info(self):
        dict_si = {}
        for path_name in ["arena_name", "place", "capacity", "construction_year"]:
            value = self.selector.xpath(TeamScraper.paths[path_name]).getall()
            print(path_name)
            print(value)
            if value ==[]:
                dict_si[path_name] = None
            else:
                dict_si[path_name] = value[0]
        return dict_si

    def get_affiliated_teams(self):
        dict_at = {}
        dict_at = self.selector.xpath(TeamScraper.paths["affiliated_team_values"]).getall()
        return dict_at
    
    def get_retired_numbers(self):
        dict_num = {}
        path_url = TeamScraper.paths["retired_num_values"] + "@href"
        path_num = TeamScraper.paths["retired_num_values"] + "text()"
        urls = self.selector.xpath(path_url).getall()
        numbers = self.selector.xpath(path_num).getall()
        for ind in range(len(urls)):
            dict_num[urls[ind]] = numbers[ind].strip()
        return dict_num
    
    def get_historic_names(self):
        n_names = self.selector.xpath(TeamScraper.paths["num_titles"]).getall()[0]
        n_names = int(float(n_names))
        n_tr = self.selector.xpath(TeamScraper.paths["num_tr"]).getall()[0]
        n_tr = int(float(n_tr))
        title_positions = []
        titles = self.selector.xpath(TeamScraper.paths["path_titles"]).getall()
        titles = [title.strip() for title in titles]
        print(titles)
        for ind in range(1, n_names + 1):
            path1 = TeamScraper.paths["path_left"] + str(ind) + TeamScraper.paths["path_right"]
            n_following = self.selector.xpath(path1).getall()[0]
            n_following =  int(float(n_following))
            title_position = n_tr - n_following
            title_positions.append(title_position)
        if title_positions == []:
            n_names = 1
            titles = ["-"]
            title_positions = [0]
        title_positions.append(n_tr + 1)
        print(title_positions)
        dict_titles = {}
        count = title_positions[0]
        for ind in range(1, n_names + 1):
            print(ind)
            list_years = []
            while True:
                count += 1
                if count in title_positions:
                    break
                path_season = TeamScraper.paths["path_season_left"] + str(count) + TeamScraper.paths["path_season_right"]
                print([path_season]) 
                season = self.selector.xpath(path_season).getall()
                print(season)
                if season != []:
                    list_years.append(season[0])
            print(list_years)
            dict_titles[titles[ind-1]] = {}
            dict_titles[titles[ind-1]]["min"] = list_years[0]
            dict_titles[titles[ind-1]]["max"] = list_years[len(list_years)-1]
        return dict_titles



