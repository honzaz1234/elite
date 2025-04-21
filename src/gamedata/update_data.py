import re
import unicodedata

import common_functions
import  mappers.team_mappers as team_map

from logger.logging_config import logger


def get_updated_period(period: str) -> int:

    try:
        result = re.findall("(1|2|3|OT)", period)[0]

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
    "blocked by": "opponent",
    "blocked by other": "other"
}

DEFLECTION_TYPE_MAPPER = {

}


SHOT_RESULT_MAPPER = {
    "goalpost": "goalpost", 
    "hit crossbar": "hit crossbar", 
    "over net": "over net", 
    "wide of net": "wide of net"
}

PENALTY_MAPPER = {
    'abuse of officials - bench': 'abuse of officials - bench',
    'boarding': 'boarding',
    'broken stick': 'broken stick',
    'closing hand on puck': 'closing hand on puck',
    'cross-checking': 'cross-checking',
    'delay game': 'delay game',
    'delay game - bench': 'delay game - bench',
    'delay game - fo viol - hand': 'delay game - fo viol - hand',
    'delay game - puck over glass': 'delay game - puck over glass',
    'delay game - unsucc chlg': 'delay game - unsucc chlg',
    'elbowing': 'elbowing',
    'embellishment': 'embellishment',
    'fighting': 'fighting',
    'game misconduct': 'game misconduct',
    'goalie leave crease': 'goalie leave crease',
    'high-sticking': 'high-sticking',
    'high-sticking - double minor': 'high-sticking - double minor',
    'holding': 'holding',
    'holding the stick': 'holding the stick',
    'hooking': 'hooking',
    'illegal check to head': 'illegal check to head',
    'instigator': 'instigator',
    'instigator - misconduct': 'instigator - misconduct',
    'interference': 'interference',
    'interference on goalkeeper': 'interference on goalkeeper',
    'kneeing': 'kneeing',
    'match penalty': 'match penalty',
    'ps-goalkeeper displaced net': 'ps-goalkeeper displaced net',
    'ps-holding on breakaway': 'ps-holding on breakaway',
    'ps-hooking on breakaway': 'ps-hooking on breakaway',
    'ps-slash on breakaway': 'ps-slash on breakaway',
    'ps-tripping on breakaway': 'ps-tripping on breakaway',
    'puck thrown fwd - goalkeeper': 'puck thrown fwd - goalkeeper',
    'roughing': 'roughing',
    'roughing - removing opp helmet': 'roughing - removing opp helmet',
    'slashing': 'slashing',
    'throwing equipment': 'throwing equipment',
    'too many men/ice - bench': 'too many men/ice - bench',
    'tripping': 'tripping',
    'unsportsmanlike conduct': 'unsportsmanlike conduct',
    'unsportsmanlike conduct-bench': 'unsportsmanlike conduct-bench',
}

PERIOD_TYPE_MAPPER = {
    "period start": "period start",
    "period end": "period end"
}


