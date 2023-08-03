import re
import datetime

class UpdatePlayerInfo:

    month_names = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, 
                   "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, 
                   "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    def __init__(self, is_goalie ):
        self.is_goalie = is_goalie
        pass

    def _update_status(self, info_dict):
        if "Status"  in info_dict:
            return info_dict
        elif "Age" in info_dict:
            print(info_dict["Age"])
            info_dict["Status"] = "Active"
        else:
            info_dict["Status"] = "Not_Active"
        return info_dict
    
    def _add_active(self, info_dict):
        print(info_dict["Status"])
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
            info_dict["Height"] = updated_height[0]
        else:
            info_dict["Height"] =  None
        return info_dict

    def _update_weight(self, info_dict):
        if "Weight" not in info_dict:
            return info_dict
        updated_weight = re.findall("([0-9]+)\skg", info_dict["Weight"])
        if updated_weight != []:
            info_dict["Weight"] = updated_weight[0]
        else:
            info_dict["Weight"] = None
        return info_dict
    
    def _update_draft_info(self, info_dict):
        if "Drafted" not in info_dict:
            info_dict["Drafted"] = False
            info_dict["Draft_Year"] = None
            info_dict["Draft_Round"] = None
            info_dict["Draft_Position"] = None
            info_dict["Draft_Team"] = None
            return info_dict
        draft_info =  info_dict["Drafted"]
        draft_year = re.findall("^([0-9]+)\s", draft_info)
        draft_round = re.findall("round\s([0-9]+)\s", draft_info)
        draft_position = re.findall("#([0-9]+)\s", draft_info)
        draft_team = re.findall("by\s(.+)$", draft_info)
        info_dict["Draft_Year"] = draft_year[0]
        info_dict["Draft_Round"] = draft_round[0]
        info_dict["Draft_Position"] = draft_position[0]
        info_dict["Draft_Team"] = draft_team[0]
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
        if "Cap Hit" not in info_dict:
            info_dict["Cap Hit"] = None
            return info_dict
        updated_cap_hit = re.sub("[^0-9]", "", info_dict["Cap Hit"])
        info_dict["Cap Hit"] = updated_cap_hit
        return info_dict
    
    def _update_nhl_rights(self, info_dict):
        if "NHL Rights" not in info_dict:
            info_dict["nhl_team_rights"] = None
            info_dict["signed_nhl"] = False
            return info_dict
        nhl_rights_list = info_dict["NHL Rights"].split(" / ")
        info_dict["nhl_team_rights"] = nhl_rights_list[0]
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
        print("orig_date:")
        print(orig_date)
        should_return = False
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

    def _update_to_integer(self, info_dict):
        for key in ["height", "weight", "age", "draft_year", "draft_round", "draft_position", "u_id", "cap_hit"]:
            if info_dict[key] is not None:
                info_dict[key] = int(info_dict[key])
        return info_dict
    
    def _update_data_types(self, info_dict):
        info_dict = self._update_to_integer(info_dict)
        info_dict = self._update_date_type(info_dict)
        return info_dict
    

    def _update_missing_values(self, info_dict):
        for key in info_dict:
            if info_dict[key] == "-" or info_dict[key] == "":
                info_dict[key] = None
        return info_dict


    def update_info_wraper(self, info_dict):
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
        info_dict = self._update_key_names(info_dict)
        info_dict = self._update_missing_values(info_dict)
        info_dict = self._update_data_types(info_dict)
        return info_dict





