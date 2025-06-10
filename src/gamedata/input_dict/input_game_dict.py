import database_creator.database_creator as db
import database_insert.db_insert as db_insert
import gamedata.insert_db.insert_db_game_data as insert_db
import mappers.db_mappers as db_mapper

from common_functions import dict_diff_unique, log_and_raise
from errors import InputPlayDBError
from decorators import time_execution
import mappers.db_mappers as db_mapper
from logger.logging_config import logger
from sqlalchemy.orm import Session

from constants import * 


class InputEliteNHLmapper():


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.mappers_o = db_mapper.GetDBID(self.db_session)
        self.input_o = insert_db.GameDataDB(
            self.db_session)


    @time_execution
    def input_all_mappers(
            self, elite_nhl_mapper: dict, stadium_mapper: dict) -> None:
        self._input_elite_nhl_mapper_dict(elite_nhl_mapper)
        self._input_stadium_mapper(stadium_mapper)
        self.db_session.commit()


    def _input_elite_nhl_mapper_dict(self, elite_nhl_mapper: dict) -> None:
        """wrapper method for inputting  all scraped data from dict to DB"""
        db_nhl_elite_mapper = self.mappers_o.get_elite_nhl_mapper()
        elite_nhl_mapper = dict_diff_unique(
            elite_nhl_mapper, db_nhl_elite_mapper)
        for season in elite_nhl_mapper:
            self._input_nhl_elite_season_dict(elite_nhl_mapper[season], season)
        logger.info("Elite NHL mapper succesfully inputted into db")


    def _input_nhl_elite_season_dict(
            self, season_mapper: dict, season: str) -> None:
        for team_id in season_mapper:
            self._input_nhl_elite_team_mapper(
                season_mapper[team_id], season, team_id)


    def _input_nhl_elite_team_mapper(
            self, team_mapper: dict, season: str, team_id: int) -> None:
        for nhl_name in team_mapper:
            self._input_nhl_elite_player_mapper(
                team_mapper[nhl_name], season, team_id, nhl_name)


    def _input_nhl_elite_player_mapper(
            self, player_mapper: dict, season: str, team_id: int,
              nhl_name: str) -> None:
        input_dict = player_mapper
        input_dict[SEASON_NAME] = season
        input_dict["team_id"] = team_id
        input_dict["nhl_name"] = nhl_name
        self.input_o._input_nhl_elite_player_mapper(input_dict)


    def _input_stadium_mapper(self, stadium_mapper):
        db_stadium_mapper = self.mappers_o.get_nhl_elite_stadium_mapper()
        stadium_mapper = dict_diff_unique(
            stadium_mapper, db_stadium_mapper)
        for stadium in stadium_mapper:
            self._input_mapped_stadium_into_db(
                stadium, stadium_mapper[stadium])
        logger.info("Stadium mapper succesfully inputted into db")


    def _input_mapped_stadium_into_db(
            self, nhl_name: str, elite_name: str) -> None:
        self.input_o._input_stadium_mapper(nhl_name, elite_name)


class InputGameInfo():


    def __init__(
            self,  db_session: Session, player_mapper: dict, 
            stadium_mapper: dict):
        self.db_session = db_session
        self.input_o = insert_db.GameDataDB(
            self.db_session)
        self.mappers_o = db_mapper.GetDBID(self.db_session)
        self.input_gi = InputGeneralInfo(
            self.db_session, stadium_mapper)
        self.input_shifts = InputShifts(
            self.db_session, player_mapper)
        self.input_PBP = InputPBP(
            self.db_session, player_mapper)

    @time_execution
    def input_game_dict(self, game: dict) -> None:

        match_id = self.input_gi._input_general_info(game)
        self.input_shifts._input_shifts(
            game["shifts"], game["HT"], game["VT"], match_id)
        self.input_PBP._input_PBP(game["PBP"], match_id)
        self.db_session.commit()


