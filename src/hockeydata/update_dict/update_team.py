import re
from hockeydata.constants import * 


class UpdateTeamDict():


    INT_KEYS = [YEAR_FOUNDED, CAPACITY, CONSTRUCTION_YEAR]
    RETIRED_NUM_REGEX = "#([0-9]+)"
    
    def __init__(self):
        pass

    def update_team_dict(self, dict: dict) -> dict:
        """wraper function for updating team dict in order to prepared it for insertion into the database
        """

        new_dict = dict.copy()
        new_dict[GENERAL_INFO] = self._update_general_info(
            gi_dict=new_dict[GENERAL_INFO])
        new_dict[HISTORIC_NAMES] = self._update_historic_name(
            dict_titles=new_dict[HISTORIC_NAMES], 
            short_name=new_dict[GENERAL_INFO][SHORT_NAME])
        new_dict[STADIUM_INFO] = self._update_stadium_info(
            si_dict=new_dict[STADIUM_INFO])
        new_dict[RETIRED_NUMBERS] = self._update_retired_numbers(
            num_dict=new_dict[RETIRED_NUMBERS])
        new_dict[AFFILIATED_TEAMS] = self.update_urls(
            list_url=new_dict[AFFILIATED_TEAMS], regex=TEAM_UID_REGEX)
        return new_dict
        
    def _update_general_info(self, gi_dict: dict) -> dict:
        """wraper method for updating general info dict in order to prepare for insertion into db
        """

        gi_dict_new = gi_dict.copy()
        gi_dict_new[PLACE_DICT] = self._create_place_dict(
            place_string=gi_dict_new[PLACE])
        gi_dict_new[COLOUR_LIST] = self._update_colours(
            colour_string=gi_dict_new[TEAM_COLOURS])
        gi_dict_new[ACTIVE] = self._update_status(
            leagues=gi_dict_new[PLAYS_IN])
        gi_dict_new = self._update_missing_values(
            dict=gi_dict_new)
        gi_dict_new = self._update_numbers(dict=gi_dict_new)
        del gi_dict_new[PLACE]
        return gi_dict_new
    
    def _update_stadium_info(self, si_dict: dict) -> dict:
        """wraper method for updating stadium info dict in order to prepare for insertion into db"""


        si_dict_new = si_dict.copy()
        si_dict_new[PLACE_DICT] = self._create_place_dict(
            place_string=si_dict_new[LOCATION])
        si_dict_new = self._update_missing_values(dict=si_dict_new)
        si_dict_new = self._update_numbers(dict=si_dict_new)
        del si_dict_new[LOCATION]
        return si_dict_new
        

    def _create_place_dict(self, place_string: str|None) -> dict:
        """place of birth string scraped from player webpage consists of 2 or 3 values; town and country or town region and country in case Canada or USA; the ranking of these 3 values is always the same:
        on the first position is place, followed by region and finally country all separated by , 
        on a rare occasions, only a name of (US or CAN) region is mentioned with the country being explicitly stated
        """

        dict_place = {}
        no_val = False
        if place_string is None:
            no_val = True
        elif "," not in place_string:
            no_val = True
        if no_val == True:
            dict_place[COUNTRY] = None
            dict_place[REGION] = None
            dict_place[PLACE] = None
            return dict_place
        list_place = place_string.split(",")
        dict_place[PLACE] = list_place[0]
        if len(list_place) == 2 and len(list_place[1]) == 2:
            if list_place[1] in NA_REGION_ABB["USA"]:
                dict_place[REGION] = list_place[1].strip()
                dict_place[COUNTRY] = "USA"
            elif list_place[1] in NA_REGION_ABB["CAN"]:
                dict_place[REGION] = list_place[1].strip()
                dict_place[COUNTRY] = "CAN"
            else:
                dict_place[COUNTRY] = list_place[1].strip()
                dict_place[REGION] = None
        elif len(list_place) == 2:
            dict_place[COUNTRY] = list_place[1].strip()
            dict_place[REGION] = None
        elif len(list_place) == 3:
            dict_place[COUNTRY] = list_place[2].strip()
            dict_place[REGION] = list_place[1].strip()
        return dict_place

    def update_urls(self, list_url: list, regex: str) -> dict:
        """creates dict from list where keys are regex matches and values are original values
        """

        dict_url = {}
        for url in list_url:
            u_id = re.findall(regex, url)[0]
            dict_url[u_id] = url
        return dict_url

    def _update_numbers(self, dict_: dict) -> dict:
        """method for updating string integers to integers"""

        for key in dict_:
            if key in UpdateTeamDict.INT_KEYS:
                if dict_[key] is None:
                    continue
                else:
                    new_int = (re.sub("\s", "", dict_[key]))
                    new_int = re.findall("[0-9]+", new_int)
                    if new_int != []:
                        new_int = int(new_int[0])
                    else:
                        new_int = None
                    dict_[key] = new_int
        return dict_

    def _update_colours(self, colour_string: str|None) -> list:
        """method for creating list of colours from string"""

        if colour_string == None:
            return []
        colour_list = colour_string.split(" + ")
        return colour_list

    def _update_status(self, leagues: str) -> int:
        """method for asserting if team is active (participates in some competition or not)
        """

        if leagues == NA:
            return 0
        else:
            return 1

    def _update_missing_values(self, dict_: dict) -> dict:
        """method for updating values equal to - to None"""
        for key in dict_:
            if dict_[key] == NA:
                dict_[key] = None
        return dict_

    def _update_historic_name(self, dict_titles: dict, short_name: str) -> dict:
        """in case team had only one name throught the history, the name is not mentioned in the table with historical standings from which the names are taken; in that case, the name is set to the short name from general info dict
        """

        dict_titles_new = dict_titles.copy()
        if len(dict_titles_new) == 1:
            for key in list(dict_titles_new.keys()):
                if key == NA:
                    dict_titles_new[short_name] = dict_titles_new[key]
                    del dict_titles_new[key]
        return dict_titles_new

    def _update_retired_numbers(self, num_dict: dict) -> dict:
        """method for creating dict where keys are players uids and values are list where on the first position is the number and on the second position is player uid
        """

        new_num_dict = num_dict.copy()
        for url_key in list(new_num_dict.keys()):
            u_id = int(re.findall(PLAYER_UID_REGEX, url_key)[0])
            new_number = int(re.findall(
                UpdateTeamDict.RETIRED_NUM_REGEX, new_num_dict[url_key])[0])
            new_dict = [new_number, url_key]
            new_num_dict[u_id] = new_dict
            del new_num_dict[url_key]
        return new_num_dict

