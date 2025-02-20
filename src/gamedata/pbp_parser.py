import re

from scrapy import Selector

from logger.logger import logger

PLAYER_PATTERN = "[\wÀ-ÖØ-öø-ÿ]+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*"
ZONE_PATTERN = "(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?"

class PBPParser():


    XPATHS = {
        "attendance": "//td[contains(text(), 'Attendance')]",
        "table": "//div[@class='page']/table",
    }


    def __init__(self, htm, report_id: int):
        self.htm = htm
        self.sel = Selector(text=self.htm)
        self.report_id = report_id


    def parse_htm_file(self) -> list:
        logger.info("Scraping of game PBP data from report" 
                    f"{self.report_id} started")
        parsed_data = []
        sel_tables = self.sel.xpath(PBPParser.XPATHS["table"])
        table_idx = 0
        for sel in sel_tables:
            table_idx += 1
            table_parser = PBPTableParser(table_sel=sel)
            parsed_data_table = table_parser.parse_table(table_idx=table_idx)
            parsed_data.extend(parsed_data_table)
        if not parsed_data:
            error_message = (
                f"No PBP data was scraped for match: " 
                f"{self.report_id}"
            )
            logger.error(error_message)
            raise ValueError(error_message)
        logger.info("Scraping of game PBP data from report" 
                    f"{self.report_id} finished")

        return parsed_data
    

    def get_attendance(self) -> str:
        attendance_string = self.sel.xpath(self.XPATHS["attendance"]).get()
        attendance = re.findall("[0-9,]+", attendance_string)
        attendance = attendance.replace(",", "")

        return attendance
            
            
class PBPTableParser():


    XPATHS = {
        "play_row": "./tr[contains(@id, 'PL')]"
    }


    def __init__(self, table_sel: Selector):
        self.sel = table_sel


    def parse_table(self, table_idx: int) -> list:
        parsed_data = []
        row_sel = self.sel.xpath(PBPTableParser.XPATHS["play_row"])
        logger.debug("Scraping of game PBP data from table: " 
                    f"{table_idx} started")
        row_idx = 0
        for play_row_sel in row_sel:
            row_idx += 1
            row_dict = self.parse_row(row_sel=play_row_sel,
                                      row_idx=row_idx,
                                      table_idx=table_idx)
            parsed_data.append(row_dict)
        logger.debug("Scraping of game PBP data from table: " 
                    f"{table_idx} finished")
        return parsed_data

    def parse_row(
            self, row_sel: Selector, row_idx: int, table_idx: int) -> dict:
        logger.debug(f"Scraping of game PBP data from row: {row_idx} table: " 
                    f"{table_idx} started")
        row_parser = PBPRowParser(row_sel=row_sel)
        row_dict = row_parser.parse_row()
        logger.debug(f"Scraping of game PBP data from row: {row_idx} table: " 
                    f"{table_idx} finished")

        return row_dict

    
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
        r"(?P<team>\w+)\s+#(?P<number>\d+)\s+(?P<player>[A-Z]+)\(\d+\),\s+"
        r"(?P<play_type>[\w\s]+),\s+(?P<zone>[\w.\s]+),\s+(?P<distance>\d+)"
        "\s*ft\."
    )
    
    PATTERN_A = r"Assists*?:\s*(?P<assists>(?:#\d+\s+[A-Z]+\(\d+\);?\s*)+)"

    PATTERN_AD = r"#(?P<number>\d+)\s+(?P<player>[A-Z]+)\(\d+\)"


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
        rf"(?P<player_name>{PLAYER_PATTERN}), "
        r"(?P<shot_type>[A-Za-z-]+) ,"
        rf"(?P<zone>{ZONE_PATTERN}) Zone, (?P<distance>\d+) ft\."
    )
    
    
class PBPHitParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) #(?P<player_number>\d+)" 
        rf"(?P<player_name>{PLAYER_PATTERN}) HIT "
        r"(?P<opponent_team>[A-Z]+) #(?P<opponent_player_number>\d+) "
        rf"(?P<opponent_player_name>{PLAYER_PATTERN}), "
        rf"(?P<zone>{ZONE_PATTERN}) Zone"
    )
    

class PBPFaceoffParser(PBPDescriptionParser):


    PATTERN = (
        rf"(?P<winning_team>[A-Z]+) won (?P<zone>({ZONE_PATTERN}) Zone - "
        r"(?P<losing_team>[A-Z]+) #(?P<losing_player_number>\d+) "
        rf"(?P<losing_player_name>{PLAYER_PATTERN}) vs "
        r"(?P<winning_team_again>[A-Z]+) #(?P<winning_player_number>\d+) "
        rf"(?P<winning_player_name>{PLAYER_PATTERN})"
        )


class PBPGiveAwayParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) GIVEAWAY\s*-\s*#(?P<player_number>\d+)"
        rf" (?P<player_name>{PLAYER_PATTERN}), "
        rf"(?P<zone>{ZONE_PATTERN}) Zone"
    )

    
class PBPTakeawayParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) TAKEAWAY - #(?P<player_number>\d+) "
        rf"(?P<player_name>{PLAYER_PATTERN}), "
        rf"(?P<zone>{ZONE_PATTERN}) Zone"
    )

    
class PBPMissedShotParser(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>[A-Z]+) #(?P<player_number>\d+) "
        rf"(?P<player_name>{PLAYER_PATTERN}), "
        r"(?P<shot_type>[A-Za-z-]+), (?P<shot_result>[A-Za-z\s]+), "
        rf"(?P<zone>{ZONE_PATTERN}) Zone, "
        r"(?P<distance>\d+) ft\."""
    )


