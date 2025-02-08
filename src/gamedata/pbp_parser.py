import re

from abc import ABC, abstractmethod
from scrapy import Selector

class PBPParser():


    XPATHS = {
        "table": "//div[@class='page']/table",
    }


    def __init__(self, htm):
        self.htm = htm
        self.sel = Selector(text=self.htm)

    def parse_htm_file(self):
        parsed_data = []
        sel_tables = self.sel.xpath(PBPParser.XPATHS["table"])
        for sel in sel_tables:
            table_parser = PBPTableParser(table_sel=sel)
            parsed_data_table = table_parser.parse_table()
            parsed_data.extend(parsed_data_table)
        return parsed_data
            
            
class PBPTableParser():


    XPATHS = {
        "play_row": "./tr[contains(@id, 'PL')]"
    }

    def __init__(self, table_sel: Selector):
        self.sel = table_sel

    def parse_table(self) -> list:
        parsed_data = []
        row_sel = self.sel.xpath(PBPTableParser.XPATHS["play_row"])
        for play_row_sel in row_sel:
            row_parser = PBPRowParser(row_sel=play_row_sel)
            row_dict = row_parser.parse_row()
            parsed_data.append(row_dict)
        return parsed_data

    
class PlayerOnIceParser():


    XPATHS = {
        "player_name": ".//font//@title"
    }

    def __init__(self, poit_sel: Selector):
        self.sel = poit_sel

    def get_team_players_on_ice(self):
        player_nums = self.sel.xpath(self.XPATHS["player_name"]).getall()
        
        return player_nums


class PBPDescriptionParser():


    PATTERN = None


    def __init__(self, play_desc: str):
        self.play_desc = play_desc.replace("\xa0", " ")

    def parse_play_desc(self) -> dict:
        pattern = re.compile(self.PATTERN)
        match = pattern.match(self.play_desc)
        play_dict =  match.groupdict()

        return play_dict


class PBPGoalParser(PBPDescriptionParser):


    PATTERN_GS = (
        r"(?P<team>\w+)\s+#(?P<number>\d+)\s+(?P<player>[A-Z]+\(\d+\)),\s+"
        r"(?P<play_type>[\w\s]+),\s+(?P<zone>[\w.\s]+),\s+(?P<distance>\d+)"
        "\s*ft\."
    )
    
    PATTERN_A = r"Assists?:\s+(?P<assists>(?:#\d+\s+[A-Z]+\(\d+\);?\s*)+)"

    PATTERN_AD = r"#(?P<number>\d+)\s+(?P<player>[A-Z]+)\((?P<points>\d+)\)"


    def parse_play_desc(self) -> dict:
        pattern = re.compile(self.PATTERN_GS)
        assist_pattern = re.compile(self.PATTERN_A)
        assist_details_pattern = re.compile(self.PATTERN_AD)
        main_match = pattern.search(self.play_desc)
        assist_match = assist_pattern.search(self.play_desc)
        
        if not main_match:
            return None
        
        play_dict = {
            'team': main_match.group('team'),
            'player_number': main_match.group('number'),
            'player': main_match.group('player'),
            'play_type': main_match.group('play_type').strip(),
            'zone': main_match.group('zone').strip(),
            'distance_ft': int(main_match.group('distance')),
            'assists': []
        }
        
        if assist_match:
            assists_text = assist_match.group('assists')
            assists = [m.groupdict() for m in assist_details_pattern.finditer(assists_text)]
            play_dict['assists'] = assists
        
        return play_dict


class PBPShotParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) ONGOAL\s*-\s*#(?P<player_number>\d+) "
        r"(?P<player_name>[A-Z]+(?: [A-Z]+)*), "
        r"(?P<shot_type>[A-Za-z-]+) , (?P<zone>"
        "(?:Off|Def|Neu|Neutral|Offensive"
        r"|Defensive)\.?) Zone, (?P<distance>\d+) ft\."
    )
    
    
class PBPHitParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) #(?P<player_number>\d+) (?P<player_name>"
        "[A-Z]+(?: [A-Z]+)*) HIT "
        r"(?P<opponent_team>[A-Z]+) #(?P<opponent_player_number>\d+) "
        r"(?P<opponent_player_name>[A-Z]+(?: [A-Z]+)*), "
        r"(?P<zone>(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?) Zone"
    )
    

