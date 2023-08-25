import re
import datetime

class UpdatePlayerInfo:

    month_names = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, 
                   "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, 
                   "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    
    nhl_uid = {
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
        'Montréal Wanderers': 3264}


    def __init__(self, is_goalie ):
        self.is_goalie = is_goalie

    def _update_status(self, info_dict):
        if info_dict["Status"] is not None:
            return info_dict
        elif info_dict["Age"] is not None:
            info_dict["Status"] = "Active"
        else:
            info_dict["Status"] = "Retired"
        return info_dict
    
    def _add_active(self, info_dict):
        if info_dict["Status"] == "Active":
            info_dict["Active"] = True 
        else:
            info_dict["Active"] = False
        return info_dict

    def _resolve_status(self, info_dict):
        info_dict = self._update_status(info_dict)
        info_dict = self._add_active(info_dict)
        del info_dict["Status"]
        return info_dict 

    def _update_height(self, info_dict):
        if "Height" not in info_dict:
            return info_dict
        updated_height = re.findall("([0-9]+)\scm", info_dict["Height"])
        if updated_height != []:
            info_dict["Height"] = int(updated_height[0])
        else:
            info_dict["Height"] =  None
        return info_dict

    def _update_weight(self, info_dict):
        if "Weight" not in info_dict:
            return info_dict
        updated_weight = re.findall("([0-9]+)\skg", info_dict["Weight"])
        if updated_weight != []:
            info_dict["Weight"] = int(updated_weight[0])
        else:
            info_dict["Weight"] = None
        return info_dict
    
    def _update_draft_info(self, info_dict):
        dict_draft = {}
        print(info_dict)
        if info_dict["Drafted"] == [None]:
            info_dict["Drafted"] = False
            info_dict["draft_info"]={}
            return info_dict
        for ind in range(len(info_dict["Drafted"])):
            if info_dict["Drafted"][ind] == None:
                continue
            draft_info = info_dict["Drafted"][ind]
            one_draft = {}
            draft_year = re.findall("^([0-9]+)\s", draft_info)
            draft_round = re.findall("round\s([0-9]+)\s", draft_info)
            draft_position = re.findall("#([0-9]+)\s", draft_info)
            draft_team = re.findall("by\s(.+)$", draft_info)
            one_draft["draft_year"] = int(draft_year[0])
            one_draft["draft_round"] = int(draft_round[0])
            one_draft["draft_position"] = int(draft_position[0])
            one_draft["draft_team"] = draft_team[0]
            one_draft["team_uid"] = UpdatePlayerInfo.nhl_uid[one_draft["draft_team"]]
            dict_draft[ind] = one_draft
        info_dict["draft_info"] = dict_draft
        info_dict["Drafted"] = True
        return info_dict
    
    def _update_place_birth(self, info_dict):
        if "Place of Birth" not in info_dict or "," not in info_dict["Place of Birth"]:
            info_dict["Birth_Country"] = None
            info_dict["Birth_Region"] = None
            info_dict["Birth_Place"] = None
            return info_dict
        list_place = info_dict["Place of Birth"].split(", ")
        info_dict["Birth_Place"] = list_place[0]
        if len(list_place) == 2:
            info_dict["Birth_Country"] = list_place[1]
            info_dict["Birth_Region"] = None
        if len(list_place) == 3:
            info_dict["Birth_Country"] = list_place[2]
            info_dict["Birth_Region"] = list_place[1]
        del info_dict["Place of Birth"]
        return info_dict
    
    def _update_cap_hit(self, info_dict):
        if info_dict["Cap Hit"]  == None:
            return  info_dict
        updated_cap_hit = re.sub("[^0-9]", "", info_dict["Cap Hit"])
        info_dict["Cap Hit"] = int(updated_cap_hit)
        return info_dict
    
    def _update_nhl_rights(self, info_dict):
        if info_dict["NHL Rights"] is None:
            info_dict["nhl_team_rights"] = None
            info_dict["signed_nhl"] = False
            info_dict["nr_uid"] = None
            del info_dict["NHL Rights"]
            return info_dict
        nhl_rights_list = info_dict["NHL Rights"].split(" / ")
        info_dict["nhl_team_rights"] = nhl_rights_list[0]
        info_dict["nr_uid"] = UpdatePlayerInfo.nhl_uid[info_dict["nhl_team_rights"]]
        info_dict["signed_nhl"] = nhl_rights_list[1]
        if info_dict["signed_nhl"] == "Signed":
            info_dict["signed_nhl"] = True
        else:
            info_dict["signed_nhl"] = False
        del info_dict["NHL Rights"]
        return info_dict
    
    def _update_handedness(self, info_dict):
        if self.is_goalie == True:
            info_dict["Shoots"] = "-"
        else:
            info_dict["Catches"] = "-"
        return info_dict
    
    def _update_date_birth(self, info_dict):
        info_dict["date_birth"] = info_dict["Date of Birth"]
        del info_dict["Date of Birth"]
        return info_dict
    
    def _update_contract(self, info_dict):
        if "Contract" not in info_dict:
            info_dict["Contract"] = None
        return info_dict

    def _update_key_names(self, info_dict):
        new_dict = {}
        for key in info_dict:
            new_key = key.replace(" ", "_")
            new_key = new_key.lower()
            new_dict[new_key] = info_dict[key]  
        info_dict = new_dict
        return info_dict
    
    def _update_date_type(self, info_dict):
        if info_dict["date_birth"] is None:
            return info_dict
        orig_date = info_dict["date_birth"]
        month_name = re.findall("^([A-Za-z]+)\s", orig_date)
        if month_name == []:
            info_dict["date_birth"] = None
            return info_dict
        else:
            month_name = month_name[0]
            month_num = UpdatePlayerInfo.month_names[month_name]
        day = re.findall("([0-9]+),", orig_date)
        if day == []:
            info_dict["date_birth"] = None
            return info_dict
        else:
            day = int(day[0])
        year = re.findall("[0-9]+$", orig_date)
        if year == []:
            info_dict["date_birth"] = None
            return info_dict
        else:
            year = int(year[0])
        new_date = datetime.date(year, month_num, day)
        info_dict["date_birth"] = new_date
        return info_dict
    
    def _update_relation_dict(self, info_dict):
        relation_dict = info_dict["relations"]
        for relation_type in list(relation_dict.keys()):
            new_key = relation_type.lower()
            relation_dict[new_key] = relation_dict[relation_type]
            del relation_dict[relation_type]
        for relation_type in relation_dict:
            list_u_id = relation_dict[relation_type]
            new_list = []
            for u_id in list_u_id:
                new_u_id = int(u_id)
                new_list.append(new_u_id)
            relation_dict[relation_type] = new_list




    def _update_age_to_integer(self, info_dict):
        print(info_dict["Age"])
        if info_dict["Age"] == None:
            return info_dict
        elif info_dict["Age"] == "-" or info_dict["Age"] == "PREMIUM":
            info_dict["Age"] = None
            return info_dict
        info_dict["Age"] = int(info_dict["Age"])
        return info_dict
    
    def _update_data_types(self, info_dict):
        info_dict = self._update_date_type(info_dict)
        return info_dict
    
    def _update_missing_values(self, info_dict):
        for key in info_dict:
            if info_dict[key] == "-" or info_dict[key] == "":
                info_dict[key] = None
        return info_dict

    def update_info_dict(self, info_dict):
        info_dict = self._resolve_status(info_dict)
        info_dict = self._update_height(info_dict)
        info_dict = self._update_weight(info_dict)
        info_dict = self._update_draft_info(info_dict)
        info_dict = self._update_place_birth(info_dict)
        info_dict = self._update_contract(info_dict)
        info_dict = self._update_date_birth(info_dict)
        info_dict = self._update_cap_hit(info_dict)
        info_dict = self._update_nhl_rights(info_dict)
        info_dict = self._update_handedness(info_dict)
        info_dict = self._update_age_to_integer(info_dict)
        info_dict = self._update_key_names(info_dict)
        info_dict = self._update_missing_values(info_dict)
        info_dict = self._update_data_types(info_dict)
        info_dict = self._update_relation_dict(info_dict)
        return info_dict