class PBPBlockedShotParser(PBPDescriptionParser):


    PATTERN_TEAMATE = (
        r"(?P<team>\w+)\s+#(?P<player_number>\d+)\s+"
        rf"(?P<player_name>{PLAYER_PATTERN})\s+BLOCKED BY TEAMMATE,\s*"
        rf"(?P<shot_type>[\w\s]+),\s*(?P<zone>({ZONE_PATTERN})\s*Zone"
    )
    
    PATTERN_OPPONENT = (
        r"(?P<team>\w+)\s+#(?P<player_number>\d+)\s+"
        rf"(?P<player_name>{PLAYER_PATTERN})\s+"
        r"OPPONENT-BLOCKED BY\s+(?P<blocked_team>\w+)\s+#(?"
        r"P<blocked_player_number>\d+)\s+(?P<blocked_player_name>"
        rf"{PLAYER_PATTERN}),\s*(?P<shot_type>[\w\s]+),\s*(?P<zone>"
        rf"{ZONE_PATTERN}\s*Zone)"
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

    PATTERN_NDP = (
        r"(?P<team>[A-Z]+)\s+#(?P<player_number>\d+)\s+"
        rf"(?P<player_name>{PLAYER_PATTERN})\s+"
        r"(?P<penalty_type>[A-Za-z-\s/]+)\((?P<penalty_minutes>\d+)\s*min\),\s*"
        r"(?P<zone>[A-Za-z.]+)\s*Zone"
        )

    PATTERN_PP = (
        r"(?P<team>[A-Z]+)\s+#(?P<player_number>\d+)\s+"
        rf"(?P<player_name>{PLAYER_PATTERN})\s+"
        r"(?P<penalty_type>[A-Za-z-\s/]+)\((?P<penalty_minutes>\d+)\s*min\),\s*"
        r"(?P<zone>[A-Za-z.]+)\s*Zone,*\s*Drawn By:\s*"
        r"(?P<drawn_team>[A-Z]+)\s+#(?P<drawn_player_number>\d+)\s+"
        rf"(?P<drawn_player_name>{PLAYER_PATTERN})"
        )
    
    PATTERN_TP = (
        r"(?P<team>[A-Z]+) TEAM (?P<penalty_type>[A-Za-z-\s/]+)\("
        r"(?P<penalty_minutes>\d+) min\) "
        r"Served By: #(?P<served_player_number>\d+) "
        rf"(?P<served_player_name>{PLAYER_PATTERN}), "
        rf"(?P<zone>{ZONE_PATTERN})"
        " Zone"
        )
    
    PATTERN_PPO = (
        r"(?P<team>[A-Z]{2,3})\s+#(?P<offender_number>\d+)\s+"
        r"(?P<offender_name>[A-Z]+)\s+(?P<penalty_type>[A-Za-z-\s/]+)"
        r"\((?P<penalty_minutes>\d+)\s+min\)\s+"
        r"Served\s+By:\s+#(?P<served_player_number>\d+)\s+"
        rf"(?P<served_player_name>{PLAYER_PATTERN}),\s+"
        r"(?P<Zone>[\w\s.]+)\s+"
        r"Drawn\s+By:\s+(?P<drawn_team>[A-Z]{2,3})\s+#"
        r"(?P<drawn_player_number>\d+)\s+"
        rf"(?P<drawn_player_name>{PLAYER_PATTERN})"
        )
    

    def parse_play_desc(self) -> dict:

        for pat in [self.PATTERN_NDP, self.PATTERN_PP, self.PATTERN_PPO, self.PATTERN_TP]:
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
    

class PBPDelayedPenalty(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_dict["team"] = self.play_desc.strip()

        return play_dict
    
class PBPChallenge(PBPDescriptionParser):


    PATTERN = (
        r"(?P<team>\w{3}) Challenge\s*-\s*(?P<reason>[\w\s]+)"
        r"\s*-\s*Result:\s*(?P<result>.+)"
        )


class PBPRowParser():


    PARSER_OBJECTS = {
        "BLOCK": PBPBlockedShotParser,
        "CHL": PBPChallenge,
        "DELPEN": PBPDelayedPenalty,
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
        "time": "./td[4]/text()",
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
    
    
    def get_time(self) -> str:

        return self.sel.xpath(PBPRowParser.XPATHS['time']).get()
    
    
    def parse_row(self) -> dict:
        row_dict = {}
        row_dict['period'] = self.get_period()
        row_dict['play_type'] = self.get_play_type()
        row_dict['time'] = self.get_time()
        if row_dict['play_type'] not in self.SKIP_PLAY:
            row_dict['play_info'] = self.get_play_description(
                play_type=row_dict['play_type'])
        row_dict["poi"] = self.get_players_on_ice()
        logger.debug(f"Parsed row: {row_dict}")

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
        play_desc = self.sel.xpath(PBPRowParser.XPATHS["play_desc"]).getall()
        play_desc = " ".join(play_desc)
        row_desc_parser = self.row_desc_parser_factory(
            play_type=play_type, play_desc=play_desc)
        try:
            play_desc_dict = row_desc_parser.parse_play_desc()
        except:
            logger.info(f"Error in parsing table with string {play_desc}")
            raise

        return play_desc_dict


    def row_desc_parser_factory(
            self, play_type: str, play_desc: str) -> 'PBPDescriptionParser':
        
        return PBPRowParser.PARSER_OBJECTS[play_type](play_desc=play_desc)







    








