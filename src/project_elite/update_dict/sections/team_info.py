import re

class UpdateTeamDict():

    NA_region_abbrevations = {"USA": ["NJ", "CA", "AZ", "OH", "MI", "NY", "NE", "WI", "MA", "FL", "CO", "SC", "MO", "MN", "PA",	
                              "TX",	"CT", "IN",	"WA", "IL", "ME", "AL", "OK", "UT", "OR", "NC", "RI", "NH", "VA", "AK", 	
                              "IA", "MS", "SD", "ND", "MD",	"DE", "NV", "MT", "TN", "VT", "DC", "GA", "ID"],
                              "CAN": ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "ON", "ONT", "PE", "QC", "SK","YT", "NU"]}
    integer_vals = ["founded", "construction_year", "capacity"]
    

    def __init__(self):
        pass

    def update_place(self, place_name):
        dict_place = {}
        if "," not in place_name:
            dict_place["stadium_country"] = None
            dict_place["stadium_region"] = None
            dict_place["stadium_place"] = None
            return dict_place
        list_place = place_name.split(", ")
        dict_place["stadium_place"] = list_place[0]
        if len(list_place) == 2 and len(list_place[1]) == 2:
            if list_place[1] in UpdateTeamDict.NA_region_abbrevations["USA"]:
                dict_place["stadium_region"] = list_place[1] 
                dict_place["stadium_country"] = "USA"
            elif list_place[1] in UpdateTeamDict.NA_region_abbrevations["CAN"]:
                dict_place["stadium_region"] = list_place[1] 
                dict_place["stadium_country"] = "CAN"
        elif len(list_place) == 2:
            dict_place["stadium_country"] = list_place[1]
            dict_place["stadium_region"] = None
        elif len(list_place) == 3:
                dict_place["stadium_country"] = list_place[2]
                dict_place["stadium_region"] = list_place[1]
        return dict_place
    
    def update_key_names(self, dict_info):
        new_dict = {}
        for key in dict_info:
            new_key = key.strip()
            new_key = new_key.lower()
            new_key = re.sub(" ", "_", new_key)
            new_dict[new_key] = dict_info[key]
        return new_dict
    
    def update_urls(self, list_url, regex):
        dict_url = {}
        for url in list_url:
            u_id = re.findall(regex, url)[0]
            dict_url[u_id] = url
        return dict_url
    
    def update_numbers(self, dict_info):
        for key in UpdateTeamDict.integer_vals:
            if dict_info[key] is None:
                return dict_info
            old_val = dict_info[key]
            new_val = re.sub(" ", "", old_val)
            dict_info[key] = int(new_val)
        return dict_info

    def update_status(self, league_names):
        if league_names == "-":
            return 0
        else:
            return 1
        
    def update_NA(self, dict):
        for key in dict:
            if dict[key] == "-":
                dict[key] = None
        return dict
    
    def update_historic_name(self, dict_info):
        hist_names_dict = dict_info["titles"]
        if len(hist_names_dict) == 1:
            for key in list(hist_names_dict.keys()):
                if key == "-":
                    hist_names_dict[dict_info["short_name"]] = hist_names_dict[key]
                    del hist_names_dict[key]
        dict_info["titles"] = hist_names_dict
        return dict_info
        
        
    def update_team_dict_wrap(self, dict_info):
        dict_info = self.update_key_names(dict_info)
        place_dict = self.update_place(place_name=dict_info["town"])
        dict_info = {**dict_info, **place_dict}
        dict_info["affiliated_teams"] = self.update_urls(list_url=dict_info["affiliated_teams"], regex="team\/([0-9]+)")
        dict_info["retired_numbers"] = self.update_urls(list_url=dict_info["retired_numbers"], regex="player\/([0-9]+)")
        dict_info = self.update_NA(dict_info)
        dict_info =  self.update_numbers(dict_info=dict_info)
        dict_info["active"] = self.update_status(league_names=dict_info["plays_in"])
        dict_info = self.update_historic_name(dict_info)
        return dict_info