class InputGeneralInfo():


    def __init__(self, db_session: Session, 
                 stadium_mapper: dict):
        self.db_session = db_session
        self.db_method =  db_insert.DatabaseMethods(self.db_session)
        self.db_query = db_insert.Query(self.db_session)
        self.stadium_mapper = stadium_mapper


    @time_execution
    def _input_general_info(self, game):
        stadium_id = self._get_stadium_id(game["stadium"])
        input_dict = self._get_general_info_input_dict(game, stadium_id)
        match_id = self.db_method._input_unique_data(
              table=db.Match,
              match_id=input_dict["match_id"],
              stadium_id = input_dict["stadium_id"],
              date=input_dict["date"],
              time=input_dict["time"],
              attendance=input_dict["attendance"],
              home_team_id=input_dict["HT"],
              away_team_id=input_dict["VT"])

        return match_id
    

    def _get_stadium_id(self, stadium: str) -> int:
        if stadium in self.stadium_mapper:
            stadium = self.stadium_mapper[stadium]
        stadium_id = self.db_query._find_id_in_table(
            db.Stadium, stadium=stadium)
        if stadium_id is None:
            stadium_id = input(f"Stadium under name {stadium} does not exist "
                               "in the DB. Input stadium ID manually: ")
            row_data = self.db_query._get_value_from_table(
                [db.Stadium.stadium], id=stadium_id)
            stadium_elite = row_data.stadium
            if stadium_elite is None:
                raise 
            self.stadium_mapper[stadium] = stadium_elite
            logger.info(
                "Stadium %s was added to the stadium mapper with value %s", stadium, stadium_elite
                )

        return stadium_id
    

    def _get_general_info_input_dict(self, game: dict, stadium_id: int):
        input_dict = {}
        input_dict["stadium_id"] = stadium_id
        input_dict["match_id"] = game["match_id"]
        input_dict["HT"] = game["HT"]
        input_dict["VT"] = game["VT"]
        input_dict["date"] = game["date"]
        input_dict["time"] = game["start_time_UTC"]
        input_dict["attendance"] = game["attendance"]

        return input_dict

    
class InputShifts():


    def __init__(self, db_session: Session, player_mapper: dict):
        self.db_session = db_session
        self.player_mapper = player_mapper
        self.input_shift_dict = {}


    @time_execution
    def _input_shifts(
            self, shifts: dict, HT_id: int, VT_id: int, match_id :int) -> None:
        ids = {"TH": HT_id, "TV": VT_id}
        for team_type in ids:
            self._input_team_shifts(
                shifts[team_type], ids[team_type], match_id)
        self.db_session.bulk_insert_mappings(self.input_shift_dict)


    def _input_team_shifts(
            self, shifts: list, team_id: int, match_id: int) -> None:
        for player_info in shifts:
            self._input_player_shifts(
                player_info, shifts[player_info], team_id, match_id)
            

    def _input_player_shifts(
            self, player_info: tuple, shifts: list, team_id: int, 
            match_id: int) -> None:
        player_id = self.player_mapper[team_id][player_info]
        for shift in shifts:
            shift_dict = self._get_shift_dict(
                match_id, player_id, team_id, shift)
            self.input_shift_dict.append(shift_dict)


    def _get_shift_dict(
            match_id: int, player_id: int, team_id: int, shift: dict) -> dict:
        return {
              "match_id": match_id,
              "player_id": player_id,
              "team_id": team_id,
              "period": shift["period"],
              "shift_start": shift["shift_start"],
              "shift_end": shift["shift_end"]
        }
    

