import re
import requests
import scrapy
from hockeydata.constants import *


class TeamScraper():
    """class for downloading data from team webpage;
    there are methods available for downloading general info, stadium info, affiliated teams, retired numbers and historic names
    """

    INFO_PATHS = {

        "short_name": "//h1[@class='Profile_headerMain__uA_uQ']/text()",
        "gi_left": "//div[@id='team-facts']"
                             "//td[preceding-sibling::"
                             "th[contains(text(),'",
        "gi_right": "')]]//text()",
        "si_left": "//div[@id='team-arena']"
                             "//td[preceding-sibling::"
                             "th[contains(text(),'",
        "si_right": "')]]//text()"
    }
    
    OTHER_PATHS = {
        "affiliated_teams": "//div[preceding-sibling::span[contains(text()"
                            ", 'Affiliated Team(s)')]]//li/a/@href",
        "retired_num": "//div[@id='team-retired-player']//ul/li"
    }

    URL_SECTIONS = {
        "history": "?team-history=complete#team-history"
    }

    INFO_NAMES = ["Plays in", "Team colors", "Town", "Founded", "Full name"]
    STADIUM_INFO_NAMES = ["Arena Name", "Location", "Capacity", 
                          "Construction Year"]
    WEB_MAPPING = {
        "Plays in": PLAYS_IN, 
        "Team colors": TEAM_COLOURS,
        "Town": PLACE, 
        "Founded": YEAR_FOUNDED, 
        "Full name": LONG_NAME,
        "Arena Name": ARENA_NAME,
        "Location": LOCATION,
        "Capacity": CAPACITY,
        "Construction Year": CONSTRUCTION_YEAR
        } 

    def __init__(self, url: str):
        self.url = url + TeamScraper.URL_SECTIONS["history"]
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_info(self) -> dict:
        """ wrapper function for downloading all of the info from one team webpage"""

        dict_info = {}
        dict_info[GENERAL_INFO] = self.get_general_info_dict()
        dict_info[STADIUM_INFO] = self.get_dict_info(
            list_info=TeamScraper.STADIUM_INFO_NAMES,
            key_left="si_left", key_right="si_right")
        dict_info[AFFILIATED_TEAMS] = self.get_affiliated_teams()
        dict_info[RETIRED_NUMBERS] = self.get_retired_numbers()
        hist_names = HistoricNames(selector=self.selector)
        dict_info[HISTORIC_NAMES] = hist_names.get_historic_names_dict()
        return dict_info

    def get_general_info_dict(self) -> dict:
        """wrapper function for getting all information 
        in the general info dict"""

        gi_dict = self.get_dict_info(
            list_info=TeamScraper.INFO_NAMES,
            key_left="gi_left", key_right="gi_right")
        gi_dict[SHORT_NAME] = self._get_short_name()
        gi_dict[TEAM_UID] = int(re.findall(TEAM_UID_REGEX,
                                        self.url)[0])
        return gi_dict
           
    def get_dict_info(
            self, list_info: list, key_left: str, key_right: str
            ) -> dict:
        """wrapper method for downloading all of the general info"""

        dict_ = {}
        for info in list_info:
            dict_key = TeamScraper.WEB_MAPPING[info]
            dict_[dict_key] = self._get_info(
                info=info, key_left=key_left, key_right=key_right)
        return dict_

    def _get_short_name(self) -> str:
        """wrapper method for downloading short name of team - must be always present on the webpage
        """

        short_name = (self.selector
                      .xpath(TeamScraper.INFO_PATHS["short_name"])
                      .getall())
        if short_name == []:
            raise Exception("team html not downloaded")
        else:
            short_name = short_name[0].strip()
        return short_name

    def _get_info(self, info: str, key_left: str, key_right: str) -> int|str|list:
        """general method for downloading individual general info values"""

        info_path_val = (TeamScraper.INFO_PATHS[key_left] 
                         + info 
                         + TeamScraper.INFO_PATHS[key_right])
        info_val = self.selector.xpath(info_path_val).getall()
        info_val = [string.strip() for string in info_val]
        info_val = [string for string in info_val if string != ""]
        if info_val == []:
            info_val = [None]
        return info_val[0]

    def get_affiliated_teams(self) -> list:
        """returns list of urls of affiliated team"""

        list_at = []
        list_at = (self.selector
                   .xpath(TeamScraper.OTHER_PATHS["affiliated_teams"])
                   .getall())
        return list_at

    def get_retired_numbers(self) -> dict:
        """returns dicitonary where keys are urls of pages of players which number was retired for the given team and values are the number that was retired
        """

        dict_num = {}
        path_url = TeamScraper.OTHER_PATHS["retired_num"] + "//a/@href"
        path_num = TeamScraper.OTHER_PATHS["retired_num"] + "/span/text()"
        urls = self.selector.xpath(path_url).getall()
        numbers = self.selector.xpath(path_num).getall()
        for ind in range(len(urls)):
            dict_num[urls[ind]] = numbers[ind].strip()
        return dict_num

