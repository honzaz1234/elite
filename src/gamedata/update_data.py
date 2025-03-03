import re

import common_functions
import  mappers.team_mappers as team_map

from logger.logging_config import logger


def get_updated_period(period: str) -> int:

    try:
        result = int(period)

        return result
    
    except ValueError:
        error_message = f"Invalid integer value: {period}"
        common_functions.log_and_raise(error_message, ValueError)
    except TypeError:
        error_message = (
            f"TypeError: Expected str, int, or float, but got"
            f" {type(period).__name__}"
        )
        common_functions.log_and_raise(error_message, TypeError)


class UpdateGameDate():



    UPDATE_CLASSES = {

    }


    def __init__(self, game_data: dict, player_db_data: list):
        self.game_data = game_data
        self.player_db_data = player_db_data
        self.player_mapper = {}
        self.HT_uid = None
        self.VT_uid = None


    def update_game_data(self, game_data: dict) -> dict:
        updated_data = {}
        updated_data = self.get_general_info(updated_data)
        updated_data["shifts"] = self.update_shifts()
        self.match_players_to_uid()
        updated_data["PBP"] = self.update_PBP(game_data)

        return updated_data
    

    def get_general_info(self, updated_data: dict) -> dict:
        updated_data["HT"] = self.get_set_team_uid(self.game_data["HT"], "HT")
        updated_data["VT"] = self.get_set_team_uid(self.game_data["VT"], "VT")
        updated_data["date"] = self.game_data["date"]
        updated_data["stadium"] = self.game_data["stadium"]
        updated_data["start_time_UTC"] = self.game_data["start_time_UTC"]

        return updated_data
    
    
    def get_set_team_uid(self, team_abb: str, HV_type: str) -> int:
        team_uid = team_map.get_team_uid_from_abbrevation(team_abb)
        self.set_team_uid(team_uid, HV_type)

        return team_uid

    
    def set_team_uid(self, team_uid: int,  HV_type: str) -> None:
        if HV_type == "HT":
            self.set_home_team_uid(team_uid)
        elif HV_type == "VT":
            self.set_visitor_team_uid(team_uid)


    def set_home_team_uid(self, team_uid: int) -> None:
        self.HT_uid = team_uid


    def set_visitor_team_uid(self, team_uid: int) -> None:
        self.VT_uid = team_uid


    def update_shifts(self) -> dict:
        shift_dict = {}
        us_o = UpdateShifts()
        shift_dict["TH"] = us_o.update_players_shifts(self.game_data["TH"])
        shift_dict["TV"] = us_o.update_players_shifts(self.game_data["TV"])

        return shift_dict
    

    def match_players_to_uid(
            self, scraped_data: dict, team: str) -> dict:
        for player_info in scraped_data.keys():
            team_uid = team_map.get_team_uid_from_abbrevation()
            self.match_player_to_uid(player_info, team_uid, team)


    def match_player_to_uid(
            self, player_info: tuple, team_uid: int, team: str) -> tuple:
        for player_dict in self.player_db_data["single"]:
            if player_info[0] == player_dict["player_name"]:
                self.player_mapper[team_uid][player_info] = self.player_db_data["player_id"]
                player_match = True
                break
        if not player_match:
            for player_dict in self.player_db_data["duplicate"]:
                if player_info[0] == player_dict["player_name"]:
                    player_id = input("Name of the player is duplicated for"
                                      " the same team for the same season. Set"
                                      " it manually: ")
                    self.player_mapper[team_uid][player_info[0]] = player_id

        if not player_match:
            error_message = (
                f"Player {player_info[0]} in team {team} ({team_uid}) is not"
                f"present in the database."             
                )
            common_functions.log_and_raise(error_message, ValueError)


    def update_PBP(self, pbp_data: dict) -> list:
        updated_pbp = []
        for play in pbp_data:
            pbp_o = self.get_PBP_class(pbp_data["play_type"])
            updated_play = pbp_o.update_play(play)
            updated_pbp.append(updated_play)

        return updated_pbp
    
                    
    def get_PBP_class(self, play_type: str):

        return self.UPDATE_CLASSES[play_type](
            self.player_mapper, self.HT_uid, self.VT_uid)



