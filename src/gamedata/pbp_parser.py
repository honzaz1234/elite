import re
import scrapy

import common_functions

from logger.logging_config import logger



class PBPParser():


    XPATHS = {
        "attendance": "//td[contains(text(), 'Attendance')]",
        "table": "//div[@class='page']/table",
    }


    def __init__(self, htm, report_id: int):
        self.htm = htm
        self.sel = scrapy.Selector(text=self.htm)
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
            common_functions.log_and_raise(error_message, ValueError)

        logger.info("Scraping of game PBP data from report" 
                    f"{self.report_id} finished")

        return parsed_data
    

    def get_attendance(self) -> str:
        attendance_string = common_functions.get_single_xpath_value(
            sel=self.sel, xpath=self.XPATHS["attendance"], optional=False)
        attendance = re.findall("[0-9,]+", attendance_string)
        attendance = attendance.replace(",", "")

        return attendance
            
            
class PBPTableParser():


    XPATHS = {
        "play_row": "./tr[contains(@id, 'PL')]"
    }


    def __init__(self, table_sel: scrapy.Selector):
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
            self, row_sel: scrapy.Selector, row_idx: int, table_idx: int) -> dict:
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


    def __init__(self, poit_sel: scrapy.Selector):
        self.sel = poit_sel


    def get_team_players_on_ice(self) -> list:
        player_nums = common_functions.get_list_xpath_values(
            sel=self.sel, xpath=self.XPATHS["player_name"], optional=True)
        
        return player_nums


class PBPDescriptionParser():


    PATTERN = None

    PLAYER_PATTERN = rf"[\wÀ-ÖØ-öø-ÿ']+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*"
    ZONE_PATTERN = rf"(?:Off|Def|Neu|Neutral|Offensive|Defensive)\.?"
    TEAM_PATTERN = rf"[A-Z]{{3}}" 
    NUMBER_PATTERN = rf"[0-9]{{1,2}}" 
    PENALTY_PATTERN = rf"[A-Za-z\s/-]+"
    PENALTY_SHOT_PATTERN = "Penalty\sShot"
    PERIOD_STRING = "(Period\s+Start|Period\s+End|Shootout Completed)"
    SHOT_PATTERN = "[A-Za-z\s-]+"
    DEFLECTION = '(Defensive|Offensive)'


    def __init__(self, play_desc: str, play_type: str):
        self.play_desc = play_desc.replace("\xa0", " ")
        self.play_type = play_type


    def parse_play_desc(self) -> dict:
        pattern = re.compile(rf"^\s*{self.PATTERN}\s*$")
        match = pattern.match(self.play_desc)
        try:
            play_dict = match.groupdict()
        except ValueError:
            error_message = (
                f"Extracting data with pattern: {self.PATTERN}"
                f"from string {self.play_desc} ({self.play_type})"
                f" was not succesfull"
                )
            common_functions.log_and_raise(error_message, ValueError)

        return play_dict
    