class HistoricNames():
    """FOR TIME BEING DEPRECIATED - team info website changed to dynamic - table with historic names can not be longer downloaded with requests library;
    class for creating dictionary with team historic names and season range in which these names where used"""

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
                       " team-history-and-standings'])[1]"
                       "//tr[@class='title']/td/text()",
        "name_left": "count((//div[@class='content_left']"
                     "//table[@class ='table table-striped "
                     "team-history-and-standings'])[1]"
                     "/tbody/tr[@class='title'][",
        "name_right": "]/following-sibling::tr)"
    }

    def __init__(self, selector: scrapy.Selector):
        self.selector = selector
        pass

    def get_num_names(self) -> int:
        """creates list with number of unique names that team had in history according to the table with seasonal standings"""

        n_names = (self.selector
                .xpath(HistoricNames.HN_PATHS["num_titles"])
                .getall()[0])
        n_names = int(float(n_names))
        return n_names
    
    def get_num_lines(self) -> int:
        """get number of lines in table with seasonal standings"""

        n_lines = (self.selector
            .xpath(HistoricNames.HN_PATHS["num_lines"])
            .getall()[0])
        n_lines = int(float(n_lines))
        return n_lines

    def get_team_names(self) -> list:
        """creates list with unique names that team had in history according to the table with seasonal standings
        if the same team name occurs more than once the number of its occurence is added to the end of the name
        """

        names = self.selector.xpath(HistoricNames.HN_PATHS["titles"]).getall()
        names = [name.strip() for name in names]
        names_wo_duplicates = []
        occ_count = {}
        for name in names:
            occ_count[name] = 1
        for name in names:
            if name in names_wo_duplicates:
                occ_count[name] += 1
                name =  name + " (" + str(occ_count[name]) + ")"
            names_wo_duplicates.append(name)
        return names_wo_duplicates
    
    def get_title_position(self, n: int, n_lines: int) -> int:
        """gets index of row on which the nth name is located"""

        path1 = (HistoricNames.HN_PATHS["name_left"]
                + str(n)
                + HistoricNames.HN_PATHS["name_right"])
        n_following = self.selector.xpath(path1).getall()[0]
        n_following = int(float(n_following))
        title_position = n_lines - n_following
        return title_position
    
    def get_title_positions(self, n_names: int, n_lines: int) -> list:
        """creates a list with all the positions of team names in the table"""

        title_positions = []
        for ind in range(1, n_names + 1):
            title_position = self.get_title_position(n=ind, n_lines=n_lines)
            title_positions.append(title_position)
        title_positions.append(n_lines + 1)
        return title_positions
    
    def get_season(self, n: int) -> list:
        """gets the season of nth row of the table"""

        path_season = (HistoricNames.HN_PATHS["season_l"]
                        + str(n)
                        + HistoricNames.HN_PATHS["season_r"])
        season = self.selector.xpath(path_season).getall()
        return season

    def get_historic_names_dict(self) -> dict:
        """creates dictionary where keys are the unique team names
        and values are again dictionaries with season range in which team had this name;
        when the team did not changed its name over its history it can not be found in the table, in that case short name from general info dictionary is assigned to this dictionary in update_dict module
        """

        n_names = self.get_num_names()
        n_lines = self.get_num_lines()
        print([n_names, n_lines])
        if n_names == 0:
            n_names = 1
            team_names = ["-"]
            names_positions = [0]
        else:
            team_names = self.get_team_names()
            print(team_names)
            names_positions = self.get_title_positions(
            n_lines=n_lines, n_names=n_names)
            print(names_positions)
        dict_titles = {}
        row_ind = names_positions[0]
        for ind in range(1, n_names + 1):
            list_years = []
            while True:
                row_ind += 1
                if ((row_ind in names_positions) or (row_ind > n_lines)):
                    break
                season = self.get_season(n=row_ind)
                if season != []:
                    list_years.append(season[0])
            if list_years == []:
                continue
            dict_titles[team_names[ind-1]] = {}
            dict_titles[team_names[ind-1]]["min"] = list_years[0]
            dict_titles[team_names[ind-1]]["max"] = list_years[len(list_years)-1]
        return dict_titles
