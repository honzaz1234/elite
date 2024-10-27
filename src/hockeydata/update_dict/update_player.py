import datetime
import re
from hockeydata.constants import *

class UpdatePlayer:

    """class used for updating values in dictionary with data on player in order to prepare it for inserting into DB
    is_goalie - True if player is a goalie, False if he is a field player
    """

    def __init__(self):
        self.is_goalie = None

    def _set_is_goalie(self, dict: dict):

        """method for establishing if the player is goalie or field player; important because of different statistical categories
        """

        position = dict[GENERAL_INFO][POSITION]
        if position == "G":
            self.is_goalie =  True
        else:
            self.is_goalie = False

    def update_player_dict(self, dict: dict) -> dict:
        """wrapper method for updating whole player dict"""

        new_dict = dict.copy()
        self._set_is_goalie(new_dict)
        player_info = UpdatePlayerInfo(is_goalie=self.is_goalie)
        new_dict[GENERAL_INFO] = player_info._update_info_dict(
            info_dict=new_dict[GENERAL_INFO])
        player_stats = UpdatePlayerStats(is_goalie=self.is_goalie)
        new_dict[SEASON_STATS] = player_stats._update_stats_dict(
            dict_stats= new_dict[SEASON_STATS])
        player_relation = UpdateRelations()
        #new_dict[RELATIONS] = player_relation._update_relation_dict(
        #    relation_dict=new_dict[RELATIONS])
        return new_dict
    