class PBPDescriptionParserMultipleOptions(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        for pat in self.PATTERN_LIST:
            pattern = re.compile(rf"^\s*{pat}\s*$")
            match = pattern.match(self.play_desc)
            if match:
                break
        try:
            play_dict =  match.groupdict()
        except ValueError:
            error_message = (
                f"Extracting data with pattern: {self.PATTERN}"
                f"from string {self.play_desc} ({self.play_type})"
                f" was not succesfull"
                )
            common_functions.log_and_raise(error_message, ValueError)

        return play_dict


class PBPGoalParser(PBPDescriptionParser):


    PATTERN_GS = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s*#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"(?:\(\d+\))?\s*,\s*"
        rf"(?:(?P<penalty_shot>{PBPDescriptionParser.PENALTY_SHOT_PATTERN})\s*,\s*)?"
        rf"(?P<play_type>{PBPDescriptionParser.SHOT_PATTERN})\s*"
        rf"(?:,\s*(?P<deflection_type>{PBPDescriptionParser.DEFLECTION}\sDeflection))?"
        rf"\s*,?\s*(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*,?\s*"
        rf"(?P<distance>\d+)\s*ft\."
    )

    PATTERN_OG = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"(?:\(\d+\))?\s*,\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
        rf",\s*(?P<own_goal>Own\sGoal)\s*,\s+(?P<distance>\d+)"
        rf"\s*ft\."
    )
    
    PATTERN_A = rf"Assists*?:\s*(?P<assists>(?:#\d+\s+[A-Z]+\(\d+\);?\s*)+)"

    PATTERN_AD = (
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player>{PBPDescriptionParser.PLAYER_PATTERN})\(\d+\)"
    )


    def parse_play_desc(self) -> dict:
        play_dict = {}
        try:
            for pattern in [self.PATTERN_GS, self.PATTERN_OG]:
                goal_pattern = re.compile(pattern)
                goal_match = goal_pattern.match(self.play_desc)
                if goal_match is not None:
                    break
            play_dict["goal"] = goal_match.groupdict()
        except ValueError:
            error_message = (
                f"Extracting data with pattern: {self.PATTERN}"
                f"from string {self.play_desc} ({self.play_type})"
                f" was not succesfull"
                )
            common_functions.log_and_raise(error_message, ValueError)
        assist_pattern = re.compile(self.PATTERN_A)
        assist_details_pattern = re.compile(self.PATTERN_AD)
        assist_match = assist_pattern.search(self.play_desc)
        if assist_match:
            assists_text = assist_match.group('assists')
            assists = [m.groupdict() for m in assist_details_pattern.finditer(assists_text)]
            play_dict['assists'] = assists
        
        return play_dict


class PBPShotParser(PBPDescriptionParser):


    PATTERN = (
    rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+ONGOAL\s*-\s*#"
    rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
    rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,?\s*"
    rf"(?:(?P<penalty_shot>{PBPDescriptionParser.PENALTY_SHOT_PATTERN})\s*,)?"
    rf"(?P<shot_type>{PBPDescriptionParser.SHOT_PATTERN})\s*,?\s*"
    rf"(?:(?P<deflection>{PBPDescriptionParser.DEFLECTION})\s+Deflection"
    rf"\s*,\s*)?"
    rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone,\s*" 
    rf"(?P<distance>\d+)\s*ft\."
    rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?"
    rf"(?:\s*(?P<over_board>Flub)\s*)?" 
    )
    
    
class PBPHitParser(PBPDescriptionParser):


    PATTERN = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+" 
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+" 
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+HIT "
        rf"(?P<opponent_team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<opponent_player_number>{PBPDescriptionParser.NUMBER_PATTERN})"
        rf"\s+(?P<opponent_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"\s*,\s+(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
    )
    

class PBPFaceoffParser(PBPDescriptionParser):


    PATTERN = (
        rf"(?P<winning_team>{PBPDescriptionParser.TEAM_PATTERN})\s+won\s+"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*-\s+"
        rf"(?P<l_team>{PBPDescriptionParser.TEAM_PATTERN})\s+"
        rf"#(?P<l_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<l_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"\s*vs\s*(?P<r_team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<r_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<r_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        )


class PBPGiveAwayParser(PBPDescriptionParser):


    PATTERN = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+GIVEAWAY\s*-\s*"
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})"
        rf"\s+(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN}),\s+"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
    )

    
class PBPTakeawayParser(PBPDescriptionParser):


    PATTERN = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+TAKEAWAY\s+-\s+"
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,\s+"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
    )

    
