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

    def __init__(self, poit_sel: Selector):
        self.sel = poit_sel

    def get_team_players_on_ice(self):
        pass


class PBPDescriptionParser():


    REGEXES = {
        "number": "#([0-9]+)\s"
    }


    def __init__(self, play_desc: str):
        self.play_desc = play_desc

    @abstractmethod
    def parse_play_desc(self) -> dict:
        pass


class PBPGoalParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_list = self.play_desc.split("\n")
        play_dict = self.parse_goal_scorer_info(play_list[0])
        if len(play_list) > 1:
            assist_dict = self.parse_assist_list(play_list[1])
            play_dict = play_dict | assist_dict
        return play_dict

    def parse_goal_scorer_info(self, line: str) -> dict:
        play_list = line.split(",")
        scorer_dict = {}
        scorer_dict["team"], scorer_dict["number"], scorer_dict["player"] = self.parse_goal_scorer_team(play_list[0])
        scorer_dict["shot_type"] = play_list[1].strip()
        scorer_dict["playing_area"] = play_list[2].strip()
        scorer_dict["shot_distance"] = play_list[3].strip()
        return scorer_dict

    def parse_goal_scorer_team(self, team_player: str) -> dict:
        team = re.findall("^([A-Z]+)\s", team_player)
        number = re.findall("#([0-9]+)\s", team_player)
        player = re.findall("([A-Z]+)(", team_player)
        return team, number, player

    def parse_assist_list(self, line):
        assist_all_dict = {}
        if 'Assists' in line:
            assits_list = line.split(";")
        else:
            assits_list = [line]
        for assist in assits_list:
            assist_dict = self.parse_assist(assist=assist)
            assist_all_dict = assist_all_dict | assist_dict
        return assist_all_dict
    
    def parse_assist(self, assist: str) -> dict:
        assist_dict = {}
        assist_dict['assist_provider'] = re.findall("\s([A-Z]+)\(", assist)
        assist_dict['assist_provider_n'] = re.findall("#([A-Z]+)\s", assist)
        return assist_dict


class PBPShotParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_list = self.play_desc.split(",")
        play_dict["team"], play_dict["number"], play_dict["player"] = self.parse_team_player(play_list[0])
        play_dict["shot_type"] = play_list[1].strip()
        play_dict["playing_area"] = play_list[2].strip()
        play_dict["shot_distance"] = play_list[3].strip()
        return play_dict
        
    def parse_team_player(self, team_player: str) -> tuple:
        team = re.findall("^([A-Z]+)\s", team_player)
        number = re.findall("#([0-9]+)\s", team_player)
        player = re.findall("([A-Z]+)$", team_player)
        return team, number, player
    
    
class PBPHitParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_list = self.play_desc.split(",")
        play_dict = self.get_hit_data(play_list[0])
        play_dict['playing_area'] = play_list[1].strip()
        return play_dict
    
    def get_hit_data(self, hit: str) -> dict:
        hit_dict = {}
        hit_list = hit.split("HIT")
        hit_dict["player_hitter"] = self.get_player_hit_info(hit=hit_list[0])
        hit_dict["player_hitted"] = self.get_player_hit_info(hit=hit_list[1])
        return hit_dict
    
    def get_player_hit_info(self, hit: str) -> dict:
        hit_dict = {}
        hit_dict['team'] = re.findall('^([A-Z+])\s', hit)
        hit_dict['number'] = re.findall('#([0-9]+)\s', hit)
        hit_dict['player'] = re.findall('\s([A-Z]+)\s*$', hit)
        return hit_dict
    

class PBPFaceoffParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_list = self.play_desc.split('-')
        play_dict = self.parse_faceoff_general_info(
            faceoff=play_list[0])
        play_dict["player_info"] = self.parse_faceoff_general_info(
            faceoff=play_list[1])

    def parse_faceoff_general_info(self, faceoff: str) -> dict:
        faceoff_dict = {}
        faceoff_dict['team_winner'] = re.findall("^([A-Z]+)\s", faceoff)
        faceoff_dict['playing_area'] = re.findall(
            "won\s([A-Za-z\.\s]+)$", faceoff)
        return faceoff_dict
    
    def parse_player_faceoff_info(self, faceoff: str) -> dict:
        faceoff_list = faceoff.split('vs')
        faceoff_dict = {}
        faceoff_dict["player_l"] = self.parse_one_player_faceoff_info(
            faceoff_list[0])
        faceoff_dict["player_r"] = self.parse_one_player_faceoff_info(
            faceoff_list[1])
        return faceoff_dict

    def parse_one_player_faceoff_info(self, faceoff: str) -> dict:
        play_dict = {}
        play_dict["team"] = re.findall("^([A-Z]+)\s", faceoff)
        play_dict["number"] = re.findall("#([0-9]+)\s", faceoff)
        play_dict["player"] = re.findall("([A-Z]+)\s*$", faceoff)
        return play_dict
    

class PBPGiveAwayParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_dict["team"] = re.findall("^([A-Z]+)\s", self.play_desc)
        play_dict["number"] = re.findall("#([0-9]+)\s", self.play_desc)
        play_dict["player"] = re.findall("\s([A-Z]+),", self.play_desc)
        play_dict["playing_area"] = re.findall(",\s([A-Za-z\.\s]+)$", self.play_desc)
        return play_dict
    
class PBPTakeawayParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_dict = {}
        play_dict["team"] = re.findall("^([A-Z]+)\s", self.play_desc)
        play_dict["number"] = re.findall("#([0-9]+)\s", self.play_desc)
        play_dict["player"] = re.findall("\s([A-Z]+),", self.play_desc)
        play_dict["playing_area"] = re.findall(
            ",\s([A-Za-z\.\s]+)$", self.play_desc)
        return play_dict
    
class PBPMissedShotParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        play_list = self.play_desc.split(",")
        play_dict = self.get_missed_shot_general_info(info=play_list[0])
        play_dict["shot_type"] = play_list[1].strip()
        play_dict["playing_area"] = play_list[2].strip()
        play_dict["shot_distance"] = play_list[3].strip()
        return play_dict
    
    def get_missed_shot_general_info(self, info: str) -> dict:
        general_info = {}
        general_info["team"] = re.findall("^([A-Z]+)\s", info)
        general_info["number"] = re.findall("#([0-9]+)\s", info)
        general_info["player"] = re.findall("\s([A-Z]+)$", info)
        return general_info
    

class PBPBlockedShotParser(PBPDescriptionParser):

    OPPONENT_BLOCK = "OPPONENT-BLOCKED BY"


    def parse_play_desc(self) -> dict:
        play_list = self.play_desc.split(",")
        play_dict = self.player_info(play_list[0])
        play_dict["shot_type"] = play_list[1].strip()
        play_dict["playing_area"] = play_list[2].strip()
        return play_dict

    def player_info(self, player_block: str) -> dict:
        player_block_info = {}
        if "OPPONENT-BLOCKED BY" in player_block:
            player_list = player_block_info.split("")
            player_block_info["player_blocked"] = self.get_player_info(
                player_list[0])
            player_block_info["player_blocking"] = self.get_player_info(
                player_list[1])
        else:
            player_block_info["player_blocked"] = self.get_player_info(
                player_block)
        return player_block_info

    def get_player_info(self, player_info: str) -> dict:
        player_info = {}
        player_info["team"] = re.findall("^\s*([A-Z]+)\s", player_info)
        player_info["player"] = re.findall("\s([A-Z]+)\s*$", player_info)
        player_info["number"] = re.findall("#([0-9]+)\s", player_info)
        return player_info
    

class PBPPenaltyParser(PBPDescriptionParser):


    def parse_play_desc(self) -> dict:
        pass
    

class PBPRowParser():


    PARSER_OBJECTS = {
        "BLOCK": PBPBlockedShotParser,
        "FAC": PBPFaceoffParser,
        "GIVE": PBPGiveAwayParser,
        "GOAL": PBPGoalParser,
        "HIT": PBPHitParser,
        "MISS": PBPMissedShotParser,
        "SHOT": PBPShotParser,
        "TAKE": PBPTakeawayParser
    }

    XPATHS = {
        "period": "./td[2]/text()",
        "play_desc": "./td[6]/text()",
        "play_type": "./td[5]/text()",
        "time": "./td[3]/text()",
        "team_l": "./td[6]",
        "team_r": "./td[7]"
    }


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
       # row_dict['play_info'] = self.get_play_description(
       #     play_type=row_dict['play_type'])
       # row_dict["poi"] = self.get_players_on_ice()
        return row_dict
    
    def get_players_on_ice(self) -> dict:
        poi_dict = {}
        poi_parser = PlayerOnIceParser(poit_sel=PBPRowParser.XPATHS["team_l"])
        poi_dict["players_l"] = poi_parser.get_team_players_on_ice()
        poi_parser = PlayerOnIceParser(poit_sel=PBPRowParser.XPATHS["team_r"])
        poi_dict["players_r"] = poi_parser.get_team_players_on_ice()
        return poi_dict

    def get_play_description(self, play_type: str) -> dict:
        play_desc = self.sel.xpath(PBPRowParser.XPATHS["play_desc"]).get()
        row_desc_parser = self.row_desc_parser_factory(
            play_type=play_type, play_desc=play_desc)
        play_desc_dict = row_desc_parser.parse_play_desc(play_desc)
        return play_desc_dict

    def row_desc_parser_factory(
            self, play_type: str, play_desc: str) -> 'PBPDescriptionParser':
        return PBPRowParser.PARSER_OBJECTS[play_type](play_desc=play_desc)







    








