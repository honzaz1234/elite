import re

from hockeydata.constants import *
from hockeydata.logger.logger import logger


class UpdateLeagueDict():

    """class used for updating values in dictionary with data on league in order to prepare it for inserting into DB
    """

    NOT_INT = [POSTSEASON, TEAM, TEAM_URL, POSITION]

    def __init__(self):
        pass
    
    def update_league_dict(self, league_dict: dict) -> dict:
        """wrapper method for updating all info in league dict"""

        new_league_dict = league_dict.copy()
        new_league_dict[SEASON_STANDINGS] = self._update_standing_dict(
            standing_dict=new_league_dict[SEASON_STANDINGS])
        logger.debug(f"League dict updated: {new_league_dict}")
        logger.info(f"League dict ({new_league_dict[LEAGUE_UID]})"
                     " succesfully updated")
        return new_league_dict

    def _update_standing_dict(self, standing_dict: dict) -> dict:
        """wrapper method for updating dict with team standings for individual seasons
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
        """method for updating one team entry in season data dict"""
        
        for stat in list(row_dict.keys()):
            if row_dict[stat] == NA:
                row_dict[stat] = None
            elif stat not in UpdateLeagueDict.NOT_INT:
                row_dict[stat] = int(row_dict[stat])
            elif stat == TEAM_URL:
                u_id = re.findall(TEAM_UID_REGEX, 
                                  row_dict[stat])[0]
                row_dict[TEAM_UID] = u_id
        return row_dict