class PBPMissedShotParser(PBPDescriptionParserMultipleOptions):


    PATTERN_NORMAL = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+" 
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,\s*"
        rf"(?P<shot_type>{PBPDescriptionParser.SHOT_PATTERN})\s*,\s*"
        rf"(?P<shot_result>[A-Za-z\s]+)\s*,\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*,\s*"
        rf"(?P<distance>\d+)\s*ft\.\s*"
        rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?\s*"
        rf"(?:(?P<over_board>Flub))?\s*"
    )

    PATTERN_FAILED = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+" 
        rf"#(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,\s*"
        rf"(?P<shot_type>Failed Attempt)"
        rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?\s*"
        rf"(?:\s*(?P<over_board>Flub)\s*)?"
    )

    PATTERN_LIST = [PATTERN_NORMAL, PATTERN_FAILED]


class PBPBlockedShotParser(PBPDescriptionParserMultipleOptions):


    PATTERN_TEAMATE = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"\s+BLOCKED BY TEAMMATE\s*,\s*"
        rf"(?P<shot_type>{PBPDescriptionParser.SHOT_PATTERN})\s*,\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*"
        rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?"
        rf"(?:\s*(?P<over_board>Flub)\s*)?"    
    )
    
    PATTERN_OPPONENT = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"OPPONENT-BLOCKED BY\s+"
        rf"(?P<blocked_team>{PBPDescriptionParser.TEAM_PATTERN})\s+#(?"
        rf"P<blocked_player_number>{PBPDescriptionParser.NUMBER_PATTERN})"
        rf"\s+(?P<blocked_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        rf"\s*,\s*(?P<shot_type>{PBPDescriptionParser.SHOT_PATTERN})"
        rf"\s*,\s*(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*"
        rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?\s*"
        rf"(?:\s*(?P<over_board>Flub)\s*)?"    
    )

    PATTERN_OTHER = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"BLOCKED BY OTHER"
        rf"\s*,\s*(?P<shot_type>{PBPDescriptionParser.SHOT_PATTERN})"
        rf"\s*,\s*(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*"
        rf"(?:\s*(?P<broken_stick>Broken Stick)\s*)?\s*"
        rf"(?:\s*(?P<over_board>Flub)\s*)?"    
    )


    PATTERN_LIST = [PATTERN_TEAMATE, PATTERN_OPPONENT, PATTERN_OTHER]


class PBPPenaltyParser(PBPDescriptionParserMultipleOptions):


    PATTERN_NDP = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN})\("
        rf"(?P<penalty_minutes>\d+)\s*min\)\s*,\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
        )

    PATTERN_PP = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN})\s*"
        rf"(?:\(\s*(?P<penalty_modifier>maj)\s*\))?\s*"
        rf"\(\s*(?P<penalty_minutes>\d+)\s*min\)\s*,?\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s*,?\s*"
        rf"Drawn By:\s*"
        rf"(?P<drawn_team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<drawn_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<drawn_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        )
    
    PATTERN_TP = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+TEAM\s+"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN})\(\s*"
        rf"(?P<penalty_minutes>\d+)\s*min\)\s+Served By:\s*"
        rf"#(?P<served_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<served_player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,"
        rf"\s*(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
        )
    
    PATTERN_PPDP = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN})\("
        rf"(?P<penalty_minutes>\d+)\s*min\)\s*"
        rf"Served\s+By:\s*#"
        rf"(?P<served_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<served_player_name>{PBPDescriptionParser.PLAYER_PATTERN})\s*,?"
        rf"\s*(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
        )
    
    PATTERN_PPO = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<offender_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<offender_name>{PBPDescriptionParser.PLAYER_PATTERN})\s+"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN})\s*"
        rf"(?:\s*\((?P<penalty_modifier>maj)\))?"
        rf"\s*\((?P<penalty_minutes>\d+)\s+min\)\s+Served\s+By:\s+#"
        rf"(?P<served_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<served_player_name>{PBPDescriptionParser.PLAYER_PATTERN}),\s+"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone\s+"
        rf"Drawn\s+By:\s+"
        rf"(?P<drawn_team>{PBPDescriptionParser.TEAM_PATTERN})\s+#"
        rf"(?P<drawn_player_number>{PBPDescriptionParser.NUMBER_PATTERN})\s+"
        rf"(?P<drawn_player_name>{PBPDescriptionParser.PLAYER_PATTERN})"
        )
    
    PATTERN_C = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s*#\s*"
        rf"(?P<penalty_type>{PBPDescriptionParser.PENALTY_PATTERN}"
        rf"\s*-\s*Head coach)\s*"
        rf"(?:\s*\((?P<penalty_modifier>maj)\)\s*)?"
        rf"\s*\((?P<penalty_minutes>\d+)\s+min\)\s*,\s*"
        rf"(?P<zone>{PBPDescriptionParser.ZONE_PATTERN})\s+Zone"
        )
    
    PATTERN_LIST = [
        PATTERN_NDP, PATTERN_PP, PATTERN_PPO, PATTERN_TP, PATTERN_PPDP,
        PATTERN_C
        ]
    
    
