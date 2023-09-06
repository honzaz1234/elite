import requests
import scrapy
import re


class TeamScraper():
    """class for downloading data from team webpage;
    there are methods available for downloading general info, stadium info, affiliated teams, retired numbers and historic names
    """

    INFO_PATHS = {

        "short_name": "//h1[@class='semi-logo']/text()",
        "gi_left": "//div[@class='league-title clearfix']"
                             "//*[@class='value' and preceding-sibling::"
                             "span[contains(text(),'",
        "gi_right": "')]]//text()",
        "si_left": "//strong[preceding::span[1]"
                      "[contains(text(), '",
        "si_right": "')]]/text()"
    }
    
    HN_PATHS = {
        "season_l": "(//div[@class='content_left']//"
                            "table[@class ='table table-striped "
                            "team-history-and-standings'])[1]/tbody/tr[",
        "season_r": "]/td[@class='season']/a/text()",
        "num_titles": "count((//table[@class ='table table-striped"
                      " team-history-and-standings'])[1]/tbody"
                      "/tr[@class='title'])",
        "num_lines": "count((//div[@class='content_left']"
                  "//table[@class ='table table-striped "
                  "team-history-and-standings'])[1]/tbody/tr)",
        "titles": "(//table[@class ='table table-striped"
                       " team-history-and-standings'])[1]",
        "name_left": "count((//div[@class='content_left']"
                     "//table[@class ='table table-striped "
                     "team-history-and-standings'])[1]"
                     "/tbody/tr[@class='title'][",
        "name_right": "]/following-sibling::tr)"
    }

    OTHER_PATHS = {
        "affiliated_teams": "//strong[@class='value'"
                                  " and preceding-sibling::span"
                                  "[text()='Affiliated Team(s)']]//@href",
        "retired_num": "//ul[preceding-sibling::h4"
                              "[text()='Retired Numbers']]//a[1]/"
    }

    URL_SECTIONS = {
        "history": "?team-history=complete#team-history"
    }

    INFO_NAMES = ["Plays in", "Team colours", "Town", "Founded", "Full name"]
    STADIUM_INFO_NAMES = ["Arena Name", "Location", "Capacity", 
                          "Construction Year"]


    def __init__(self, url):
        self.url = url + TeamScraper.URL_SECTIONS["history"]
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_info(self):
        """ wrapper function for downloading all of the info from one team webpage"""

        dict_info = {}
        dict_info["general_info"] = self.get_dict_info(
            list_info=TeamScraper.INFO_NAMES,
            key_left="gi_left",
            key_right="gi_right")
        dict_info["general_info"]["short_name"] = self._get_short_name()
        dict_info["stadium_info"] = self.get_dict_info(
            list_info=TeamScraper.STADIUM_INFO_NAMES,
            key_left="si_left",
            key_right="si_right")
        dict_info["affiliated_teams"] = self.get_affiliated_teams()
        dict_info["retired_numbers"] = self.get_retired_numbers()
        dict_info["titles"] = self.get_historic_names()
        dict_info["general_info"]["u_id"] = int(re.findall("team\/([0-9]+)\/",
                                                           self.url)[0])
        return dict_info

    def get_dict_info(self, list_info, key_left, key_right):
        """wrapper function for downloading all of the general info """
        dict_ = {}
        for info in list_info:
            dict_[info] = self._get_info(
                info=info, key_left=key_left, key_right=key_right)
        return dict_

    def _get_short_name(self):
        """wrapper function for downloading short name of team - must be always present on the webpage"""

        short_name = (self.selector
                      .xpath(TeamScraper.GI_PATHS["short_name"])
                      .getall())
        if short_name == []:
            raise Exception("team html not downloaded")
        else:
            short_name = short_name[0].strip()
        return short_name

    def _get_info(self, info, key_left, key_right):
        """general function for downloading individual general info values"""

        info_path_val = (TeamScraper.INFO_PATHS[key_left] 
                         + info 
                         + TeamScraper.INFO_PATHS[key_right])
        info_val = self.selector.xpath(info_path_val).getall()
        info_val = [string.strip() for string in info_val]
        info_val = [string for string in info_val if string != ""]
        if info_val == []:
            info_val = [None]
        return info_val[0]

    def get_affiliated_teams(self):
        dict_at = {}
        dict_at = (self.selector
                   .xpath(TeamScraper.OTHER_PATHS["affiliated_teams"])
                   .getall())
        return dict_at

    def get_retired_numbers(self):
        dict_num = {}
        path_url = TeamScraper.OTHER_PATHS["retired_num"] + "@href"
        path_num = TeamScraper.OTHER_PATHS["retired_num"] + "text()"
        urls = self.selector.xpath(path_url).getall()
        numbers = self.selector.xpath(path_num).getall()
        for ind in range(len(urls)):
            dict_num[urls[ind]] = numbers[ind].strip()
        return dict_num

    def get_historic_names(self):
        n_names = (self.selector
                   .xpath(TeamScraper.HN_PATHS["num_titles"])
                   .getall()[0])
        n_names = int(float(n_names))
        n_lines = (self.selector
                .xpath(TeamScraper.HN_PATHS["num_lines"])
                .getall()[0])
        n_lines = int(float(n_lines))
        title_positions = []
        titles = self.selector.xpath(TeamScraper.HN_PATHS["titles"]).getall()
        titles = [title.strip() for title in titles]
        for ind in range(1, n_names + 1):
            path1 = (TeamScraper.HN_PATHS["name_left"]
                     + str(ind)
                     + TeamScraper.HN_PATHS["name_right"])
            n_following = self.selector.xpath(path1).getall()[0]
            n_following = int(float(n_following))
            title_position = n_lines - n_following
            title_positions.append(title_position)
        if title_positions == []:
            n_names = 1
            titles = ["-"]
            title_positions = [0]
        title_positions.append(n_lines + 1)
        dict_titles = {}
        count = title_positions[0]
        for ind in range(1, n_names + 1):
            list_years = []
            while True:
                count += 1
                if count in title_positions:
                    break
                path_season = (TeamScraper.HN_PATHS["season_l"]
                               + str(count)
                               + TeamScraper.HN_PATHS["season_r"])
                season = self.selector.xpath(path_season).getall()
                if season != []:
                    list_years.append(season[0])
            if list_years == []:
                continue
            dict_titles[titles[ind-1]] = {}
            dict_titles[titles[ind-1]]["min"] = list_years[0]
            dict_titles[titles[ind-1]]["max"] = list_years[len(list_years)-1]
        return dict_titles