class UpdatePlayerInfo():
    """class used for updating values in subdictionary general info"""

    #regexes used to extract specific information from original strings

    HEIGHT_REGEX = "([0-9]+)\scm"
    WEIGHT_REGEX = "([0-9]+)\skg"
    CAP_HIT_REGEX = "[^0-9]"
    DAY_REGEX = "([0-9]+),"
    MONTH_REGEX = "^([A-Za-z]+)\s"
    YEAR_REGEX = "[0-9]+$"

    DRAFT_YEAR_REGEX = "^([0-9]+)\s"
    DRAFT_ROUND_REGEX = "round\s([0-9]+)\s"
    DRAFT_POSITION_REGEX = "#\s([0-9]+)\s"
    DRAFT_TEAM_REGEX = "by\s(.+)$"
    
    #names of keys from dictionary to be deleted before insertion of the dict #into DB

    DELETE_KEYS = [BIRTH_PLACE_STRING, NHL_RIGHTS, DRAFT_LIST]

    #unique identificators of NHL teams

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

    def __init__(self, is_goalie: bool):
        """is_goalie - True if player is a goalie False otherwise"""

        self.is_goalie = is_goalie


    def _update_status(self, active: str, age: str) -> bool:
        """method for updating status of player(active/retired)
        the value is present on the player webpage only if he is retired and alive, so if the value returned in scraping part of the project is not none it means that he is is retired, similiarly if the value is not present and the age value is also not present it means that the player is no longer alive, otherwise player is active
        """

        if active is not None:
            return False
        elif age is not None:
            return True
        else:
            return False
        
    def _update_nationality(self, nation_list: list) -> list:
        """method for filtering out the / symbol from the list of   nationalities
        """

        for nation in nation_list:
            if nation == "/":
                nation_list.remove(nation)
        return nation_list

    def _update_physical_char(self, char: str|None, regex: str) -> int|None:
        """method for updating value of height and weight; in both cases there 2 different metrics availaible on the website (kg/lbs) and (cm/inch);
        this methods keeps the kg and cm values
        """

        if char == None:
            return None
        updated_char = re.findall(regex, char)
        if updated_char != []:
            return int(updated_char[0])
        else:
            return None

    def _create_draft_info_dict(self, draft_list: list) -> dict:
        """wrapper method which creates dict with draft information on player
            in some rare cases player was drafted more than once in NHL
        """

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
    
    def _update_draft_status(self, draft_list: list) -> bool:
        """create value describing if the player was drafted or not"""

        if draft_list == [None]:
            return False
        else:
            return True
    
    def _get_one_draft_info(self, draft_string: str) -> dict:
            """method for creating dict with draft info"""

            draft_dict = {}
            draft_year = re.findall(
                UpdatePlayerInfo.DRAFT_YEAR_REGEX, draft_string)
            draft_dict[DRAFT_YEAR] = int(draft_year[0])
            draft_round = re.findall(
                UpdatePlayerInfo.DRAFT_ROUND_REGEX, draft_string)
            draft_dict[DRAFT_ROUND] = int(draft_round[0])
            draft_position = re.findall(
                UpdatePlayerInfo.DRAFT_POSITION_REGEX, draft_string)
            draft_dict[DRAFT_POSITION]  = int(draft_position[0])
            draft_dict[DRAFT_TEAM] = re.findall(
                UpdatePlayerInfo.DRAFT_TEAM_REGEX, draft_string)[0]
            draft_dict[TEAM_UID] = (UpdatePlayerInfo
                                    .NHL_UID[draft_dict[DRAFT_TEAM]])
            return draft_dict
    
    def _create_place_dict(self, place_string: str|None) -> dict:
        """place of birth string scraped from player webpage consists of 2 or 3 values; town and country or town region and country in case Canada or USA; the ranking of these 3 values is always the same:
        on the first position is place, followed by region and finally country all separated by comma
        on a rare occasions, only a name of (US or CAN) region is mentioned without the country being explicitly stated
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

    def _update_cap_hit(self, cap_hit: str|None) -> str|None:
        """update player cap hit to number"""

        if cap_hit == None:
            return None
        updated_cap_hit = re.sub(UpdatePlayerInfo.CAP_HIT_REGEX, "", cap_hit)
        return int(updated_cap_hit)

    def _get_nhl_rights_uid(self, nhl_rights: str|None) -> int|None:
        """attain uid of team that owns player's nhl rights"""

        if nhl_rights is None:
            return None
        team_rights = self._get_nhl_rights_info(
                nhl_rights=nhl_rights, ind=0)
        team_uid = UpdatePlayerInfo.NHL_UID[team_rights]
        return team_uid
    
    def _get_nhl_signed_status(self, nhl_rights: str|None) -> bool:
        """get value describing if the player is signed by nhl team"""

        signed_string = self._get_nhl_rights_info(
                nhl_rights=nhl_rights, ind=1)
        if signed_string == "Signed":
            return True
        else:
            return False

    def _get_nhl_rights_info(self, nhl_rights: str|None, ind: int) -> str|None:
        """method for attaining info (team name or signed/unsigned)
        from nhl rights string
        """

        if nhl_rights is None:
            return None
        nhl_rights_list = nhl_rights.split(" / ")
        info_rights = nhl_rights_list[ind]
        return info_rights
            
    def _update_birth_date(self, date_string: str|None) -> datetime.date|None:
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

    def _update_age(self, age: str|None) -> int|None:
        """updates value of age"""

        if age == None:
            return None
        elif age == NA or age == "PREMIUM":
            age = None
        else:
            return int(age)

    def _update_info_dict_individual_vals(self, info_dict: dict) -> dict:
        """wrapper for all methods updating single values in dict"""

        info_dict_updated = info_dict.copy()
        info_dict_updated[ACTIVE] = self._update_status(
            active=info_dict[ACTIVE], age=info_dict_updated[AGE])
        info_dict_updated[NATIONALITY] = self._update_nationality(
            info_dict_updated[NATIONALITY])
        info_dict_updated[HEIGHT] = self._update_physical_char(
            char=info_dict_updated[HEIGHT], 
            regex=UpdatePlayerInfo.HEIGHT_REGEX)
        info_dict_updated[WEIGHT] = self._update_physical_char(
            char=info_dict_updated[WEIGHT], 
            regex=UpdatePlayerInfo.WEIGHT_REGEX)
        info_dict_updated[DRAFTED] = self._update_draft_status(
            draft_list=info_dict_updated[DRAFT_LIST])
        info_dict_updated[DRAFTS] = self._create_draft_info_dict(
            draft_list=info_dict_updated[DRAFT_LIST])
        info_dict_updated[PLACE_DICT] = self._create_place_dict(
            place_string=info_dict_updated[BIRTH_PLACE_STRING])
        info_dict_updated[CAP_HIT] = self._update_cap_hit(
            cap_hit=info_dict_updated[CAP_HIT])
        info_dict_updated[NHL_RIGHTS_UID] = self._get_nhl_rights_uid(
            nhl_rights=info_dict_updated[NHL_RIGHTS])
        info_dict_updated[SIGNED_NHL] = self._get_nhl_signed_status(
            nhl_rights=info_dict_updated[NHL_RIGHTS])
        info_dict_updated[BIRTH_DATE] = self._update_birth_date(
            date_string=info_dict_updated[BIRTH_DATE])
        info_dict_updated[AGE] = self._update_age(
            age=info_dict_updated[AGE])
        info_dict_updated[PLAYER_UID] = int(info_dict_updated[PLAYER_UID])
        return info_dict_updated
    
    def _update_missing_values(self, info_dict: dict) -> dict:
        """update missing values in dict to None"""

        for key in info_dict:
            if info_dict[key] == NA or info_dict[key] == "":
                info_dict[key] = None
        return info_dict
    
    def _delete_redundant_keys(self, info_dict: dict) -> dict:
        """delete keys that are unecessary to be kept in the dict"""

        new_info_dict = info_dict.copy()
        for key in UpdatePlayerInfo.DELETE_KEYS:
            del  new_info_dict[key]
        return new_info_dict

    def _update_info_dict(self, info_dict: dict) -> dict:
        """wrapper method for all the changes in the info dict"""

        info_dict_vals = self._update_info_dict_individual_vals(
            info_dict=info_dict)
        info_dict_miss = self._update_missing_values(
            info_dict=info_dict_vals)
        info_dict_final = self._delete_redundant_keys(
            info_dict=info_dict_miss) 
        return info_dict_final

 