class PBPGameStopageParser(PBPDescriptionParser):


    PATTERN = rf"(?P<game_stopage_type>.+)"


class PBPPeriod(PBPDescriptionParser):


    PATTERN =  (
        rf"{PBPDescriptionParser.PERIOD_STRING}-\s+Local\s+time:\s+"
        rf"(?P<time>\d+\s*:\s*\d+)\s*(?P<timezone>[A-Z]+)"
    )


class PBPDelayedPenalty(PBPDescriptionParser):


    PATTERN = rf"(?P<team>.+)"
    

class PBPChallenge(PBPDescriptionParserMultipleOptions):


    PATTERN = (
        rf"(?P<team>{PBPDescriptionParser.TEAM_PATTERN})\s+Challenge"
        rf"\s*-\s*(?P<reason>[\w\s]+)"
        rf"\s*-\s*Result:\s*(?P<result>.+)"
        )

    PATTERN_LEAGUE = (
        rf"(?P<league_challenge>League)\s+Challenge"
        rf"\s*-\s*(?P<reason>[\w\s]+)"
        rf"\s*-\s*Result:\s*(?P<result>.+)"
        )
    
    PATTERN_LIST = [PATTERN, PATTERN_LEAGUE]


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
        "SOC": PBPPeriod,
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

    SKIP_PLAY = ["PGSTR", "PGEND", "ANTHEM", "GEND", "GOFF"]


    def __init__(self, row_sel: scrapy.Selector):
        self.sel = row_sel


    def parse_row(self) -> dict:
        row_dict = {}
        row_dict['period'] = common_functions.get_single_xpath_value(
            sel=self.sel, xpath=self.XPATHS["period"], optional=False)
        row_dict['play_type'] = common_functions.get_single_xpath_value(
            sel=self.sel, xpath=self.XPATHS["play_type"], optional=False)
        row_dict['time'] = common_functions.get_single_xpath_value(
            sel=self.sel, xpath=self.XPATHS["time"], optional=False)
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
        try:
            play_desc = common_functions.get_single_xpath_value(
            sel=self.sel, xpath=self.XPATHS["play_desc"], optional=False)
            row_desc_parser = self.row_desc_parser_factory(
                play_type=play_type, play_desc=play_desc)
            play_desc_dict = row_desc_parser.parse_play_desc()

            return play_desc_dict
            
        except AttributeError as e:
            error_message = (
                f"AttributeError in parsing play description: "
                f"{e} | Input: {play_desc}"
            )
            common_functions.log_and_raise(error_message, AttributeError)
        except TypeError as e:
            error_message = (
                f"TypeError while processing play description: {e} | "
                f"Input: {play_desc}"
            )
            common_functions.log_and_raise(error_message, TypeError)
        except Exception as e:
            error_message = (
                f"TypeError while processing play description: {e} | "
                f"Input: {play_desc}"
                )
            common_functions.log_and_raise(error_message, Exception)


    def row_desc_parser_factory(
            self, play_type: str, play_desc: str) -> 'PBPDescriptionParser':
        
        return PBPRowParser.PARSER_OBJECTS[play_type](
            play_desc=play_desc, play_type=play_type)







    