class PBPDB():


     def __init__(self, db_session: Session):
        self.db_session = db_session
        self.db_method = db_insert.DatabaseMethods(self.db_session)


     def _input_broken_play_info(self, play_id: int, play_desc: str) -> None:
         self.db_method._input_unique_data(db.BrokenPBP,
                                           play_id=play_id,
                                            play_desc=play_desc)
          

     def _input_play_info(self, play: dict, play_id: int) -> int:
          pass
     

     def _input_poi(
               self, play_id: int, player_id: int, team_id: int) -> int:
          shift_id = self.db_method._input_unique_data(db.PlayerOnIce,
                                                       play_id=play_id,
                                                       player_id=player_id,
                                                       team_id=team_id)
          
          return shift_id
     

     def _input_broken_poi(
               self, play_id: int, team_id: int, poi: str, 
               error_type: str) -> int:
          shift_id = self.db_method._input_unique_data(db.BrokenPOI,
                                                       play_id=play_id,
                                                       team_id=team_id,
                                                       poi=poi,
                                                       error_type=error_type)
          
          return shift_id
          
                                                            
class BlockedShotDB(PBPDB):


    def _input_play_info(self, play: dict, play_id: int) -> int:
         blocker_type_id = self.db_method._input_unique_data(
              table=db.BlockerType, blocker_type=play["blocked_by"]
         )
         shot_type_id = self.db_method._input_unique_data(
              table=db.ShotType, shot_type=play["shot_type"]
         )
         zone_id = self.db_method._input_unique_data(
              table=db.Zone, zone=play["zone"]
         )
         
         play_id = self.db_method._input_unique_data(
              table=db.BlockedShotPlay,
                   play_id=play_id,
                   shooter_id=play["shooter_id"],
                   shooter_team_id=play["shooter_team_id"],
                   blocker_type_id=blocker_type_id,
                   blocker_id=play["blocker_id"],
                   blocker_team_id=play["blocker_team_id"],
                   zone_id=zone_id,
                   shot_type_id=shot_type_id,
                   broken_stick=play["broken_stick"],
                   over_board=play["over_board"]
         )

         return play_id
    

class ChallengeDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:

          reason_id = self.db_method._input_unique_data(
               db.ChallengeReason, challenge_reason=play["reason"]
          )
          result_id = self.db_method._input_unique_data(
               db.ChallengeResult, challenge_result=play["result"]
          )
          play_id = self.db_method._input_unique_data(
               table=db.ChallengePlay,
                    play_id=play_id,
                    team_id=play["team_id"],
                    reason_id=reason_id,
                    result_id=result_id,
                    league_challenge=play["league_challenge"]
          )

          return play_id


class FaceOffDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          zone_id = self.db_method._input_unique_data(
               db.Zone,
               zone=play["zone"],
          )
          play_id = self.db_method._input_unique_data(
               db.FaceoffPlay,
               play_id=play_id,
               winner_id=play["faceoff_winner_id"],
               loser_id=play["faceoff_loser_id"],
               winner_team_id=play["winner_team_id"],
               loser_team_id=play["losing_team_id"],
               zone_id=zone_id
          )


class GiveAwayDB(PBPDB):


     def _input_play_info(self, play: dict, play_id) -> int:
          zone_id = self.db_method._input_unique_data(
               db.Zone,
               zone=play["zone"],
          )
          play_id = self.db_method._input_unique_data(
               db.GiveawayPlay,
               play_id=play_id,
               player_id=play["player_id"],
               team_id=play["team_id"],
               zone_id=zone_id
          )

          return play_id
     

class GoalDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          zone_id = self.db_method._input_unique_data(
               db.Zone,
               zone=play["zone"],
          )
          shot_type_id = self.db_method.get_compulsory_table_id(
               db.ShotType,
               play["shot_type"],
               shot_type=play["shot_type"],
          )
          deflection_type_id = self.db_method.get_compulsory_table_id(
               db.DeflectionType, 
               play["deflection_type"], 
               deflection=play["deflection_type"])
          play_id = self.db_method._input_unique_data(
               db.GoalPlay,
               play_id=play_id,
               distance=play["distance"],
               penalty_shot=play["penalty_shot"],
               own_goal=play["own_goal"],
               team_id=play["team_id"],
               player_id=play["player_id"],
               shot_type_id=shot_type_id,
               deflection_type_id=deflection_type_id,
               zone_id=zone_id
          )

          if "assists" not in play:
               return play_id
          
          for assist in play["assists"]:
               self.db_method._input_unique_data(
                    db.AssistPlay,
                    goal_id=play_id,
                    player_id=assist["player_id"],
                    is_primary=assist["is_primary"]
               )

          return play_id
     

class HitDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          zone_id = self.db_method._input_unique_data(
               db.Zone,
               zone=play["zone"],
          )
          play_id = self.db_method._input_unique_data(
               db.HitPlay,
               play_id=play_id,
               hitter_id=play["hitter_id"],
               hitter_team_id=play["hitter_team_id"],
               victim_id=play["victim_id"],
               victim_team_id=play["victim_team_id"],
               zone_id=zone_id
          )

          return play_id
     

class MissedShotDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
         shot_result_id = self.db_method.get_compulsory_table_id(
              db.ShotResult,
              play["shot_result"],
              shot_result=play["shot_result"]
         )
         zone_id = self.db_method.get_compulsory_table_id(
              db.Zone,
              play["zone"],
              zone=play["zone"]
         )
         shot_type_id = self.db_method.get_compulsory_table_id(
              db.ShotType,
              play["shot_type"],
              shot_type=play["shot_type"]
         )
         play_id = self.db_method._input_unique_data(
              table=db.MissedShotPlay,
                   play_id=play_id,
                   player_id=play["player_id"],
                   team_id=play["team_id"],
                   zone_id=zone_id,
                   shot_type_id=shot_type_id,
                   shot_result_id=shot_result_id,
                   distance=play["distance"],
                   broken_stick=play["broken_stick"],
                   over_board=play["over_board"],
         )

         return play_id
     

class PeriodDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          time_zone_id = self.db_method._input_unique_data(
              table=db.TimeZone, time_zone=play["timezone"]
         )
          period_type_id = self.db_method._input_unique_data(
              table=db.PeriodType, period_type=play["period_type"]
         )    
          play_id = self.db_method._input_unique_data(
              table=db.PeriodPlay,
                   play_id=play_id,
                   time=play["time"],
                   time_zone_id=time_zone_id,
                   period_type_id=period_type_id
         )
          
          return play_id
     

class PenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          penalty_type_id = self.db_method._input_unique_data(
              table=db.PenaltyType, penalty_type=play["penalty_type"]
         )
          zone_id = self.db_method._input_unique_data(
              table=db.Zone, zone=play["zone"]
         )    
          play_id = self.db_method._input_unique_data(
               table=db.PenaltyPlay,
                    play_id=play_id,
                    offender_id=play["offender_id"],
                    offender_team_id=play["offender_team_id"],
                    served_by_id=play["served_player_id"],
                    victim_id=play["victim_id"],
                    victim_team_id=play["victim_team_id"],
                    zone_id=zone_id,
                    penalty_type_id=penalty_type_id,
                    penalty_minutes=play["penalty_minutes"],
                    major_penalty=play["major_penalty"]
                    )
          

class ShotDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          zone_id = self.db_method._input_unique_data(
              table=db.Zone, zone=play["zone"]
         )
          shot_type_id = self.db_method._input_unique_data(
              table=db.ShotType, shot_type=play["shot_type"]
         )
          deflection_type_id = self.db_method.get_compulsory_table_id(
               db.DeflectionType,
               play["deflection_type"],
               deflection_type=play["deflection_type"]
          )
          play_id = self.db_method._input_unique_data(
              table=db.ShotPlay,
                   play_id=play_id,
                   player_id=play["player_id"],
                   team_id=play["team_id"],
                   zone_id=zone_id,
                   shot_type_id=shot_type_id,
                   distance=play["distance"],
                   penalty_shot=play["penalty_shot"],
                   broken_stick=play["broken_stick"],
                   over_board=play["over_board"],
                   deflection_type_id=deflection_type_id
         )
          
          return play_id
     
     
class TakeAwayDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          zone_id = self.db_method._input_unique_data(
               db.Zone,
               zone=play["zone"],
          )
          play_id = self.db_method._input_unique_data(
               db.GiveawayPlay,
               play_id=play_id,
               player_id=play["player_id"],
               team_id=play["team_id"],
               zone_id=zone_id
          )

          return play_id
     

class DelayedPenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          play_id = self.db_method._input_unique_data(
               db.DelayedPenaltyPlay,
               play_id=play_id,
               team_id=play["team_id"],
          )

          return play_id
     

class GameStopageDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          stopage_type_id = self.db_method._input_unique_data(
               db.GameStopageType,
               stopage_type=play["stopage_type"]
          )
          play_id = self.db_method._input_unique_data(
               db.GameStopagePlay,
               play_id=play_id,
               stopage_type_id=stopage_type_id
          )

          return play_id
     

class InputPBP():


    INPUT_CLASSES = {
            "BLOCK": BlockedShotDB,
            "CHL": ChallengeDB,
            "DELPEN": DelayedPenaltyDB,
            "FAC": FaceOffDB,
            "GIVE": GiveAwayDB,
            "GOAL": GoalDB,
            "HIT": HitDB,
            "MISS": MissedShotDB,
            "PEND": PeriodDB,
            "PENL": PenaltyDB,
            "PSTR": PeriodDB,
            "SOC": PeriodDB,
            "SHOT": ShotDB,
            "STOP": GameStopageDB,
            "TAKE": TakeAwayDB,
        }  


    def __init__(
            self, db_session: Session, player_mapper: dict):
        self.db_session = db_session
        self.db_method =  db_insert.DatabaseMethods(self.db_session)
        self.input_pbp = PBPDB(db_session)
        self.input_poi_dict = {}
        self.player_mapper = player_mapper


    @time_execution
    def _input_PBP(self, plays: list, match_id) -> None:
        for play in plays:
            play_id = self._input_play(play, match_id)
            try:
                self._input_poi(play_id, play["poi"])
            except Exception as e:
                print(e)
                print(play)
                raise e
        self.db_session.bulk_insert_mappings(self.input_poi_dict)
            

    def _input_play(self, play: dict, match_id: int) -> int:

          play_type_id = self.db_method._input_unique_data(
              table=db.PlayType, play_type=play["play_type"]
         )

          play_id = self.db_method._input_unique_data(
               db.Play,
               play_type_id=play_type_id,
               match_id=match_id,
               period=play["period"],
               time=play["time"]
          )
          input_po = self._play_factory(play["play_type"])
          if "error" in play:
               input_po._input_broken_play_info(
                    play_id, play["play_desc"])
               
               return play_id
          try:
               input_po._input_play_info(play["play_info"], play_id)
          except Exception as e:
               log_and_raise(
                    None, InputPlayDBError, original_message=e, 
                    play_type=play["play_type"],
                    play=play)
               
          return play_id


    def _play_factory(self, play_type: str):
          
          return self.INPUT_CLASSES[play_type](self.db_session)


    def _input_poi(self, play_id: int, shifts: dict) -> None:
        if "poi" in shifts.get("error", {}):
            for team_id, error_data in shifts["error"].items():
                poi = error_data.get("poi")
                error_type = error_data.get("error_type")
                self.input_pbp._input_broken_poi(
                    play_id, team_id, poi, error_type)
            for team_id in shifts:
                if team_id == "error":
                    continue
                self._input_team_poi(play_id, shifts[team_id], team_id)


    def _input_team_poi(
            self, play_id: int, team_shifts: list, team_id: int) -> None:
        for player_id in team_shifts:
            poi_dict = self._get_poi_dict(play_id, player_id, team_id)
            self._input_team_poi.append(poi_dict)


    def get_poi_dict(play_id: int, player_id: int, team_id: int) -> dict:

        return {
            "play_id": play_id,
            "player_id": player_id,
            "team_id": team_id
            }
          
























    