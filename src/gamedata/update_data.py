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


ZONE_MAPPER = {
    "def.": "defensive",
    "off.": "offensive",
    "neu.": "neutral"
}

SHOT_TYPE_MAPPER = {
    "backhand": "backhand",
    "bat": "bat",
    "between legs": "between legs",
    "cradle": "cradle",
    "deflected": "deflected",
    "failed attempt": "failed attempt",
    "poke": "poke",
    "slap": "slapshot",
    "snap": "snapshot",
    "tip-in": "tip-in",
    "wrap-around": "wrap-around",
    "wrist": "wristshot"
}

BLOCKED_BY_MAPPER = {
    "blocked by teammate": "teammate",
    "opponent-blocked by": "opponent",
    "blocked by other": "other"
}

DEFLECTION_TYPE_MAPPER = {

}


SHOT_RESULT_MAPPER = {

}

PENALTY_MAPPER = {

}

PERIOD_TYPE_MAPPER = {

}


class UpdateShifts():


    NAME_PATTERN = (
        rf"(?P<number>\d+)\s+"
        rf"(?P<surname>[\wÀ-ÖØ-öø-ÿ']+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*),"
        rf"\s+(?P<first_name>[A-Z]+)"
        )
    
    SHIFT_PATTERN = r"(?P<shift>\d{1,2}:\d{2})"


    def __init__(self):
        pass


    def update_players_shifts(self, shifts: dict) -> dict:
        updated_dict = {}
        for item in shifts:
            for player_name_number in item:
                updated_name, number, updated_shifts = self.update_player_shifts(
                    player_name_number = player_name_number,
                    shifts=item[player_name_number])
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
    

    def update_shifts(self, shifts: list) -> list:
        updated_shifts = []
        for shift in shifts:
            updated_shift = self.update_shift(shift)
            updated_shifts.append(updated_shift)

        return updated_shifts
    
    def update_shift(self, shift: dict) -> dict: 
        shifts_updated = {}        
        shifts_updated["period"] = get_updated_period(shift["period"])
        shifts_updated["shift_start"] = self.get_updated_shift(
            shift["shift_start"])
        shifts_updated["shift_end"] = self.get_updated_shift(
            shift["shift_end"])
        
        return shifts_updated


    def get_updated_shift(self, shift_string: str):
        try:
            if not isinstance(shift_string, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(shift_string).__name__}"
                    )
                raise TypeError(error_message)
            print(shift_string)
            match = re.search(self.SHIFT_PATTERN, shift_string)
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


    def get_player_uid(
            self, team_uid: int, player_number: int, team_abb: str) -> int:
        for player_info in self.player_mapper[team_uid]:
            if player_info[1] == player_number:
                return self.player_mapper[team_uid][player_info]
        error_message = (
            f"No player data found for player with number {player_number} "
            f"for team {team_abb} ({team_uid})"
        )
        common_functions.log_and_raise(error_message, KeyError)
        

class FaceoffUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:

        updated_dict = {}
        updated_dict["winner_team_uid"] = team_map.get_team_uid_from_abbrevation(play["winning_team"])
        if play['winning_team'] == play['l_team']:
            winning_player_number = play["l_player_number"]
            losing_team_id = team_map.get_team_uid_from_abbrevation(
                play["r_team"])
            losing_player_number = play['r_player_number']
            losing_team = play['r_team']
        else:
            winning_player_number = play["r_player_number"]
            losing_team_id = team_map.get_team_uid_from_abbrevation(
                play["l_team"])
            losing_player_number = play['l_player_number']
            losing_team = play['l_team']
        updated_dict['faceoff_winner_uid'] = self.get_player_uid(
                updated_dict["winner_team_uid"],
                winning_player_number,
                play['winning_team']
                )
        updated_dict['faceoff_loser_uid'] = self.get_player_uid(
                losing_team_id,
                losing_player_number,
                losing_team
                )
        updated_dict["losing_team_uid"] = losing_team_id

        return updated_dict
    

class BlockedShotUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["blocker_team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["blocked_team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["blocked_team"])
        updated_dict['blocker_player_uid'] = self.get_player_uid(
            updated_dict["blocker_team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict['blocked_player_uid'] = self.get_player_uid(
            updated_dict["blocked_team_uid"],
            play["blocked_player_number"],
            play["blocked_team"]
        )
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["blocked_by"] = BLOCKED_BY_MAPPER[play['blocked_by'].lower()]
        updated_dict["broke_stick"] = "broken_stick" in play 
        updated_dict["over_board"] = "over_board" in play 


class GoalUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["play_type"].lower()]
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        updated_dict["deflection_type"] = (
            DEFLECTION_TYPE_MAPPER[play["deflection_type"].lower()] 
            if "deflection_type" in play else None)
        updated_dict["penalty_shot"] = "penalty_shot" in play
        updated_dict["own_goal"] = "own_goal" in play
        if "assists" in play:
            updated_dict["assits"] = self.get_updated_assits(play["assits"])
    
        return updated_dict


    def get_updated_assits(self, assits: dict, team_uid: int, 
                           team_abb: str) -> dict:
        updated_assits = {}
        updated_assits["primary"] = self.get_updated_assist(
            assits[0], team_uid, team_abb)
        if len(assits) == 2:
            updated_assits["secondary"] = self.get_updated_assist(
                assits[1], team_uid, team_abb)
        
        return assits
    

    def get_updated_assist(
            self, assist: dict, team_uid: int, team_abb: str) -> dict:
        player_uid = self.get_player_uid(
            team_uid,
            assist["player_number"],
            team_abb
        )

        return player_uid
    

class ShotUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        updated_dict["deflection_type"] = (
            DEFLECTION_TYPE_MAPPER[play["deflection"].lower()] 
            if "deflection_type" in play else None)
        updated_dict["penalty_shot"] = "penalty_shot" in play
        updated_dict["broken_stick"] = "broken_stick" in play
        updated_dict["over_board"] = "over_board" in play
    
        return updated_dict
    

class HitUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["hitter_team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["hitted_team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["opponent_team"])
        updated_dict['hitter_player_uid'] = self.get_player_uid(
            updated_dict["hitter_team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict['hitted_player_uid'] = self.get_player_uid(
            updated_dict["hitted_team_uid"],
            play["opponent_player_number"],
            play["opponent_team"]
        )
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower]

        return updated_dict
    

class GiveAwayUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class TakeAwayUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class MissedShotUpdater(UpdatePBP):


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["shot_result"] = play["shot_result"].lower()
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        updated_dict["penalty_shot"] = "penalty_shot" in play
        updated_dict["broken_stick"] = "broken_stick" in play
        updated_dict["over_board"] = "over_board" in play
    
        return updated_dict
    

class PenaltyUpdater():
    
    
    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["team"])
        updated_dict["player_uid"] = self.get_player_uid(
            updated_dict["team_uid"],
            play["player_number"],
            play["team"]
        )
        updated_dict["penalty_type"] = PENALTY_MAPPER[play["penalty_type"].lower()]
        updated_dict["penalty_minutes"] = int(play["penalty_minutes"])
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["major"] = "penalty_modifier" in play
        if "drawn_team" in play:
            updated_dict["drawn_team_uid"] = team_map.get_team_uid_from_abbrevation(
                play["drawn_team"])
            updated_dict["drawn_player_uid"] = self.get_player_uid(
                updated_dict["drawn_team_uid"],
                play["drawn_player_number"],
                play["drawn_team"]
            )
        if "served_player_name" in play:
            updated_dict["served_player_uid"] = self.get_player_uid(
                updated_dict["team_uid"],
                play["served_player_number"],
                play["team"]
            )


class SimpleReturnUpdater():


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        for key in play:
            updated_dict[key] = play[key].lower()
        
        return updated_dict
    