class UpdateRelations():
    """method for updating values in relations dictionary"""

    def __init__(self):
            pass

    def _update_relation_dict(self, relation_dict: dict) -> dict:
        """wrapper method for updating relations dictionary"""

        new_relation_dict = self._relations_to_lower(relation_dict)
        new_relation_dict_2 = self._relation_uids_to_int(new_relation_dict)
        return new_relation_dict_2  

    def _relations_to_lower(self, relation_dict: dict) -> dict:
        """methods for converting relation types to lower case"""

        new_dict = {}
        for relation_type in list(relation_dict.keys()):
            new_key = relation_type.lower()
            new_dict[new_key] = relation_dict[relation_type]
        return new_dict
    
    def _relation_uids_to_int(self, relation_dict: dict) -> dict:
        """method for converting uids of relations to integers"""

        for relation_type in relation_dict:
            list_u_id = relation_dict[relation_type]
            new_list = []
            for u_id in list_u_id:
                new_u_id = int(u_id)
                new_list.append(new_u_id)
            relation_dict[relation_type] = new_list
        return relation_dict

    
class UpdatePlayerStats:

    """class for updating dict with player's seasonal stats"""

    #regex used for extracting captaincy info

    CAPTAINCY_REGEX = "[AC]"

    def __init__(self, is_goalie: bool):
        """is_goalie - True if player is a goalie False otherwise"""

        self.is_goalie = is_goalie

    def _update_stats_dict(self, dict_stats: dict) -> dict:
        """method for updating whole dict with player season statistics"""

        new_dict_stats = dict_stats.copy()
        for competition_type in list(new_dict_stats.keys()):
            comptetition_dict = new_dict_stats[competition_type]
            new_competition_dict = self._update_competition_dict(
                competition_dict=comptetition_dict)
            new_dict_stats[competition_type] = new_competition_dict
        return new_dict_stats

    def _update_competition_dict(self, competition_dict: dict) -> dict:
        """method for updating dict for one competition
        (league/tournament)
        """

        competition_dict_new = competition_dict.copy()
        for year_key in list(competition_dict_new.keys()):
            year_dict = competition_dict_new[year_key]
            year_dict_new = self._update_year_dict(year_dict=year_dict)
            competition_dict_new[year_key] = year_dict_new
        return competition_dict_new

    def _update_year_dict(self, year_dict: dict) -> dict:
        """method for updating dict for one season"""

        new_year_dict = year_dict.copy()
        for league_key in list(new_year_dict.keys()):
            league_dict = new_year_dict[league_key]
            league_dict_new = self._update_league_dict(league_dict=league_dict)
            new_year_dict[league_key] = league_dict_new
        return new_year_dict

    def _update_league_dict(self, league_dict: dict) -> dict:
        """method for updating dict for one league"""

        new_league_dict = league_dict.copy()
        if new_league_dict[LEAGUE_URL] is not None:
            league_id = re.findall(LEAGUE_UID_REGEX, 
                                   new_league_dict[LEAGUE_URL])[0]
        else:
            league_id = None
        new_league_dict[LEAGUE_UID] = league_id
        for team_key in list(new_league_dict.keys()):
            if team_key not in [LEAGUE_URL, LEAGUE_UID]:
                team_dict = new_league_dict[team_key]
                new_team_dict = self._update_team_dict(team_dict=team_dict)
                new_league_dict[team_key] = new_team_dict
        return new_league_dict

    def _update_team_dict(self, team_dict: dict) -> dict:
        """method for updating dict for one team"""

        new_team_dict = team_dict.copy()
        team_id = re.findall(
            TEAM_UID_REGEX, new_team_dict[TEAM_URL])[0]
        new_team_dict[TEAM_UID] = int(team_id)
        new_team_dict[LEADERSHIP] = self.update_leadership(
                new_team_dict[LEADERSHIP])
        for season_type in [REGULAR_SEASON, PLAY_OFF]:
            if season_type not in new_team_dict:
                continue
            list_season = new_team_dict[season_type]
            if list_season is None:
                continue
            season_dict = SeasonDict(is_goalie=self.is_goalie)
            stat_dict = season_dict._update_season(season_list=list_season)
            new_team_dict[season_type] = stat_dict
        return new_team_dict

    def update_leadership(self, lead_value: str|None) -> str|None:
        """get rid of quotation marks around A or C letter"""

        if lead_value is None:
            return None
        new_lead_value = re.findall(
            UpdatePlayerStats.CAPTAINCY_REGEX, lead_value)[0]
        return new_lead_value


