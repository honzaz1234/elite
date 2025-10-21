import re
import unicodedata

from datetime import datetime
from decorators import time_execution
from sqlalchemy.sql.schema import Table

import common_functions as cf
import  mappers.team_mappers as team_map
import  database_creator.database_creator as db

from errors import MissingPlayer, MissingPlayerID, MissingPlayKeyError, TooManyPOIError, UpdateGameDataError, UpdatePlayError
from logger.logging_config import logger


def get_updated_period(period: str) -> int:

    try:
        result = re.findall("([0-9]+|OT|SO)", period)[0]

        return result
    
    except IndexError:
        error_message = f"Invalid value: {period}"
        cf.log_and_raise(error_message, ValueError)
    except TypeError:
        error_message = (
            f"TypeError: Expected str, int, or float, but got"
            f" {type(period).__name__}"
        )
        cf.log_and_raise(error_message, TypeError)


ZONE_MAPPER = {
    "def.": "defensive",
    "off.": "offensive",
    "neu.": "neutral"
}


BLOCKED_BY_MAPPER = {
    "blocked by teammate": "teammate",
    "opponent-blocked by": "opponent",
    "blocked by": "opponent",
    "blocked by other": "other"
}


class UpdateShifts():

    SURNAME_REGEX = "[\wÀ-ÖØ-öø-ÿ']+(?:[-' ][\wÀ-ÖØ-öø-ÿ]+)*"
    FIRST_NAME_REGEX = "[\wÀ-ÖØ-öø-ÿ'\.]+(?:[-' ][\wÀ-ÖØ-öø-ÿ\.]+)*"

    NAME_PATTERN = (
        rf"(?P<number>\d+)\s+"
        rf"(?P<surname>{SURNAME_REGEX}),"
        rf"\s+(?P<first_name>{FIRST_NAME_REGEX})"
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
        shifts = self.update_shifts(shifts)

        return updated_name, number, shifts
    

    def get_name_number(self, player_name_number: str) -> tuple:
        match = re.match(self.NAME_PATTERN, player_name_number)

        if not match:
            error_message = (
                f"Regex failed to match pattern for input: '"
                f"{player_name_number}'"
            )
            cf.log_and_raise(error_message, ValueError)
        player_dict = match.groupdict()
        player_name = f'{player_dict["first_name"]} {player_dict["surname"]}'
        
        return player_name.title(), int(player_dict["number"])
    

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
            shift_seconds = cf.convert_to_seconds(shift)
            logger.debug("Pattern '%s' found", shift_string)

            return shift_seconds
        except re.error as e:
            cf.log_and_raise(e, re.error)
        except TypeError as e:
            cf.log_and_raise(e, TypeError)


class UpdatePBP():


    PLAYER_PATTERN = rf"[A-ZÀ-ÖØ-Þ']+(?:[-' ][A-ZÀ-ÖØ-Þ']+)*"

    MATCH_PATTERN = (
        rf"(Center|Right\sWing|Left\sWing|Defender)\s*-\s*"
        rf"(?P<player_name>{PLAYER_PATTERN})"
    )


    def __init__(
            self, match_player_mapper: dict, team_type_to_abb: dict, team_abb_to_db_id: dict, look_ups: dict):
        self.match_player_mapper = match_player_mapper
        self.team_type_to_abb = team_type_to_abb
        self.team_abb_to_db_id = team_abb_to_db_id
        self.look_ups = look_ups 


    def update_play(self, play: dict) -> dict:
        updated_play = {}
        updated_play["period"] = get_updated_period(play["period"])
        updated_play["play_type"] = play["play_type"]
        updated_play["time"] = self.get_updated_time(play["time"])
        updated_play["poi"] = self.get_updated_poi(play["poi"])
        if "error" not in play:
            try:
                updated_play["play_info"] = self.update_play_info_wrapper(
                play["play_info"])
            except (MissingPlayKeyError):
                cf.log_and_raise(
                    None, UpdatePlayError, play=play)
        else:
            updated_play["play_desc"] = play["play_desc"]
            updated_play["error"] = play["error"]

        return updated_play

        
    def get_updated_time(self, time: str):
        try:
            if not isinstance(time, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(time).__name__}"
                    )
                cf.log_and_raise(error_message, TypeError)
            shift_seconds = cf.convert_to_seconds(time)
            logger.debug("Pattern '%s' found", time)

            return shift_seconds
        except TypeError as e:
            cf.log_and_raise(e, TypeError)


    def get_updated_poi(self, poi: dict) -> dict:
        updated_poi = {}
        for team_type in poi:
                team_abb = self.team_type_to_abb[team_type]
                team_id = self.team_abb_to_db_id[team_abb]
                try:
                    updated_poi[team_id] = self.get_updated_team_poi(
                        poi[team_type], team_id, team_abb)
                except TooManyPOIError:
                    error_type = "too_many_poi"
                    self.create_poi_error_entry(
                        updated_poi, poi[team_type], team_id, error_type)
                except  MissingPlayerID:
                    error_type = "missing_n"
                    self.create_poi_error_entry(
                        updated_poi, poi[team_type], team_id, error_type)

        return updated_poi
    

    def create_poi_error_entry(
            self, updated_poi: dict, poi: dict, team_id: int, 
            error_type: str) -> dict:
        if "error" not in updated_poi:
            updated_poi["error"] = {}
        updated_poi["error"][team_id] = {}
        updated_poi["error"][team_id]["poi"] = poi
        updated_poi["error"][team_id]["error_type"] = error_type

        return updated_poi

    
    def get_updated_team_poi(
            self, team_poi: list, team_id: int, team_abb: str) -> list:
        updated_team_poi = []
        if len(team_poi) > 6:
            cf.log_and_raise(
                None, TooManyPOIError, poi=team_poi, team_abb=team_abb)
            
        for player_number in team_poi:
            try:
                player_id = self.get_player_id(
                    team_id, int(player_number), team_abb)
                updated_team_poi.append(player_id)
            except KeyError as e:
                cf.log_and_raise(
                    None, 
                    MissingPlayerID, 
                    team_id=team_id,
                    team_abb=team_abb,
                    player_number=player_number)

        return updated_team_poi
    

    def get_player_id(
            self, team_id: int, player_number: int, team_abb: str) -> int:
        for player_info in self.match_player_mapper[team_id]:
            if player_info[1] == player_number:
                return self.match_player_mapper[team_id][player_info]
        error_message = (
            f"No player data found for player with number {player_number} "
            f"for team {team_abb} ({team_id})"
        )
        cf.log_and_raise(error_message, KeyError)
    

    def update_shot_type(self, shot_type):
        shot_type = shot_type.strip().lower()
        if shot_type not in self.SHOT_TYPES:
            error_message = f"Shot type not known: {shot_type}"
            raise KeyError(error_message)
           # cf.log_and_raise(error_message, KeyError) add after longer testing
        
        return shot_type
    

    def update_play_info_wrapper(self, play_info: dict) -> dict:
        try:
            updated_play = self.update_play_info(play_info)
        except KeyError:
            cf.log_and_raise(
                None, MissingPlayKeyError, play_info=play_info)

        return updated_play


    def update_play_info(self, play: dict) -> dict:
        pass


    def map_value_from_look_up(
            self, value: str, mapper: dict, table: Table) -> str:
        value = value.strip().lower()
        if value not in mapper[table]:
            logger.info(
                "New value %s added to the table %s", 
                value, table.__tablename__
                )
            new_index = max(mapper[table].values(), default=0) + 1
            mapper[table][value] = new_index
            logger.info(
                "New value %s added to the mapper of table %s", 
                value, table.__tablename__
                )
                
        return value


class FaceoffUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:

        updated_dict = {}
        if play["winning_team"] == play["l_team"]:
            winner_team_id = self.team_abb_to_db_id[play["l_team"]]
            winning_player_number = int(play["l_player_number"])
            losing_team_id = self.team_abb_to_db_id[play["r_team"]]
            losing_player_number = int(play["r_player_number"])
            losing_team = play["r_team"]
        else:
            winner_team_id = self.team_abb_to_db_id[play["r_team"]]
            winning_player_number = int(play["r_player_number"])
            losing_team_id = self.team_abb_to_db_id[play["l_team"]]
            losing_player_number = int(play["l_player_number"])
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
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class BlockedShotUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        blocker_team_id = self.team_abb_to_db_id[play["team"]]
        blocked_team_id = self.team_abb_to_db_id[play["blocked_team"]]
        updated_dict["blocker_id"] = self.get_player_id(
            blocker_team_id,
            int(play["player_number"]),
            play["team"],
        )
        updated_dict["shooter_id"] = self.get_player_id(
            blocked_team_id,
            int(play["blocked_player_number"]),
            play["blocked_team"],
        )
        updated_dict["blocker_team_id"] = blocker_team_id
        updated_dict["shooter_team_id"] = blocked_team_id
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["shot_type"] = self.map_value_from_look_up(
            play["shot_type"], self.look_ups, 
            db.ShotType
            )
        updated_dict["blocked_by"] = self.map_value_from_look_up(
            play["blocked_by"], self.look_ups, 
            db.BlockerType
            )
        updated_dict["broken_stick"] = play["broken_stick"] is not None
        updated_dict["over_board"] = play["over_board"] is not None

        return updated_dict


class GoalUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["goal"]["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            int(play["goal"]["player_number"]),
            play["goal"]["team"],
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = (
            self.map_value_from_look_up(
            play["goal"]["shot_type"], self.look_ups, 
            db.ShotType
            )
            if "shot_type" in play["goal"] else None
            )
        updated_dict["zone"] = ZONE_MAPPER[play["goal"]["zone"].lower()]
        updated_dict["distance"] = (
            int(play["goal"]["distance"])
            if "distance" in play["goal"] else None
            )
        if "deflection_type" in play["goal"]:
            updated_dict["deflection_type"] = (
            self.map_value_from_look_up(
           play["goal"]["deflection_type"], self.look_ups,
           db.DeflectionType
            )
            if play["goal"]["deflection_type"] is not None else None)
        else:
            updated_dict["deflection_type"] = None
        if "penalty_shot" in play["goal"]:
            updated_dict["penalty_shot"] = (
                play["goal"]["penalty_shot"] is not None
            )
        else:
            updated_dict["penalty_shot"] = False
        updated_dict["own_goal"] = "own_goal" in play["goal"]
        if "assists" in play:
            updated_dict["assists"] = self.get_updated_assits(
                play["assists"], updated_dict["team_id"], play["goal"]["team"])
    
        return updated_dict


    def get_updated_assits(self, assists: dict, team_id: int, 
                           team_abb: str) -> list:
        updated_assits = []
        rank = 1
        for assist in assists:
            updated_assist = self.get_updated_assist(
            assist, team_id, team_abb, rank)
            rank += 1
            updated_assits.append(updated_assist)
        
        return updated_assits
    

    def get_updated_assist(
            self, assist: dict, team_id: int, team_abb: str, 
            rank: int) -> dict:
        player_id = self.get_player_id(
            team_id,
            int(assist["player_number"]),
            team_abb,
        )
        if rank == 1:
            is_primary = True
        else:
            is_primary = False

        return {"player_id": player_id, "is_primary": is_primary}
    

class ShotUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            int(play["player_number"]),
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = self.map_value_from_look_up(
            play["shot_type"], self.look_ups,
            db.ShotType
            )
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        updated_dict["distance"] = (int(play["distance"])
                                    if "distance" in play else None)
        if play["deflection_type"] is not None:
            updated_dict["deflection_type"] = (
                self.map_value_from_look_up(
            play["deflection_type"], self.look_ups,
            db.DeflectionType
            )
            )
        else:
            updated_dict["deflection_type"] = None
        updated_dict["penalty_shot"] = play["penalty_shot"] is not None
        updated_dict["broken_stick"] = play["broken_stick"] is not None
        updated_dict["over_board"] = play["over_board"] is not None
    
        return updated_dict
    

class DelayedPenaltyUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["team_id"] = self.team_abb_to_db_id[play["team"]]

        return updated_dict
    

class HitUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        hitter_team_id = self.team_abb_to_db_id[play["team"]]
        hitted_team_id = self.team_abb_to_db_id[play["opponent_team"]]
        updated_dict["hitter_id"] = self.get_player_id(
            hitter_team_id,
            int(play["player_number"]),
            play["team"]
        )
        updated_dict["victim_id"] = self.get_player_id(
            hitted_team_id,
            int(play["opponent_player_number"]),
            play["opponent_team"]
        )
        updated_dict["hitter_team_id"] = hitter_team_id
        updated_dict["victim_team_id"] = hitted_team_id
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]

        return updated_dict
    

class GiveAwayUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        team_id = self.team_abb_to_db_id[play["team"]]
        updated_dict["player_id"] = self.get_player_id(
            team_id,
            int(play["player_number"]),
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
            int(play["player_number"]),
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
            int(play["player_number"]),
            play["team"]
        )
        updated_dict["team_id"] = team_id
        updated_dict["shot_type"] = self.map_value_from_look_up(
            play["shot_type"], self.look_ups,
            db.ShotType
            )
        if "shot_result" in play:
            updated_dict["shot_result"] = self.map_value_from_look_up(
            play["shot_result"], self.look_ups,
            db.ShotResult
            )
        else:
            updated_dict["shot_result"] = None
        updated_dict["zone"] = (ZONE_MAPPER[play["zone"].lower()]
                                    if "zone" in play else None)
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
        if "player_number" in play:
            updated_dict["offender_id"] = self.get_player_id(
                team_id,
                int(play["player_number"]),
                play["team"]
            )
        else:
             updated_dict["offender_id"] = None
        updated_dict["offender_team_id"] = team_id
        updated_dict["penalty_type"] = self.map_value_from_look_up(
            play["penalty_type"], self.look_ups,
            db.PenaltyType
            )
        updated_dict["penalty_type"] = play["penalty_type"].lower().strip()
        updated_dict["penalty_minutes"] = int(play["penalty_minutes"])
        updated_dict["zone"] = ZONE_MAPPER[play["zone"].lower()]
        if "penalty_modifier" in play:
            if play["penalty_modifier"] is not None:
                updated_dict["major_penalty"] = True
            else:
                updated_dict["major_penalty"] = False
        else:
            updated_dict["major_penalty"] = False
        if "drawn_team" in play:
            drawn_team_id = self.team_abb_to_db_id[play["drawn_team"]]
            updated_dict["victim_id"] = self.get_player_id(
                drawn_team_id,
                int(play["drawn_player_number"]),
                play["drawn_team"]
            )
            updated_dict["victim_team_id"] = drawn_team_id
        else:
            updated_dict["victim_team_id"] = None
            updated_dict["victim_id"] = None
        if "served_player_name" in play:
            updated_dict["served_player_id"] = self.get_player_id(
                team_id,
              int(play["served_player_number"]),
                play["team"]
            )
        else:
            updated_dict["served_player_id"] = None

    
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
        updated_dict["period_type"] = self.map_value_from_look_up(
            play["period_type"], self.look_ups,
            db.PeriodType
        )
        updated_dict["time"] = cf.convert_to_seconds(
            play["time"])
        updated_dict["timezone"] = play["timezone"]

        return updated_dict


class ChallengeUpdater(UpdatePBP):


    def update_play_info(self, play: dict) -> dict:
        updated_dict = {}
        updated_dict["reason"] = play["reason"].lower()
        updated_dict["result"] = play["result"].lower()
        if "team" in play:
            updated_dict["team_id"] = self.team_abb_to_db_id[play["team"]]
        else:
            updated_dict["team_id"] = None
        if "league_challenge" in play:
            updated_dict["league_challenge"] = (
                play["league_challenge"] is not None
            )
        else:
            updated_dict["league_challenge"] = False

        return updated_dict
    

