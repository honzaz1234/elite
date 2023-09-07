import re
import datetime

from constants import *

class UpdatePlayer:

    def __init__(self, is_goalie):
        self.is_goalie = is_goalie



    def update_player_dict(self, dict):
        is_goalie = self.check_goalie(dict)
        info_updater = player_info.UpdatePlayerInfo(is_goalie=is_goalie)
        dict_info = dict["info"]
        dict["info"] = info_updater.update_info_dict(dict_info)
        stats_updater = player_stats.UpdatePlayerStats(is_goalie=is_goalie)
        dict_stats = dict["stats"]
        dict["stats"] = stats_updater.update_stats_dict(dict_stats)
        dict["u_id"] = int(dict["u_id"])
        return dict
    

class UpdatePlayerInfo():

    HEIGHT_REGEX = "([0-9]+)\scm"
    WEIGHT_REGEX = "([0-9]+)\skg"
    CAP_HIT_REGEX = "[^0-9]"
    DAY_REGEX = "([0-9]+),"
    MONTH_REGEX = "^([A-Za-z]+)\s"
    YEAR_REGEX = "[0-9]+$"

    DELETE_KEYS = [BIRTH_PLACE_STRING, DRAFTED, NHL_RIGHTS]

    NHL_UID = {
        'Boston Bruins': 52,
        'Toronto Maple Leafs': 76,
        'Tampa Bay Lightning': 75,
        'Florida Panthers': 62,
        'Buffalo Sabres': 53,
        'Ottawa Senators': 69,
        'Detroit Red Wings': 60,
        'Montréal Canadiens': 64,
        'Carolina Hurricanes': 55,
        'New Jersey Devils': 66,
        'New York Rangers': 68,
        'New York Islanders': 67,
        'Pittsburgh Penguins': 71,
        'Washington Capitals': 78,
        'Philadelphia Flyers': 70,
        'Columbus Blue Jackets': 58,
        'Colorado Avalanche': 57,
        'Dallas Stars': 59,
        'Minnesota Wild': 63,
        'Winnipeg Jets': 9966,
        'Nashville Predators': 65,
        'St. Louis Blues': 74,
        'Arizona Coyotes': 72,
        'Chicago Blackhawks': 56,
        'Vegas Golden Knights': 22211,
        'Edmonton Oilers': 61,
        'Los Angeles Kings': 79,
        'Seattle Kraken': 27336,
        'Calgary Flames': 54,
        'Vancouver Canucks': 77,
        'San Jose Sharks': 73,
        'Anaheim Ducks': 1580,
        'Phoenix Coyotes': 72,
        'Atlanta Thrashers': 51,
        'Mighty Ducks of Anaheim': 1580,
        'Hartford Whalers': 546,
        'Québec Nordiques': 544,
        'Minnesota North Stars': 543,
        'Chicago Black Hawks': 56,
        'Colorado Rockies': 769,
        'Atlanta Flames': 767,
        'Cleveland Barons': 96,
        'California Golden Seals': 1815,
        'Kansas City Scouts': 3314,
        'Oakland Seals': 1815,
        'California/Oakland Seals': 1815,
        'Brooklyn Americans': 3029,
        'New York Americans': 3029,
        'Montréal Maroons': 3284,
        'St. Louis Eagles': 11424,
        'Ottawa HC (Senators)': 69,
        'Detroit Falcons': 60,
        'Philadelphia Quakers': 5942,
        'Detroit Cougars': 60,
        'Pittsburgh Pirates': 7287,
        'Toronto St. Patricks/Maple Leafs': 76,
        'Toronto St. Patricks': 76,
        'Hamilton Tigers': 3196,
        'Québec Athletic Club': 3194,
        'Toronto Hockey Club': 76,
        'Montréal Wanderers': 3264
    }

    MONTHS = {
        "Jan": 1, 
        "Feb": 2, 
        "Mar": 3, 
        "Apr": 4,
        "May": 5, 
        "Jun": 6, 
        "Jul": 7, 
        "Aug": 8,
        "Sep": 9, 
        "Oct": 10, 
        "Nov": 11, 
        "Dec": 12
    }

    def __init__(self, is_goalie):
        self.is_goalie = is_goalie


    def _update_status(self, active, age):
        """method for updating status of player(active/retired)
        the value is present on the player webpage only if he is retired and alive, so if the value returned in scraping part of the project is not none it means that he is is retired, similiarly if the value is not present and the age value is also not present it means that the player is no longer alive, otherwise player is active
        """

        if active is not None:
            return False
        elif age is not None:
            return True
        else:
            return False
        

    def _update_nationality(self, nation_list):
        """method for filtering out the / from the list of nationalities"""

        for nation in nation_list:
            if nation == "/":
                nation_list.remove(nation)
        return nation_list

    
    def _update_physical_char(self, char, regex):
        """method for updating value of height and weight; in both cases there 2 different metrics availaible on the website (kg/lbs) and (cm/inch);
        this methods keeps the kg and cm values
        """

        if char == None:
            return None
        updated_char = re.findall(regex, char)
        if updated_char != []:
            return updated_char[0]
        else:
            return None

    def _create_draft_info_dict(self, draft_list):
        dict_draft = {}
        if draft_list == [None]:
            return {}
        for ind in range(len(draft_list)):
            if draft_list[ind] == None:
                continue
            one_draft_dict = self._get_one_draft_info(
                draft_string=draft_list[ind])
            dict_draft[ind] = one_draft_dict
        return dict_draft
    
    def _update_draft_status(self, draft_list):
        """create value describing if the player was drafted or not"""

        if draft_list == [None]:
            return False
        else:
            return True
    
    def _get_one_draft_info(self, draft_string):
            """method for creating dict with draft info"""

            draft_dict = {}
            draft_dict[DRAFT_YEAR] = re.findall(
                "^([0-9]+)\s", draft_string)
            draft_dict[DRAFT_ROUND] = re.findall(
                "round\s([0-9]+)\s", draft_string)
            draft_dict[DRAFT_POSITION] = re.findall(
                "#([0-9]+)\s", draft_string)
            draft_dict[DRAFT_TEAM] = re.findall(
                "by\s(.+)$", draft_string)
            draft_dict[TEAM_UID] = (UpdatePlayerInfo
            .NHL_UID[draft_string[DRAFT_TEAM]])
            return draft_dict
    
    def _create_place_birth_dict(self, birth_string):
        """place of birth string scraped from player webpage consists of 2 or 3 values; town and country or town region and country in case Canada or USA; the ranking of these 3 values is always the same:
        on the first position is place, followed by region and finally country all separated by ,
        """

        birthplace_dict = {}
        if  "," not in birth_string:
            birthplace_dict[BIRTH_COUNTRY] = None
            birthplace_dict[BIRTH_REGION] = None
            birthplace_dict[BIRTH_PLACE] = None
            return birthplace_dict
        list_place = birth_string.split(", ")
        birthplace_dict[BIRTH_PLACE] = list_place[0]
        if len(list_place) == 2:
            birthplace_dict[BIRTH_COUNTRY] = list_place[1]
            birthplace_dict[BIRTH_REGION] = None
        if len(list_place) == 3:
            birthplace_dict[BIRTH_COUNTRY] = list_place[2]
            birthplace_dict[BIRTH_REGION] = list_place[1]
        return birthplace_dict

    def _update_cap_hit(self, cap_hit):
        """update player cap hit to number"""

        if cap_hit == None:
            return None
        updated_cap_hit = re.sub(UpdatePlayerInfo.CAP_HIT_REGEX, "", cap_hit)
        return updated_cap_hit

    def _get_nhl_rights_uid(self, nhl_rights):
        """attain uid of team that owns player nhl rights"""

        team_rights = self._get_nhl_rights_info(
                nhl_rights=nhl_rights, ind=0)
        team_uid = UpdatePlayerInfo.NHL_UID[team_rights]
        return team_uid
    
    def _get_nhl_signed_status(self, nhl_rights):
        """get value describing if the player is signed by nhl team"""

        signed_string = self._get_nhl_rights_info(
                nhl_rights=nhl_rights, ind=1)
        if signed_string == "Signed":
            return True
        else:
            return False

    def _get_nhl_rights_info(self, nhl_rights, ind):
        """function to attain info (team name or signed/unsigned)
        from nhl rights string
        """

        if nhl_rights is None:
            return None
        nhl_rights_list = nhl_rights.split(" / ")
        info_rights = nhl_rights_list[ind]
        return info_rights
            
    def _update_birth_date(self, date_string):
        """creates date object from string"""

        if date_string is None:
            return None
        month_name = re.findall(UpdatePlayerInfo.MONTH_REGEX, date_string)
        if month_name == []:
            return None
        month_name = month_name[0]
        month_num = UpdatePlayerInfo.MONTHS[month_name]
        day = re.findall(UpdatePlayerInfo.DAY_REGEX, date_string)
        if day == []:
            return None
        day = int(day[0])
        year = re.findall(UpdatePlayerInfo.YEAR_REGEX, date_string)
        if year == []:
            return None
        year = int(year[0])
        new_date = datetime.date(year, month_num, day)
        return new_date

    def _update_age(self, age):
        """updates value of age"""

        if age == None:
            return None
        elif age == "-" or age == "PREMIUM":
            age = None

    def _update_info_dict_individual_vals(self, info_dict):
        """wraper for all methods updating single values in dict"""

        info_dict_updated = info_dict.copy()
        info_dict_updated[ACTIVE] = self._update_status(
            active=info_dict[ACTIVE], age=info_dict[AGE])
        info_dict_updated[NATIONALITY] = self._update_nationality(
            info_dict[NATIONALITY])
        info_dict_updated[HEIGHT] = self._update_physical_char(
            char=info_dict[HEIGHT], 
            regex=UpdatePlayerInfo.HEIGHT_REGEX)
        info_dict_updated[WEIGHT] = self._update_physical_char(
            char=info_dict[WEIGHT], 
            regex=UpdatePlayerInfo.WEIGHT_REGEX)
        info_dict_updated[DRAFTED] = self._update_draft_status(
            draft_list=info_dict[DRAFT_LIST])
        info_dict_updated[DRAFTS] = self._create_draft_info_dict(
            draft_list=info_dict[DRAFT_LIST])
        info_dict_updated[BIRTH_PLACE_DICT] = self._create_place_birth_dict(
            birth_string=info_dict[BIRTH_PLACE_STRING])
        info_dict_updated[CAP_HIT] = self._update_cap_hit(cap_hit=info_dict[CAP_HIT])
        info_dict_updated[NHL_RIGHTS_UID] = self._get_nhl_rights_uid(
            nhl_rights=info_dict[NHL_RIGHTS])
        info_dict_updated[SIGNED_NHL] = self._get_nhl_signed_status(
            nhl_rights=info_dict[NHL_RIGHTS])
        info_dict_updated[BIRTH_DATE] = self._update_birth_date(
            date_string=info_dict[BIRTH_DATE])
        info_dict_updated[AGE] = self._update_age(
            age=info_dict[AGE])
        return info_dict_updated
    
    def _update_missing_values(self, info_dict):
        """update missing values in dict to None"""

        for key in info_dict:
            if info_dict[key] == "-" or info_dict[key] == "":
                info_dict[key] = None
        return info_dict
    
    def _delete_redundant_keys(self, info_dict):
        """delete keys that are unecessary to keep in the dict"""

        new_info_dict = info_dict.copy
        for key in UpdatePlayerInfo.DELETE_KEYS:
            del  new_info_dict[key]
        return new_info_dict

    def _update_info_dict(self, info_dict):
        """wraper method for all the changes in the info dict"""

        info_dict_vals = self._update_info_dict_individual_vals(
            info_dict=info_dict)
        info_dict_miss = self._update_missing_values(
            info_dict=info_dict_vals)
        info_dict_final = self._delete_redundant_keys(
            info_dict=info_dict_miss) 
        return info_dict_final

 
class UpdateRelations():

    def __init__(self):
            pass

    def _update_relation_dict(self, relation_dict):
        new_relation_dict = self._relations_to_lower(relation_dict)
        new_relation_dict_2 = self._relation_uids_to_int(new_relation_dict)
        return new_relation_dict_2  

    def _relations_to_lower(self, relation_dict):
        for relation_type in relation_dict:
            new_key = relation_type.lower()
            relation_dict[new_key] = relation_dict[relation_type]
        return relation_dict
    
    def _relation_uids_to_int(self, relation_dict):
        for relation_type in relation_dict:
            list_u_id = relation_dict[relation_type]
            new_list = []
            for u_id in list_u_id:
                new_u_id = int(u_id)
                new_list.append(new_u_id)
            relation_dict[relation_type] = new_list
        return relation_dict

    