class PBPFaceoffParser(PBPDescriptionParser):


    PATTERN = (r"(?P<winning_team>[A-Z]+) won (?P<zone>(?:Off|Def|Neu|Neutral|"
            r"Offensive|Defensive)\.?) Zone - "
            r"(?P<losing_team>[A-Z]+) #(?P<losing_player_number>\d+) "
            r"(?P<losing_player_name>[A-Z]+(?: [A-Z]+)*) vs "
            r"(?P<winning_team_again>[A-Z]+) #(?P<winning_player_number>\d+) "
            r"(?P<winning_player_name>[A-Z]+(?: [A-Z]+)*)")


class PBPGiveAwayParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) GIVEAWAY\s*-\s*#(?P<player_number>\d+) (?P<player_name>"
        r"[A-Z]+(?: [A-Z]+)*), "
        r"(?P<zone>(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?) Zone"
    )

    
class PBPTakeawayParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) TAKEAWAY - #(?P<player_number>\d+) "
        r"(?P<player_name>[A-Z]+(?: [A-Z]+)*), "
        r"(?P<zone>(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?) Zone"
    )

    
class PBPMissedShotParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) #(?P<player_number>\d+) (?P<player_name>"
        "[A-Z]+(?: [A-Z]+)*), "
        r"(?P<shot_type>[A-Za-z-]+), (?P<shot_result>[A-Za-z\s]+), "
        r"(?P<zone>(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?) Zone, "
        r"(?P<distance>\d+) ft\."""
    )


class PBPBlockedShotParser(PBPDescriptionParser):


    PATTERN_TEAMATE = (
        r"(?P<team>\w+)\s+#(?P<player_number>\d+)\s+(?P<player_name>"
        "[A-Z]+(?: [A-Z]+)*)\s+BLOCKED BY TEAMMATE,\s*"
        r"(?P<shot_type>[\w\s]+),\s*(?P<zone>(?:Off|Def|Neu|Neutral|Offensive"
        "|Defensive)\.?\s*Zone)"
    )
    
    PATTERN_OPPONENT = (
        r"(?P<team>\w+)\s+#(?P<player_number>\d+)\s+"
        r"(?P<player_name>[A-Z]+(?: [A-Z]+)*)\s+"
        r"OPPONENT-BLOCKED BY\s+(?P<blocked_team>\w+)\s+#(?"
        r"P<blocked_player_number>\d+)\s+(?P<blocked_player_name>"
        r"[A-Z]+(?: [A-Z]+)*),\s*(?P<shot_type>[\w\s]+),\s*(?P<zone>"
        "(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?\s*Zone)"
    )

    def parse_play_desc(self) -> dict:
        if "TEAMMATE" in self.play_desc:
            pattern = re.compile(self.PATTERN_TEAMATE)
        else:
            pattern = re.compile(self.PATTERN_OPPONENT)
        match = pattern.match(self.play_desc)
        play_dict =  match.groupdict()

        return play_dict


class PBPPenaltyParser(PBPDescriptionParser):


    PATTERN_PP = (
        r"(?P<team>[A-Z]+)\s+#(?P<player_number>\d+)\s+(?"
        r"P<player_name>[A-Z]+(?: [A-Z]+)*)\s+"
        r"(?P<penalty_type>[\w\s]+)\((?P<penalty_minutes>\d+)\s*min\),\s*"
        r"(?P<zone>[A-Za-z.]+) Zone\s*Drawn By:\s*"
        r"(?P<drawn_team>[A-Z]+)\s+#(?P<drawn_player_number>\d+)\s+"
        r"(?P<drawn_player_name>[A-Z]+(?: [A-Z]+)*)"
        )
    
    PATTERN_TP = (
        r"(?P<team>[A-Z]+) TEAM (?P<penalty_type>[A-Za-z\s/-]+)\("
        r"(?P<penalty_minutes>\d+) min\) "
        r"Served By: #(?P<served_player_number>\d+) "
        r"(?P<served_player_name>[A-Z]+(?: [A-Z]+)*), "
        r"(?P<zone>(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?)"
        " Zone"
        )
    
    PATTERN_PPO = (
        r"(?P<team>[A-Z]{2,3})\s+#(?P<offender_number>\d+)\s+"
        r"(?P<offender_name>[A-Z]+)"
        r"\s+(?P<penalty_type>[\w-]+)\((?P<penalty_minutes>\d+)"
        "\s+min\)\s+Served\s"
        r"+By:\s+#(?P<served_player_number>\d+)\s+"
        r"(?P<served_player_name>[A-Z]+),\s+(?"
        r"P<Zone>[\w\s.]+)\s+Drawn\s+By:\s+(?P<drawn_team>[A-Z]{2,3})\s+#"
        r"(?P<drawn_player_number>\d+)\s+(?P<drawn_player_name>[A-Z]+)"
        )
    

    def parse_play_desc(self) -> dict:

        for pat in [self.PATTERN_PP, self.PATTERN_PPO, self.PATTERN_TP]:
            pattern = re.compile(pat)
            match = pattern.match(self.play_desc)
            if match:
                break
        play_dict =  match.groupdict()
        
        return play_dict
    
    
class PBPGameStopageParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_dict["game_stopage_type"] = self.play_desc

        return play_dict
    

class PBPPeriod(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_dict["time"] = re.findall(
            "Local time:\s([0-9]+:[0-9]+)", self.play_desc)[0]
        play_dict["time_zone"] = re.findall("([A-Z]+)$", self.play_desc)[0]

        return play_dict


class PBPRowParser():


    PARSER_OBJECTS = {
        "BLOCK": PBPBlockedShotParser,
        "FAC": PBPFaceoffParser,
        "GIVE": PBPGiveAwayParser,
        "GOAL": PBPGoalParser,
        "HIT": PBPHitParser,
        "MISS": PBPMissedShotParser,
        "PEND": PBPPeriod,
        "PENL": PBPPenaltyParser,
        "PSTR": PBPPeriod,
        "SHOT": PBPShotParser,
        "STOP": PBPGameStopageParser,
        "TAKE": PBPTakeawayParser
    }

    XPATHS = {
        "period": "./td[2]/text()",
        "play_desc": "./td[6]/text()",
        "play_type": "./td[5]/text()",
        "time": "./td[3]/text()",
        "team_l": "./td[7]",
        "team_r": "./td[8]"
    }

    SKIP_PLAY = ["PGSTR", "PGEND", "ANTHEM", "GEND"]


    def __init__(self, row_sel: Selector):
        self.sel = row_sel

    def get_play_type(self) -> str: 
        return self.sel.xpath(PBPRowParser.XPATHS['play_type']).get()
    
    def get_period(self) -> str:
        return self.sel.xpath(PBPRowParser.XPATHS['period']).get()
    
    def parse_row(self) -> dict:
        row_dict = {}
        row_dict['period'] = self.get_period()
        row_dict['play_type'] = self.get_play_type()
        if row_dict['play_type'] not in self.SKIP_PLAY:
            row_dict['play_info'] = self.get_play_description(
                play_type=row_dict['play_type'])
        row_dict["poi"] = self.get_players_on_ice()
        return row_dict
    
    def get_players_on_ice(self) -> dict:
        poi_dict = {}
        poi_parser = PlayerOnIceParser(poit_sel=self.sel.xpath(
            PBPRowParser.XPATHS["team_l"]))
        poi_dict["players_l"] = poi_parser.get_team_players_on_ice()
        poi_parser = PlayerOnIceParser(poit_sel=self.sel.xpath(
            PBPRowParser.XPATHS["team_r"]))
        poi_dict["players_r"] = poi_parser.get_team_players_on_ice()
        return poi_dict

    def get_play_description(self, play_type: str) -> dict:
        play_desc = self.sel.xpath(PBPRowParser.XPATHS["play_desc"]).get()
        row_desc_parser = self.row_desc_parser_factory(
            play_type=play_type, play_desc=play_desc)
        play_desc_dict = row_desc_parser.parse_play_desc()
        return play_desc_dict

    def row_desc_parser_factory(
            self, play_type: str, play_desc: str) -> 'PBPDescriptionParser':
        return PBPRowParser.PARSER_OBJECTS[play_type](play_desc=play_desc)







    