class  UpdateGameData():


    UPDATE_CLASSES = {
        "BLOCK": BlockedShotUpdater,
        "CHL": ChallengeUpdater,
        "DELPEN": DelayedPenaltyUpdater,
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

    SKIP_PLAY = ["PGSTR", "PGEND", "ANTHEM", "GEND", "GOFF", "EGT", "EGPID"]


    def __init__(self, mappers: dict, season: str):
        self.mappers = mappers
        self.season = season
        self.nhl_elite_mapper_detail = mappers["elite_nhl_detail"][season]
        self.season_db_mapper = self.mappers["season_name_player_id"][self.season]
        self.normalized_season_db_mapper = self.mappers["normalized_season_name_player_id"][self.season]
        self.look_ups = mappers["look_ups"]
        self.match_player_mapper = {}
        self.team_type_to_abb = {}
        self.team_abb_to_db_id = {}


    @time_execution
    def update_game_data(self, game_data: dict) -> dict:
        updated_data = {}
        updated_data = self.get_general_info(updated_data, game_data)
        updated_data["shifts"] = self.update_shifts(game_data)
        self.match_players_to_db_id(updated_data)
        try:
            updated_data["PBP"] = self.update_PBP(game_data["PBP"])
        except:
            cf.log_and_raise(
                None, 
                UpdateGameDataError, 
                match_id=game_data["id"],
                team_home=game_data["HT"],
                team_away=game_data["VT"],
                date=game_data["date"]
                )
        logger.info(
            "Updating dict of game from date %s (%s) was successful",
            updated_data['date'],
            updated_data['match_id']
        )

        return updated_data
    

    def get_general_info(self, updated_data: dict, game_data: dict) -> dict:
        self.set_dictionaries(game_data)
        self.update_nhl_db_mapper()
        updated_data["HT"] = self.get_team_id(game_data["HT"])
        updated_data["VT"] = self.get_team_id(game_data["VT"])
        updated_data["TH"] = game_data["HT"]
        updated_data["TV"] = game_data["VT"]
        updated_data["attendance"] = game_data["attendance"]
        updated_data["match_id"] = int(game_data["id"])  
        updated_data["date"] = (
            datetime.strptime(game_data["date"], '%Y-%m-%d').date()
            )
        updated_data["stadium"] = game_data["stadium"]
        updated_data["start_time_UTC"] = game_data["start_time_UTC"]

        return updated_data
    
    
    def get_team_id(self, team_abb: str) -> int:
        team_uid = team_map.get_team_uid_from_abbrevation(team_abb)
        team_id = self.season_db_mapper[team_uid]["single"][0]["team_id"]

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
            if team_id not in self.nhl_elite_mapper_detail:
                self.nhl_elite_mapper_detail[team_id] = {}


    def update_shifts(self, game_data: dict) -> dict:
        shift_dict = {}
        us_o = UpdateShifts()
        shift_dict["TH"] = us_o.update_players_shifts(game_data["HTS"])
        shift_dict["TV"] = us_o.update_players_shifts(game_data["VTS"])
        logger.debug(
            "Updating shift dict of game from date %s (%s) was successful",
            game_data['date'],
            game_data['id']
        )

        return shift_dict
    

    def match_players_to_db_id(
            self, scraped_data: dict) -> None:
        for team_type in scraped_data["shifts"].keys():
            team_abb = self.team_type_to_abb[team_type]
            team_uid = team_map.get_team_uid_from_abbrevation(team_abb)
            team_id = self.team_abb_to_db_id[team_abb]
            self.match_team_players_to_db_id(
                scraped_data["shifts"][team_type], team_uid, team_id, team_abb)


    def match_team_players_to_db_id(
            self, team_shifts: dict, team_uid: int, 
            team_id: int, team_abb: str) -> None:
        self.match_player_mapper[team_id] = {}
        for player_info in team_shifts:
            self.match_player_to_db_id(
                player_info, team_uid, team_id, team_abb)
        logger.debug(
            "Matching players from NHL data to DB data for team %s (%s) was successful",
            team_abb,
            team_id
        )

    
    def match_player_to_db_id(
        self, player_info: tuple, team_uid: int, team_id: int, 
        team_abb: str) -> None:
        player_matched = self.try_find_match_with_nhl_db_mapper(
            player_info, team_id)
        if player_matched:
            return
        matcher_o = SingleMatchFinder(
            team_mapper=self.match_player_mapper[team_id],
            player_info=player_info, 
            db_mapper=self.season_db_mapper[team_uid]["single"],
            normalized_db_mapper=self.normalized_season_db_mapper[team_uid]["single"],
            nhl_elite_mapper=self.mappers["elite_nhl"],
            nhl_elite_mapper_detail=self.nhl_elite_mapper_detail[team_id],
            firstname_mapper=self.mappers["first_name"]
            )
        player_matched = matcher_o.iterrate_to_find_match_wrapper()
        if player_matched:
            return
        matcher_o = DuplicatesMatchFinder(
            team_mapper=self.match_player_mapper[team_id],
            player_info=player_info, 
            db_mapper=self.season_db_mapper[team_uid]["duplicates"],
            normalized_db_mapper=self.normalized_season_db_mapper[team_uid]["duplicates"],
            nhl_elite_mapper=self.mappers["elite_nhl"],
            nhl_elite_mapper_detail=self.nhl_elite_mapper_detail[team_id],
            firstname_mapper=self.mappers["first_name"]
            )
        player_matched = matcher_o.iterrate_to_find_match_wrapper()
        if player_matched:
            return
        self.input_match_manually(
            player_info=player_info, team_id=team_id, team_abb=team_abb,
            team_uid=team_uid
            )


    def try_find_match_with_nhl_db_mapper(
            self, player_info, team_id) -> bool:
        for nhl_name in self.nhl_elite_mapper_detail[team_id]:
            mapper_dict = self.nhl_elite_mapper_detail[team_id][nhl_name]
            if ((player_info[0] == nhl_name) 
            & (player_info[1] == mapper_dict["number"])):
                self.match_player_mapper[team_id][player_info] = (
                    mapper_dict["player_id"]
                )
                
                return True
            
        return False


    def update_PBP(self, pbp_data: dict) -> list:
        updated_pbp = []
        for play in pbp_data:
            if play["play_type"] in self.SKIP_PLAY:
                continue
            pbp_o = self.get_PBP_class(
                play["play_type"])
            updated_play = pbp_o.update_play(play)
            updated_pbp.append(updated_play)
        logger.debug("Updating PBP list was succesfull")

        return updated_pbp
    
                    
    def get_PBP_class(self, play_type: str):

        return self.UPDATE_CLASSES[play_type](
            self.match_player_mapper, self.team_type_to_abb, self.team_abb_to_db_id,
            self.look_ups
            )
    

    def input_match_manually(self, player_info: dict, team_id: int, 
                             team_abb: str, team_uid: str) -> None:
        logger.info(
            "No match was found for player %s from team %s (id: %s) in db or "
            "NHL elite mapper.", player_info, team_abb, team_id
            )
        player_id = input("Input player id: " )
        self.match_player_mapper[team_id][player_info] = player_id
        db_name = self.get_db_name_from_player_id(
            player_id=int(player_id), team_uid=team_uid, team_id=team_id, team_abb=team_abb
            )
        new_entry = {
                "db_name": db_name, 
                "number": player_info[1], 
                "player_id": player_id
        }
        self.nhl_elite_mapper_detail[team_id][player_info[0]] = new_entry 


    def get_db_name_from_player_id(
            self, player_id: int, team_uid: int, team_id: str, 
            team_abb: str) -> str:
        for type_ in self.season_db_mapper[team_uid]:
            for player_dict in self.season_db_mapper[team_uid][type_]:
                if player_dict["player_id"] == player_id:
                    return player_dict["player_name"]
        cf.log_and_raise(
            None, MissingPlayer, player_id=player_id, team_id=team_id, team_abb=team_abb
            )
    

class MatchFinder():


    def __init__(
            self, team_mapper: dict, player_info: tuple, db_mapper: dict, 
            normalized_db_mapper: dict, nhl_elite_mapper_detail: dict, nhl_elite_mapper: dict, firstname_mapper: dict):
        self.team_mapper = team_mapper
        self.player_info = player_info
        self.db_mapper = db_mapper
        self.normalized_db_mapper = normalized_db_mapper
        self.nhl_elite_mapper_detail = nhl_elite_mapper_detail
        self.nhl_elite_mapper = nhl_elite_mapper
        self.firstname_mapper = firstname_mapper
        self.matched_db_name = None


    def iterrate_to_find_match_wrapper(self) -> bool:
        name_matched = self.iterrate_to_find_match(
            nhl_name=self.player_info[0], db_mapper=self.db_mapper,
            add_to_mapper=False
        )
        if name_matched:

            return True
        name_matched = self.iterrate_to_find_match(
            nhl_name=self.player_info[0], db_mapper=self.normalized_db_mapper,
            add_to_mapper=True
        )
        if name_matched:

            return True
        name_matched = self.iterrate_to_find_mapped_match()

        if name_matched:

            return True
        name_matched = self.iterrate_to_find_alternative_form_match()

        
        return name_matched


    def iterrate_to_find_match(
            self, nhl_name: str, db_mapper: dict, add_to_mapper: bool) -> bool:
        index = -1
        for player_dict in db_mapper:
            index += 1
            name_matched = self.try_to_find_match(
                db_name=player_dict["player_name"],
                nhl_name=nhl_name,
                player_id=player_dict["player_id"]
                )
            if name_matched:
                self.matched_db_name = self.db_mapper[index]["player_name"]
                if add_to_mapper:
                    self.add_to_detail_mapper()

                return True
            
        return False
    

    def iterrate_to_find_mapped_match(self) -> bool:
        mapped_match = self.try_to_map_scraped_to_db_name()
        if not mapped_match:
            return False
        name_matched = self.iterrate_to_find_match(
            nhl_name=mapped_match, db_mapper=self.db_mapper, add_to_mapper=True
            )
        if name_matched:
            logger.info(
                "Match for player %s was found with NHL to Elite mapper "
                "(db_name: %s, player_id: %s, player_number: %s)", 
                self.player_info[0], self.matched_db_name, 
                self.team_mapper[self.player_info], 
                self.player_info[1]
                )
        
        return name_matched
    

    def try_to_map_scraped_to_db_name(self) -> str|None:
        for name in self.nhl_elite_mapper:
            if name == self.player_info[0]:
                return self.nhl_elite_mapper[name]
        
        return 
    

    def iterrate_to_find_alternative_form_match(self) -> bool:
        normalized_player_name = self.normalize_name(
            self.player_info[0])
        
        scraped_first_name = normalized_player_name.split()[:-1]
        scraped_first_name = " ".join(scraped_first_name)
        for name_set in self.firstname_mapper:
            if scraped_first_name in name_set:
                updated_firstname = next(iter(name_set - {scraped_first_name}))
                update_name = (
                    updated_firstname 
                    + " " 
                    + normalized_player_name.split()[-1]
                )
                name_matched = self.iterrate_to_find_match(
                    nhl_name=update_name, db_mapper=self.normalized_db_mapper,
                    add_to_mapper=True
                    )
                if name_matched:
                    logger.info("Match for scraped name was found with first "
                                "name mapper. Name %s (#%s) was mapped to name"
                                " %s (%s)",
                                self.player_info[0], 
                                self.player_info[1], 
                                self.matched_db_name, 
                                self.team_mapper[self.player_info]
                                )
                    
                    return True
        
        return False
    

    def add_to_detail_mapper(self) -> None:
        new_entry = {
                "db_name": self.matched_db_name, 
                "number": self.player_info[1], 
                "player_id": self.team_mapper[self.player_info]
        }
        self.nhl_elite_mapper_detail[self.player_info[0]] = new_entry


    def try_to_find_match(
            self, db_name: str, nhl_name: str, player_id: int) -> bool:
        pass


    def normalize_name(self, name: str) -> str:
        normalized = unicodedata.normalize("NFD", name)
        ascii_name = "".join(c for c in normalized if not unicodedata.combining(c))

        return ascii_name
    

class SingleMatchFinder(MatchFinder):

 
    def try_to_find_match(
            self, db_name: str, nhl_name: str, player_id: int) -> bool:
        if db_name.lower() == nhl_name.lower():
            self.team_mapper[self.player_info] = player_id

            return True
        
        return False


class DuplicatesMatchFinder(MatchFinder):


    def try_to_find_match(
            self, db_name: str, nhl_name: str, player_id: int) -> bool:
        if db_name.lower() == nhl_name.lower():
            self.team_mapper[self.player_info] = input(
                "Name of the player is duplicated for "
                "given team season combination. Set player_id "
                "manually: ")
            return True
        
        return False

        










    



















        



