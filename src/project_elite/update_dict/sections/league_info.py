import re
from constants import *


class UpdateLeagueDict():

    NOT_INT = ["postseason", "team", "url"]
    NA = "-"

    def __init__(self):
        pass

    def _update_standing_dict(self, league_dict):
        """wraper function for updating dict with team standings for individual seasons
        """

        new_dict = {}
        for section in league_dict:
            new_dict[section] = {}
            for season in league_dict[section]:
                new_dict[section][season] = {}
                for position in league_dict[section][season]:
                    new_key = int(re.findall("([0-9]+).", position)[0])
                    row_dict = league_dict[section][season][position]
                    new_row_dict = self._update_row(row_dict)
                    new_dict[section][season][new_key] = new_row_dict
        return new_dict

    def _update_row(self, row_dict):
        """function for updating one team entry in season data dict"""
        
        for stat in list(row_dict.keys()):
            if row_dict[stat] == UpdateLeagueDict.NA:
                row_dict[stat] = None
            elif stat not in UpdateLeagueDict.NOT_INT:
                row_dict[stat] = int(row_dict[stat])
            elif stat == "url":
                u_id = re.findall(
                    TEAM_UID_REGEX, row_dict[stat])[0]
                row_dict["u_id"] = u_id
        return row_dict