class PeriodUpdater():


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["period_type"] = PERIOD_TYPE_MAPPER[play["period_type"].lower()]
        updated_dict["time"] = common_functions.convert_to_seconds(
            play["time"])
        updated_dict["timezone"] = play["timezone"]

        return updated_dict


class ChallengeUpdater():


    def update_player_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["reason"] = play["reason"].lower()
        updated_dict["result"] = play["result"].lower()
        updated_dict["team"] = play["team"] if "team" in play else None
        updated_dict["league_challenge"] = (True if "league_challenge" in play 
                                            else False)
        
        return updated_dict
    

class UpdateGameDate():


    UPDATE_CLASSES = {
        "BLOCK": BlockedShotUpdater,
        "CHL": ChallengeUpdater,
        "DELPEN": SimpleReturnUpdater,
        "FAC": FaceoffUpdater,
        "GIVE": GiveAwayUpdater,
        "GOAL": GoalUpdater,
        "HIT": HitUpdater,
        "MISS": MissedShotUpdater,
        "PEND": PeriodUpdater,
        "PENL": PenaltyUpdater,
        "PSTR": PeriodUpdater,
        "SOC": PeriodUpdater,
        "SHOT": ShotUpdater,
        "STOP": SimpleReturnUpdater,
        "TAKE": TakeAwayUpdater
    }


    def __init__(self, player_db_data: list):
        self.player_db_data = player_db_data
        self.player_mapper = {}
        self.HT_uid = None
        self.VT_uid = None


    def update_game_data(self, game_data: dict) -> dict:
        updated_data = {}
        updated_data = self.get_general_info(updated_data, game_data)
        updated_data["shifts"] = self.update_shifts(game_data)
        self.match_players_to_uid(updated_data)
        updated_data["PBP"] = self.update_PBP(game_data)

        return updated_data
    

    def get_general_info(self, updated_data: dict, game_data: dict) -> dict:
        updated_data["HT"] = self.get_set_team_uid(game_data["HT"], "HT")
        updated_data["VT"] = self.get_set_team_uid(game_data["VT"], "VT")
        updated_data["date"] = game_data["date"]
        updated_data["stadium"] = game_data["stadium"]
        updated_data["start_time_UTC"] = game_data["start_time_UTC"]

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


    def update_shifts(self, game_data: dict) -> dict:
        shift_dict = {}
        us_o = UpdateShifts()
        shift_dict["TH"] = us_o.update_players_shifts(game_data["HTS"])
        shift_dict["TV"] = us_o.update_players_shifts(game_data["VTS"])

        return shift_dict
    

    def match_players_to_uid(
            self, scraped_data: dict, team_abb: str) -> None:
        for team_type in scraped_data['shift_data'].keys():
            team_uid = scraped_data[team_type]
            self.match_team_players_to_uid(
                scraped_data['shift_data'][team_type], team_uid, team_abb)


    def match_team_players_to_uid(
            self, team_shifts: dict, team_uid: int, 
            team_abb: str) -> None:
        for player_info in team_shifts:
            self.match_player_to_uid(player_info, team_uid, team_abb)

    
    def match_player_to_uid(
            self, player_info: tuple, team_uid: int, team_abb: str) -> tuple:
        self.player_mapper[team_uid] = {}
        for player_dict in self.player_db_data["single"]:
            if player_info[0] == player_dict["player_name"]:
                self.player_mapper[team_uid][player_info] = player_dict["player_id"]
                player_match = True
                break
        if not player_match:
            for player_dict in self.player_db_data["duplicate"]:
                if player_info[0] == player_dict["player_name"]:
                    player_id = input("Name of the player is duplicated for"
                                      " given team season combination. Set"
                                      " it manually: ")
                    self.player_mapper[team_uid][player_info[0]] = player_id

        if not player_match:
            error_message = (
                f"Player {player_info[0]} in team {team_abb} ({team_uid}) is not"
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









    



















        