class UpdateShifts():

    NAME_REGEX = "[\wÀ-ÖØ-öø-ÿ']+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*"

    NAME_PATTERN = (
        rf"(?P<number>\d+)\s+"
        rf"(?P<surname>{NAME_REGEX}),"
        rf"\s+(?P<first_name>{NAME_REGEX})"
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

        return updated_dict
    
    
    def update_player_shifts(
            self, player_name_number: str, shifts: dict) -> tuple:
        updated_name, number = self.get_name_number(
            player_name_number=player_name_number)
        print(updated_name)
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
        player_name = f'{player_dict["first_name"]} {player_dict["surname"]}'
        
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
        "backhand",
        "bat",
        "between legs",
        "cradle",
        "deflected",
        "failed attempt",
        "poke",
        "slap",
        "snap",
        "tip-in",
        "wrap-around",
        "wrist"
    ]


    ZONE_MAPPER = {
        "Neu.": "neutral",
        "Neu. Zone": "neutral",
        "Off.": "offensive",
        "Off. Zone": "offensive",
        "Def.": "defensive",
        "Def. Zone": "defensive",
    }

    PLAYER_PATTERN = rf"[A-ZÀ-ÖØ-Þ']+(?:[-' ][A-ZÀ-ÖØ-Þ']+)*"

    MATCH_PATTERN = (
        rf"(Center|Right\sWing|Left\sWing|Defender)\s*-\s*"
        rf"(?P<player_name>{PLAYER_PATTERN})"
    )


    def __init__(
            self, player_mapper: dict, team_type_to_abb: dict, team_abb_to_db_id: dict):
        self.player_mapper = player_mapper
        self.team_type_to_abb = team_type_to_abb
        self.team_abb_to_db_id = team_abb_to_db_id


    def update_play(self, play: dict) -> dict:
        updated_play = {}
        updated_play["period"] = get_updated_period(play["period"])
        updated_play["play_type"] = play["play_type"]
        updated_play["time"] = self.get_updated_time(play["time"])
        updated_play["play_info"] = self.update_play_info(play["play_info"])

        return updated_play

        
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
                team_abb = self.team_type_to_abb[team_type]
                team_id = self.team_abb_to_db_id[team_abb]
                updated_poi[team_id] = self.get_updated_team_poi(
                    poi[team_type], team_id, team_abb)

        return updated_poi
    

    def get_updated_team_poi(
            self, team_poi: list, team_id: int, team_abb: str) -> list:
        updated_team_poi = []
        for player_number in team_poi:
            player_id = self.get_player_id(
                team_id, player_number, team_abb)
            updated_team_poi.append(player_id)

        return updated_team_poi
    

    def get_player_id(
            self, team_id: int, player_number: int, team_abb: str) -> int:
        for player_info in self.player_mapper[team_id]:
            if player_info[1] == player_number:
                return self.player_mapper[team_id][player_info]
        error_message = (
            f"No player data found for player with number {player_number} "
            f"for team {team_abb} ({team_id})"
        )
        common_functions.log_and_raise(error_message, KeyError)
    

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
    

    def update_play_info(self, play: dict):
        pass

        
class FaceoffUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:

        updated_dict = {}
        if play["winning_team"] == play["l_team"]:
            winner_team_id = self.team_abb_to_db_id[play["l_team"]]
            winning_player_number = play["l_player_number"]
            losing_team_id = self.team_abb_to_db_id[play["r_team"]]
            losing_player_number = play["r_player_number"]
            losing_team = play["r_team"]
        else:
            winner_team_id = self.team_abb_to_db_id[play["r_team"]]
            winning_player_number = play["r_player_number"]
            losing_team_id = self.team_abb_to_db_id[play["l_team"]]
            losing_player_number = play["l_player_number"]
            losing_team = play["l_team"]
        updated_dict["faceoff_winner_id"] = self.get_player_id(
                winner_team_id,
                winning_player_number,
                play["winning_team"],
                )
        updated_dict["faceoff_loser_id"] = self.get_player_id(
                losing_team_id,
                losing_player_number,
                losing_team,
                )
        updated_dict["winner_team_id"] = winner_team_id
        updated_dict["losing_team_id"] = losing_team_id

        return updated_dict
    

class BlockedShotUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        blocker_team_id = self.team_abb_to_db_id[play["team"]]
        blocked_team_id = self.team_abb_to_db_id[play["blocked_team"]]
        updated_dict["blocker_player_id"] = self.get_player_id(
            blocker_team_id,
            play["player_number"],
            play["team"],
        )
        updated_dict["blocked_player_id"] = self.get_player_id(
            blocked_team_id,
            play["blocked_player_number"],
            play["blocked_team"],
        )
        updated_dict["blocker_team_id"] = blocker_team_id
        updated_dict["blocked_team_id"] = blocked_team_id
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["blocked_by"] = BLOCKED_BY_MAPPER[play["blocked_by"].lower()]
        updated_dict["broke_stick"] = play["broken_stick"] is not None
        updated_dict["over_board"] = play["over_board"] is not None

        return updated_dict


class GoalUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["goal"]["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            play["goal"]["player_number"],
            play["goal"]["team"],
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["goal"]["play_type"].lower()]
        updated_dict["zone"] = ZONE_MAPPER[play["goal"]["zone"].lower()]
        updated_dict["distance"] = (int(play["goal"]["distance"])
                                    if "distance" in play["goal"] else None)
        updated_dict["deflection_type"] = (
            DEFLECTION_TYPE_MAPPER[play["goal"]["deflection_type"]] 
            if play["goal"]["deflection_type"] is not None else None)
        updated_dict["penalty_shot"] = play["goal"]["penalty_shot"] is not None
        updated_dict["own_goal"] = "own_goal" in play["goal"]
        if "assists" in play:
            updated_dict["assists"] = self.get_updated_assits(
                play["assists"], updated_dict["team_id"], play["goal"]["team"])
    
        return updated_dict


    def get_updated_assits(self, assits: dict, team_id: int, 
                           team_abb: str) -> dict:
        updated_assits = {}
        updated_assits["primary"] = self.get_updated_assist(
            assits[0], team_id, team_abb)
        if len(assits) == 2:
            updated_assits["secondary"] = self.get_updated_assist(
                assits[1], team_id, team_abb)
        
        return assits
    

    def get_updated_assist(
            self, assist: dict, team_uid: int, team_abb: str) -> dict:
        player_id = self.get_player_id(
            team_uid,
            assist["player_number"],
            team_abb,
        )

        return player_id
    

class ShotUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        updated_dict["deflection_type"] = (
            DEFLECTION_TYPE_MAPPER[play["deflection"].lower()] 
            if "deflection_type" in play else None)
        updated_dict["penalty_shot"] = play["penalty_shot"] is not None
        updated_dict["broken_stick"] = play["broken_stick"] is not None
        updated_dict["over_board"] = play["over_board"] is not None
    
        return updated_dict
    

class HitUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        hitter_team_id = self.team_abb_to_db_id[play["team"]]
        hitted_team_uid = self.team_abb_to_db_id[play["opponent_team"]]
        updated_dict["hitter_player_id"] = self.get_player_id(
            hitter_team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["hitted_player_id"] = self.get_player_id(
            hitted_team_uid,
            play["opponent_player_number"],
            play["opponent_team"]
        )
        updated_dict["hitter_team_id"] = hitter_team_id
        updated_dict["hitted_team_id"] = hitted_team_uid
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class GiveAwayUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class TakeAwayUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class MissedShotUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = SHOT_TYPE_MAPPER[play["shot_type"].lower()]
        updated_dict["shot_result"] = SHOT_RESULT_MAPPER[play["shot_result"].lower()]
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        updated_dict["penalty_shot"] = play["penalty_shot"] is not None
        updated_dict["broken_stick"] = play["broken_stick"] is not None
        updated_dict["over_board"] = play["over_board"] is not None
    
        return updated_dict
    

class PenaltyUpdater(UpdatePBP):
    
    
    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_uid"] = self.get_player_id(
            team_id,
            play["player_number"],
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["penalty_type"] = PENALTY_MAPPER[play["penalty_type"].lower().strip()]
        updated_dict["penalty_minutes"] = int(play["penalty_minutes"])
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        if "penalty_modifier" in play:
            if play["penalty_modifier"] is not None:
                updated_dict["major"] = True
            else:
                updated_dict["major"] = False
        else:
            updated_dict["major"] = False
        if "drawn_team" in play:
            drawn_team_id = self.team_abb_to_db_id[play["drawn_team"]]
            updated_dict["drawn_player_id"] = self.get_player_id(
                drawn_team_id,
                play["drawn_player_number"],
                play["drawn_team"]
            )
            updated_dict["drawn_team_id"] = drawn_team_id
        if "served_player_name" in play:
            updated_dict["served_player_id"] = self.get_player_id(
                team_id,
                play["served_player_number"],
                play["team"]
            )
    
        return updated_dict


class SimpleReturnUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        for key in play:
            updated_dict[key] = play[key].lower()
        
        return updated_dict
    

class PeriodUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["period_type"] = PERIOD_TYPE_MAPPER[play["period_type"].lower()]
        updated_dict["time"] = common_functions.convert_to_seconds(
            play["time"])
        updated_dict["timezone"] = play["timezone"]

        return updated_dict


class ChallengeUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["reason"] = play["reason"].lower()
        updated_dict["result"] = play["result"].lower()
        updated_dict["team"] = play["team"] is not None
        updated_dict["league_challenge"] = play["league_challenge"] is not None
        
        return updated_dict
    

class UpdateGameData():


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

    SKIP_PLAY = ["PGSTR", "PGEND", "ANTHEM", "GEND", "GOFF"]


    def __init__(self, player_db_data: dict, nhl_db_mapper: dict):
        self.player_db_data = player_db_data
        self.player_mapper = {}
        self.team_type_to_abb = {}
        self.team_abb_to_db_id = {}
        self.nhl_db_mapper = nhl_db_mapper


    def update_game_data(self, game_data: dict) -> dict:
        updated_data = {}
        updated_data = self.get_general_info(updated_data, game_data)
        updated_data["shifts"] = self.update_shifts(game_data)
        self.match_players_to_db_id(updated_data)
        updated_data["PBP"] = self.update_PBP(game_data["PBP"])

        return updated_data
    

    def get_general_info(self, updated_data: dict, game_data: dict) -> dict:
        self.set_dictionaries(game_data)
        self.update_nhl_db_mapper()
        updated_data["HT"] = self.get_team_id(game_data["HT"])
        updated_data["VT"] = self.get_team_id(game_data["VT"])
        updated_data["TH"] = game_data["HT"]
        updated_data["TV"] = game_data["VT"]  
        updated_data["date"] = game_data["date"]
        updated_data["stadium"] = game_data["stadium"]
        updated_data["start_time_UTC"] = game_data["start_time_UTC"]

        return updated_data
    
    
    def get_team_id(self, team_abb: str) -> int:
        team_uid = team_map.get_team_uid_from_abbrevation(team_abb)
        team_id = self.player_db_data[team_uid]["single"][0]["team_id"]

        return team_id
    

    def set_dictionaries(self, game_data: dict) -> None:
        self.team_type_to_abb = {"TH": game_data["HT"], "TV": game_data["VT"]}
        ht_id = self.get_team_id(game_data["HT"])
        vt_id = self.get_team_id(game_data["VT"])
        self.team_abb_to_db_id = {
            game_data["HT"]: ht_id, 
            game_data["VT"]: vt_id
            }
        

    def update_nhl_db_mapper(self):
        for team_id in self.team_abb_to_db_id.values():
            if team_id not in self.nhl_db_mapper:
                self.nhl_db_mapper[team_id] = {}


    def update_shifts(self, game_data: dict) -> dict:
        shift_dict = {}
        us_o = UpdateShifts()
        shift_dict["TH"] = us_o.update_players_shifts(game_data["HTS"])
        shift_dict["TV"] = us_o.update_players_shifts(game_data["VTS"])

        return shift_dict
    

    def match_players_to_db_id(
            self, scraped_data: dict) -> None:
        for team_type in scraped_data["shifts"].keys():
            team_abb = self.team_type_to_abb[team_type]
            team_uid = team_map.get_team_uid_from_abbrevation(team_abb)
            team_id = self.player_db_data[team_uid]["single"][0]["team_id"]
            self.player_mapper[team_id] = {}
            self.match_team_players_to_db_id(
                scraped_data["shifts"][team_type], team_uid, team_id, team_abb)


    def match_team_players_to_db_id(
            self, team_shifts: dict, team_uid: int, 
            team_id: int, team_abb: str) -> None:
        for player_info in team_shifts:
            self.match_player_to_db_id(
                player_info, team_uid, team_id, team_abb)

    
    def match_player_to_db_id(
            self, player_info: tuple, team_uid: int, team_id: int, 
            team_abb: str) -> None:
            player_matched = self.try_find_match_with_nhl_db_mapper(
                player_info, team_id)
            if player_matched:
                return
            matcher_o = SingleMatchFinder(
                player_info, self.player_db_data[team_uid]["single"],
                self.nhl_db_mapper[team_id])
            player_matched = matcher_o.iterrate_to_find_match_wrapper()
            if player_matched:
                self.player_mapper[team_id][player_info] = matcher_o.player_id
                return
            matcher_o = DuplicatesMatchFinder(
                player_info, self.player_db_data[team_uid]["duplicates"],
                self.nhl_db_mapper[team_id])
            player_matched = matcher_o.iterrate_to_find_match_wrapper()
            if player_matched:
                self.player_mapper[team_id][player_info] = matcher_o.player_id
                return
            self.player_mapper[team_id][player_info] = matcher_o.input_match_manually(player_info)
          #  if player_matched:
           #     return 
           # error_message = (
           #     f"Player {player_info[0]} in team {team_abb} """
           #     f"(UID: {team_uid}) is not present in the "
           #     f"database"             
           #  )
           # common_functions.log_and_raise(error_message, ValueError)


    def try_find_match_with_nhl_db_mapper(
            self, player_info, team_id) -> bool:
        for nhl_name in self.nhl_db_mapper[team_id]:
            mapper_dict = self.nhl_db_mapper[team_id][nhl_name]
            if ((player_info[0] == mapper_dict["db_name"]) 
            & (player_info[1] == mapper_dict["number"])):
                self.player_mapper[team_id][player_info] = (
                    mapper_dict["db_name"],
                    mapper_dict["number"]
                )

                return True
            
        return False


    def update_PBP(self, pbp_data: dict) -> list:
        updated_pbp = []
        for play in pbp_data:
            if play["play_type"] in self.SKIP_PLAY:
                continue
            pbp_o = self.get_PBP_class(play["play_type"])
            updated_play = pbp_o.update_play(play)
            updated_pbp.append(updated_play)

        return updated_pbp
    
                    
    def get_PBP_class(self, play_type: str):

        return self.UPDATE_CLASSES[play_type](
            self.player_mapper, self.team_type_to_abb, self.team_abb_to_db_id)
    

class MatchFinder():


    def __init__(
            self, player_info: tuple, db_mapper: dict, nhl_db_mapper: dict):
        self.player_info = player_info
        self.db_mapper = db_mapper
        self.player_id = None
        self.nhl_db_mapper = nhl_db_mapper
        self.original_name = None


    def iterrate_to_find_match_wrapper(self) -> bool:
        name_matched = self.iterrate_to_find_match()
        if not name_matched:
            name_matched = self.iterrate_to_find_normalized_match()
        
        return name_matched


    def iterrate_to_find_match(self) -> bool:
        for player_dict in self.db_mapper:
            name_matched = self.try_to_find_match(player_dict)
            if name_matched:

                return True
            
        return False
    

    def try_to_find_match(self) -> bool:
        pass


    def iterrate_to_find_normalized_match(self) -> bool:
        pass


    def normalize_scraped_name(self, name: str) -> str:
        normalized = unicodedata.normalize("NFD", name)
        ascii_name = "".join(c for c in normalized if not unicodedata.combining(c))

        return ascii_name
    
    
    def create_match_dict(self, player_info, player_dict):
        return {
            "db_name": self.original_name, 
            "number": player_info[1], 
            "player_id": player_dict["player_id"]
            }
    

    def input_match_manually(self, player_info):
        logger.info(rf"No match was find for {player_info}"
                    rf" in db or NHL elite mapper."
                    rf" Input the db name and player id manually.")
        name = input("Input db player name: ")
        player_id = input("Input player id:" )
        return {
            "db_name": name, 
            "number": player_info[1], 
            "player_id": player_id
            }


class SingleMatchFinder(MatchFinder):


    def try_to_find_match(self, player_dict) -> bool:
        if self.player_info[0].lower() == player_dict["player_name"].lower():
            self.player_id = player_dict["player_id"]

            return True
        
        return False
    

    def iterrate_to_find_normalized_match(self) -> bool:
        for player_dict in self.db_mapper:
            self.original_name = player_dict["player_name"]
            updated_player_dict = player_dict.copy()
            updated_player_dict["player_name"] = self.normalize_scraped_name(
                updated_player_dict["player_name"])
            name_matched = self.try_to_find_match(updated_player_dict)
            if name_matched:
               #match_confirmed = input(f"Match for player {self.player_info}"
               #                         f" was find after normalisation of"
               #                         f" name of db entry {player_dict}."
               #                         f"Write {True} if match is correct"
               #                         f" and {False} otherwise.")
               match_confirmed = True
               if match_confirmed:
                    self.nhl_db_mapper[self.player_info[0]] = self.create_match_dict(
                        self.player_info, player_dict)
                    self.player_id = player_dict["player_id"]   

                    return True
                
        return False
    

class DuplicatesMatchFinder(MatchFinder):


    def try_to_find_match(self, player_dict) -> bool:
        if self.player_info[0].lower() == player_dict["player_name"].lower():
            self.player_id = input("Name of the player is duplicated for"
                            " given team season combination. Set"
                            " it manually: ")
            self.nhl_db_mapper[self.player_info] = self.create_match_dict(
                         self.player_info, player_dict)
            
            return True
        
        return False
    

    def iterrate_to_find_normalized_match(self) -> bool:
        for player_dict in self.db_mapper:
            self.original_name = player_dict["player_name"]
            updated_player_dict = player_dict.copy()
            updated_player_dict["player_name"] = self.normalize_scraped_name(
                updated_player_dict["player_name"])
            name_matched = self.try_to_find_match(updated_player_dict)
            if name_matched:
                match_confirmed = logger.info(
                    f"Match for player {self.player_info}"
                    f" was find after normalisation of"
                    f" name of db entry {player_dict}.")
                if match_confirmed:

                    return True
                
        return False
    

        










    



















        



