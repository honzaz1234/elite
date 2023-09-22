import re
from hockeydata.constants import *


class UpdateLeagueDict():

    NOT_INT = [POSTSEASON, TEAM, TEAM_URL, POSITION]

    def __init__(self):
        pass
    
    def update_league_dict(self, league_dict: dict) -> dict:
        new_league_dict = league_dict.copy()
        new_league_dict[SEASON_STANDINGS] = self._update_standing_dict(
            standing_dict=new_league_dict[SEASON_STANDINGS])
        return new_league_dict

    def _update_standing_dict(self, standing_dict: dict) -> dict:
        """wraper function for updating dict with team standings for individual seasons
        """

        new_dict = {}
        for section in standing_dict:
            new_dict[section] = {}
            for season in standing_dict[section]:
                new_dict[section][season] = {}
                for position in standing_dict[section][season]:
                    new_key = int(re.findall("([0-9]+).", position)[0])
                    row_dict = standing_dict[section][season][position]
                    new_row_dict = self._update_row(row_dict)
                    new_dict[section][season][new_key] = new_row_dict
        return new_dict

    def _update_row(self, row_dict: dict) -> dict:
        """function for updating one team entry in season data dict"""
        
        for stat in list(row_dict.keys()):
            if row_dict[stat] == NA:
                row_dict[stat] = None
            elif stat not in UpdateLeagueDict.NOT_INT:
                row_dict[stat] = int(row_dict[stat])
            elif stat == TEAM_URL:
                u_id = re.findall(
                    TEAM_UID_REGEX, row_dict[stat])[0]
                print(u_id)
                row_dict[TEAM_UID] = u_id
        return row_dict