class SeasonDict():
    """class containing methods for updating season stats from one season"""

    PLAYER_ATT = [GP, G, A, TP, PIM, PLUS_MINUS]
    GOALIE_ATT = [GP, GD, GAA,
                  SVP, GA, SVS, SO, WLT, TOI]
    WLT = [G_W, G_L, G_T]

    def __init__(self, is_goalie):
        self.is_goalie = is_goalie


    def _update_season(self, season_list: list) -> dict:
        """wrapper method for updating season stats of player"""

        if self.is_goalie == True:
            n_att = len(SeasonDict.GOALIE_ATT)
        else:
            n_att = len(SeasonDict.PLAYER_ATT)
        if (
            set(season_list) == {NA} 
            or set(season_list) == {NA, ""} 
            or set(season_list) == set()
            ):
            season_list = [None] * n_att
        if self.is_goalie == True:
            dict_stats = self._update_season_goalkeeper(
                season_list=season_list)
        else:
            dict_stats = self._update_season_player(
                season_list=season_list)
        return dict_stats


    def _update_season_goalkeeper(self, season_list: list) -> dict:
        """update seasonal stat for goalkeeper
        two attributes SVP - save percentage and GAA - goal against average are float numbers, otherwise all statistics are integers 
        """

        dict_stats = {}
        for ind in range(len(season_list)):
            if season_list[ind] == NA:
                    season_list[ind] = None
            if ind == 7:
                dic_wlt = self._w_l_t_to_dict(season_list[ind])
                dict_stats = {**dict_stats, **dic_wlt}
            elif season_list[ind] is None:
                dict_stats[SeasonDict.GOALIE_ATT[ind]
                           ] = season_list[ind]
            elif ind in [2, 3]:
                stat = float(season_list[ind])
                dict_stats[SeasonDict.GOALIE_ATT[ind]] = stat
            else:
                stat = self.stat_to_int(stat=season_list[ind])
                dict_stats[SeasonDict.GOALIE_ATT[ind]] = stat
        return dict_stats

    def _update_season_player(self, season_list: list) -> dict:
        """method for updating stats of player"""

        dict_stats = {}
        for ind in range(len(season_list)):
            if season_list[ind] == NA or season_list[ind] is None:
                stat = None
            else:
                stat = self.stat_to_int(stat=season_list[ind])
            dict_stats[SeasonDict.PLAYER_ATT[ind]] = stat
        return dict_stats

    def _w_l_t_to_dict(self, wlt_string: str|None) -> dict:
        """method for updating stats of goalie"""

        if wlt_string is None:
            return {G_W: None, G_L: None, G_T: None}
        dic_wlt = {}
        stat_list = wlt_string.split("-")
        for ind in range(len(SeasonDict.WLT)):
            dic_wlt[SeasonDict.WLT[ind]] = int(stat_list[ind])
        return dic_wlt
    
    def stat_to_int(self, stat: str) -> int:
            """method for converting stat to integer"""

            stat = re.sub(" ", "", stat)
            stat = int(stat)
            return stat 