class UpdateShifts():


    NAME_PATTERN = (
        rf"(?P<number>\d+)\s+(?P<surname>[A-Z]+),\s+"
        rf"(?P<first_name>[A-Z]+)"
        )
    
    SHIFT_PATTERN = rf"^(?P<shift>[0-9]{{1, 2}}:[0-9]{2})"


    def __init__(self):
        pass


    def update_players_shifts(self, shifts: dict) -> dict:
        updated_dict = {}
        for player_name_number in shifts:
            updated_name, number, updated_shifts = self.update_player_shifts(
                player_name_number = player_name_number,
                shifts=shifts[player_name_number])
            updated_dict[(updated_name, number)] = updated_shifts

        return updated_shifts
    
    
    def update_player_shifts(
            self, player_name_number: str, shifts: dict) -> tuple:
        updated_name, number = self.get_name_number(
            player_name_number=player_name_number)
        shifts = self.update_shifts(shifts)

        return updated_name, number, shifts
    

    def get_name_number(self, player_name_number: str) -> tuple:
        match = re.match(self.NAME_PATTERN, player_name_number)

        if not match:
            error_message = (
                f"Regex failed to match pattern for input: '"
                f"{player_name_number}'"
            )
            common_functions.log_and_raise(error_message, ValueError)
        player_dict = match.groupdict()
        player_name = f"{player_dict['first_name']} {player_dict['surname']}"
        
        return player_name.title(), player_dict["number"]
    

    def update_shifts(self, shifts: dict) -> dict:
        shifts_updated = {}        
        shifts_updated["period"] = get_updated_period(shifts["period"])
        shifts_updated["shift_start"] = self.get_updated_shift(
            shifts["shift_start"])
        shifts_updated["shift_end"] = self.get_updated_shift(
            shifts["shift_end"])
        
        return shifts_updated


    def get_updated_shift(self, shift_string: str):
        try:
            if not isinstance(shift_string, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(shift_string).__name__}"
                    )
                raise TypeError(error_message)
            match = re.match(self.SHIFT_PATTERN, shift_string)
            shift = match.group("shift")
            shift_seconds = common_functions.convert_to_seconds(shift)
            logger.debug(f"Pattern '{shift_string}' found")

            return shift_seconds
        except re.error as e:
            common_functions.log_and_raise(e, re.error)
        except TypeError as e:
            common_functions.log_and_raise(e, TypeError)


class UpdatePBP():


    UPDATE_CLASSES = {

    }

    SHOT_TYPES = [
        'backhand',
        'bat',
        'between legs',
        'cradle',
        'deflected',
        'failed attempt',
        'poke',
        'slap',
        'snap',
        'tip-in',
        'wrap-around',
        'wrist'
    ]


    ZONE_MAPPER = {
        "Neu.": "neutral",
        "Neu. Zone": "neutral",
        "Off.": "offensive",
        "Off. Zone": "offensive",
        "Def.": "defensive",
        "Def. Zone": "defensive",
    }

    PLAYER_PATTERN = rf"[\wÀ-ÖØ-öø-ÿ']+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*"

    MATCH_PATTERN = (
        rf"(Center|Right\sWing|Left\sWing|Defender)\s*-\s*"
        rf"(?P<player_name>{PLAYER_PATTERN})"
    )


    def __init__(self, player_mapper: dict, TH_uid: str, TV_uid: str):
        self.player_mapper = player_mapper
        self.team_uids = {"TH": TH_uid, "TV": TV_uid}


    def update_play(self, play: dict) -> dict:
        updated_play = {}
        updated_play["period"] = get_updated_period(play["period"])
        updated_play["time"] = self.get_updated_time(play["time"])
        updated_play["play_info"] = self.update_play_info(play["play_info"])

        
    def get_updated_time(self, time: str):
        try:
            if not isinstance(time, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(time).__name__}"
                    )
                common_functions.log_and_raise(error_message, TypeError)
            shift_seconds = common_functions.convert_to_seconds(time)
            logger.debug(f"Pattern '{time}' found")

            return shift_seconds
        except TypeError as e:
            common_functions.log_and_raise(e, TypeError)


    def get_updated_poi(self, poi: dict) -> dict:
        updated_poi = {}
        for team_type in poi:
                team_uid = self.team_uids[team_type]
                updated_poi[team_uid] = self.get_updated_team_poi(
                    poi[team_type], team_uid)

        return updated_poi
    

    def get_updated_team_poi(self, team_poi: list, team_uid: int) -> list:
        updated_team_poi = []
        for player in team_poi:
            player_id = self.get_player_id_poi(self, player, team_uid)
            updated_team_poi.append(player_id)

        return updated_team_poi
    

    def update_zone(self, zone: str):
        #try: - add after longer testing
        updated_zone = self.ZONE_MAPPER[zone]
        #except KeyError:
        #    error_message = f"Unknown zone string: {zone}"
        #    common_functions.log_and_raise(error_message, KeyError)

        return updated_zone
    

    def update_shot_type(self, shot_type):
        shot_type = shot_type.strip().lower()
        if shot_type not in self.SHOT_TYPES:
            error_message = f"Shot type not known: {shot_type}"
            raise KeyError(error_message)
           # common_functions.log_and_raise(error_message, KeyError) add after longer testing
        
        return shot_type
    

    def get_player_uid(self, surname: str, player_number: int, team_uid: int):
        for player_tuple in self.player_mapper[team_uid]:
            if ((player_tuple[0] == surname) 
            and (player_tuple[1] == player_number)):
                return self.player_mapper[team_uid][player_tuple]
        error_message = (
            f"No player data found for player {surname} "
            f"({player_number})"
        )
        common_functions.log_and_raise(error_message, KeyError)

    
    def get_player_id_poi(self, player: str, team_uid: int) -> int:    
        try:
            if not isinstance(player, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(player).__name__}"
                    )
                raise TypeError(error_message)
            match = re.match(self, player)
            player_name = match.group("player_name")
            logger.debug(f"Pattern '{player_name}' found")
            player_id = self.player_mapper[team_uid][player_name]

            return player_id
        except re.error as e:
            common_functions.log_and_raise(e, re.error)
        except TypeError as e:
            common_functions.log_and_raise(e, TypeError)


    def update_play_info(self):
        pass


class UpdateFaceoff(UpdatePBP):


    def update_play_info(self, play: dict):

        updated_dict = {}
        updated_dict["winner_team_uid"] = team_map.get_team_uid_from_abbrevation(play["winning_team"])










        



