import re

class UpdateLeagueDict():

    def __init__(self):
        pass

    def _update_standing_dict(self, league_dict):
        new_dict={}
        for league_section in league_dict:
            new_dict[league_section] = {}
            for season in league_dict[league_section]:
                new_dict[league_section][season] = {}
                for position in league_dict[league_section][season]:
                    new_key_name = re.findall("([0-9]+).", position)[0]
                    row_dict = league_dict[league_section][season][position]
                    new_row_dict = self._update_row(row_dict)
                    new_dict[league_section][season][new_key_name] = new_row_dict
        return new_dict

    def _update_row(self, row_dict):
        for stat in row_dict:
            if row_dict[stat] == "-":
                row_dict[stat] = None
            elif stat not in ["postseason", "team"]:
                row_dict[stat] = int(row_dict[stat])
        return row_dict


