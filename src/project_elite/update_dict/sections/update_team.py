import re


class UpdateTeamDict():

    NA_REGION_ABB = {
        "USA": ["NJ", "CA", "AZ", "OH", "MI", 
                "NY", "NE", "WI", "MA", "FL", "CO", "SC", "MO", "MN", "PA", "TX", "CT", "IN", "WA", "IL", "ME", "AL", "OK", "UT", "OR", "NC", "RI", "NH", "VA", "AK", "IA", "MS", "SD", "ND", "MD",	"DE", "NV", "MT", "TN", "VT", "DC", "GA", "ID", "KY", "LA"],
        "CAN": ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "ON", "ONT", 
                "PE", "QC", "SK", "YT", "NU", "WV"]}
    INT_KEYS = ["founded", "construction_year", "capacity"]
    GI_KEYS = ["short_name", "plays_in", "full_name",
               "team_colours", "founded", "active", "u_id", "place"]
    SI_KEYS = ["construction_year", "capacity",
               "construction_year", "arena_name", "place"]

    def __init__(self):
        pass

    def update_place(self, place_name):
        dict_place = {}
        if place_name is None:
            dict_place["country"] = None
            dict_place["region"] = None
            dict_place["place"] = None
            return dict_place
        if "," not in place_name:
            dict_place["country"] = None
            dict_place["region"] = None
            dict_place["place"] = None
            return dict_place
        list_place = place_name.split(",")
        dict_place["place"] = list_place[0]
        if len(list_place) == 2 and len(list_place[1]) == 2:
            if list_place[1] in UpdateTeamDict.NA_REGION_ABB["USA"]:
                dict_place["region"] = list_place[1].strip()
                dict_place["country"] = "USA"
            elif list_place[1] in UpdateTeamDict.NA_REGION_ABB["CAN"]:
                dict_place["region"] = list_place[1].strip()
                dict_place["country"] = "CAN"
            else:
                dict_place["country"] = list_place[1].strip()
                dict_place["region"] = None

        elif len(list_place) == 2:
            dict_place["country"] = list_place[1].strip()
            dict_place["region"] = None
        elif len(list_place) == 3:
            dict_place["country"] = list_place[2].strip()
            dict_place["region"] = list_place[1].strip()
        return dict_place

    def update_key_names(self, dict_info):
        for key in ["general_info", "stadium_info"]:
            for subkey in list(dict_info[key].keys()):
                new_key = subkey.strip()
                new_key = new_key.lower()
                new_key = re.sub(" ", "_", new_key)
                if new_key != subkey:
                    dict_info[key][new_key] = dict_info[key][subkey]
                    del dict_info[key][subkey]
        return dict_info

    def update_urls(self, list_url, regex):
        dict_url = {}
        for url in list_url:
            u_id = re.findall(regex, url)[0]
            dict_url[u_id] = url
        return dict_url

    def update_numbers(self, dict_info):
        for key in dict_info:
            if key == "u_id":
                continue
            for subkey in dict_info[key]:
                if subkey in UpdateTeamDict.INT_KEYS:
                    if dict_info[key][subkey] is None:
                        continue
                    if dict_info[key][subkey] == "-":
                        dict_info[key][subkey] = None
                    else:
                        new_int = (re.sub("\s", "", dict_info[key][subkey]))
                        new_int = re.findall("[0-9]+", new_int)
                        if new_int != []:
                            new_int = int(new_int[0])
                        else:
                            new_int = None
                        dict_info[key][subkey] = new_int
        return dict_info

    def update_colours(self, colour_string):
        if colour_string == None:
            return []
        colour_list = colour_string.split(" + ")
        return colour_list

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
                    hist_names_dict[dict_info["general_info"]
                                    ["short_name"]] = hist_names_dict[key]
                    del hist_names_dict[key]
        dict_info["titles"] = hist_names_dict
        return dict_info

    def update_team_url(self, list_url):
        new_list = []
        for url in list_url:
            u_id = re.findall("team\/([0-9]+)\/", url)[0]
            new_list.append(u_id)
        return new_list

    def update_retired_numbers(self, player_dict):
        for url_key in list(player_dict.keys()):
            u_id = int(re.findall("player\/([0-9]+)\/", url_key)[0])
            new_number = int(re.findall("#([0-9]+)", player_dict[url_key])[0])
            new_dict = [new_number, url_key]
            player_dict[u_id] = new_dict
            del player_dict[url_key]
        return player_dict

    def update_info(self, info_dict, list_keys):
        for key in list(info_dict.keys()):
            if key not in list_keys:
                del info_dict[key]
        for key in list_keys:
            if key not in info_dict:
                info_dict[key] = None
            elif type(info_dict[key]) == str:
                info_dict[key] = info_dict[key].strip()
        return info_dict

    def update_team_dict_wrap(self, dict_info):
        dict_info = self.update_key_names(dict_info)
        for key in ["stadium_info", "general_info"]:
            if "town" in dict_info[key]:
                subkey = "town"
            elif "place" in dict_info[key]:
                subkey = "place"
            else:
                continue
            place_dict = self.update_place(place_name=dict_info[key][subkey])
            dict_info[key]["place"] = place_dict
        dict_info["affiliated_teams"] = self.update_urls(
            list_url=dict_info["affiliated_teams"], regex="team\/([0-9]+)")
        dict_info = self.update_NA(dict_info)
        dict_info = self.update_numbers(dict_info=dict_info)
        dict_info["general_info"]["active"] = self.update_status(
            league_names=dict_info["general_info"]["plays_in"])
        dict_info = self.update_historic_name(dict_info)
        dict_info["retired_numbers"] = self.update_retired_numbers(
            player_dict=dict_info["retired_numbers"])
        dict_info["general_info"] = self.update_info(
            info_dict=dict_info["general_info"], 
            list_keys=UpdateTeamDict.GI_KEYS)
        dict_info["stadium_info"] = self.update_info(
            info_dict=dict_info["stadium_info"], 
            list_keys=UpdateTeamDict.SI_KEYS)
        dict_info["colour_list"] = self.update_colours(
            colour_string=dict_info["general_info"]["team_colours"])
        return dict_info
