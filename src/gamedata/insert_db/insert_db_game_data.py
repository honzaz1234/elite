import database_creator.database_creator as db
import database_insert.db_insert as db_insert

from constants import *
from logger.logging_config import logger
from sqlalchemy.orm import Session


class PBPDB():


     def __init__(self, db_session: Session):
        self.db_session = db_session
        self.db_method = db_insert.DatabaseMethods(self.db_session)


     def _input_play_wrapper(self, play: dict, match_id: int) -> None:

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
          self._input_play(play["play_info"], play_id)



     def _input_play_info(self, play: dict, play_id: int) -> int:
          pass


class BlockedShotDB(PBPDB):


    def _input_play_info(self, play: dict, play_id: int) -> int:
         blocker_type_id = self.db_method._input_unique_data(
              table=db.BlockerType, blocker_type=play["blocked_by"]
         )
         shot_type_id = self.db_method._input_unique_data(
              table=db.ShotType, blocker_type=play["shot_type"]
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
               db.ChallengeResult, result=play["result"]
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
               winner_id=play["winner_id"],
               loser_id=play["loser_id"],
               winner_team_id=play["winner_team_id"],
               loser_team_id=play["loser_team_id"],
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
          shot_type_id = self.db_method._input_unique_data(
               db.ShotType,
               shot_type=play["shot_type"],
          )
          deflection_type_id = self.db_method._input_unique_data(
               db.DeflectionType,
               deflection=play["deflection_type"],
          )
          goal_id = self.db_method._input_unique_data(
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

          for assist in play["assists"]:
               self.db_method._input_unique_data(
                    db.AssistPlay,
                    goal_id=goal_id,
                    player_id=assist["player_id"],
                    is_primary=assist["is_primary"]
               )

          return goal_id
     

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
         shot_result_id = self.db_method._input_unique_data(
              table=db.ShotResult, shot_result=play["shot_result"]
         )
         shot_type_id = self.db_method._input_unique_data(
              table=db.ShotType, blocker_type=play["shot_type"]
         )
         zone_id = self.db_method._input_unique_data(
              table=db.Zone, zone=play["zone"]
         )
         
         play_id = self.db_method._input_unique_data(
              table=db.BlockedShotPlay,
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
              table=db.TimeZone, shotime_Zonet_result=play["timezone"]
         )
          period_type_id = self.db_method._input_unique_data(
              table=db.PeriodType, blocker_type=play["period_type"]
         )    
          play_id = self.db_method._input_unique_data(
              table=db.PeriodType,
                   play_id=play_id,
                   time=play["time"],
                   time_zone_id=time_zone_id,
                   period_type_id=period_type_id
         )
          
          return play_id
     

class PenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> int:
          penalty_type_id = self.db_method._input_unique_data(
              table=db.PenaltyType, shotime_Zonet_result=play["penalty_type"]
         )
          zone_id = self.db_method._input_unique_data(
              table=db.Zone, blocker_type=play["zone"]
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
              table=db.Zone, shotime_Zonet_result=play["zone"]
         )
          shot_type_id = self.db_method._input_unique_data(
              table=db.ShotType, deflection_type=play["shot_type_id"]
         ) 
          deflection_id = self.db_method._input_unique_data(
              table=db.DeflectionType, deflection_type=play["deflection_type"]
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
                   deflection_id=deflection_id
         )
          
          return play_id
     
     
class TakeAwayDB(PBPDB):


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
     

class DelayedPenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id) -> int:
          play_id = self.db_method._input_unique_data(
               db.DelayedPenaltyPlay,
               play_id=play_id,
               team_id=play["team_id"],
          )

          return play_id
     

class GameStopageDB(PBPDB):


     def _input_play_info(self, play: dict, play_id) -> int:
          stopage_type_id = self.db_method._input_unique_data(
               db.GameStopageType,
               stopage_type_id=play["stopage_type"]
          )
          play_id = self.db_method._input_unique_data(
               db.GameStopageType,
               play_id=play_id,
               stopage_type_id=stopage_type_id
          )

          return play_id


class GameDataDB():
    """class containing methods used for inserting data in DB"""


    INPUT_CLASSES = {
     "BLOCK": BlockedShotDB,
     "CHL": ChallengeDB,
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
     "TAKE": TakeAwayDB
     }  


    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.db_method = db_insert.DatabaseMethods(self.db_session)
        self.query = db_insert.Query(db_session=self.db_session)    


    def _input_nhl_elite_player_mapper(self, dict_: dict) -> int:
            season_id = self.db_method._input_unique_data(
                    table=db.Season, season=dict_[SEASON_NAME])
            mapper_id = self.db_method._input_unique_data(
                table=db.NHLEliteNameMapper,
                nhl_name=dict_["nhl_name"],
                elite_name=dict_["db_name"],
                player_number = dict_["number"],
                team_id = dict_["team_id"],
                season_id = season_id,
                player_id=dict_["player_id"]
                )
            
            return mapper_id
    

    def _input_general_info(self, dict_: dict) -> int:
         match_id = self.db_method._input_unique_data(
              table=db.Match,
              stadium_id = dict_["stadium_id"],
              date=dict_["date"],
              time=dict_["time"],
              attendance=dict_["attendance"],
              home_team_id=dict_["HT"],
              away_team_id=dict_["VT"])
         
         return match_id
    

    def _get_stadium_id(self, stadium: str) -> int|None:
         stadium_id = self.query._find_id_in_table(db.Stadium, stadium=stadium)

         return stadium_id
    
    
    def _get_stadium_name(self, stadium_id) -> str|None:
         stadium_name = self.query._get_value_from_table(
            [db.Stadium.stadium], id=stadium_id)
         
         return stadium_name
    

    def _input_shift(
              self, shift: dict, player_id: int, team_id: int, 
              play_id: int) -> int|None:
         
         shift_id = self.db_method._input_unique_data(
              table=db.PlayerShift,
              play_id=play_id,
              player_id=player_id,
              team_id=team_id,
              period=shift["period"],
              shift_start=shift["shift_start"],
              shift_end=shift["shift_end"]
         )

         return shift_id
    

    def _input_play(self, play: dict, match_id: int) -> None:

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
          input_po._input_play_info(play["play_info"], play_id)


    def _play_factory(self, play_type: str):
          
          return INPUT_CLASSES[play_type](self.db_session)
          
          
     






     



     










