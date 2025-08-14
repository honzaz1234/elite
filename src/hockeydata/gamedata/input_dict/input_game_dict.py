import database_creator.database_creator as db
import database_insert.db_insert as db_insert
import mappers.db_mappers as db_mapper

from common_functions import dict_diff_unique, log_and_raise
from errors import InputPlayDBError, NoneReferenceValueError
from database_creator.database_config import TABLE_CONFIG
from decorators import time_execution
from logger.logging_config import logger
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

from constants import * 


class InputEliteNHLmapper():
    

    def __init__(self, db_session: Session):
        self.db_method =  db_insert.DatabaseMethods(db_session)
        self.db_session = db_session
        self.mappers_o = db_mapper.GetDBID(db_session)
        self.update_on_conflict = False
        self.input_player_mapper_list = []
        self.input_stadium_mapper_list = []


    @time_execution
    def input_all_mappers(
            self, mappers: dict) -> None:
        logger.info("Inputing mappers into DB...")
        self._input_nhl_elite_mapper_dict(
            nhl_elite_mapper=mappers["elite_nhl_detail"], 
            season_mapper=mappers["look_ups"][db.Season]
            )
        self._input_stadium_mapper(stadium_mapper=mappers["stadium"])
        self._input_look_ups(look_ups=mappers["look_ups"])
        self.db_session.commit()
        logger.info("All mappers were inputed into DB.")


    def _input_nhl_elite_mapper_dict(
            self, nhl_elite_mapper: dict, season_mapper: dict) -> None:
        """wrapper method for inputting  all scraped data from dict to DB"""
        db_nhl_elite_mapper = self.mappers_o.get_nhl_elite_mapper()
        nhl_elite_mapper = dict_diff_unique(
            nhl_elite_mapper, db_nhl_elite_mapper)
        for season in nhl_elite_mapper:
            self._input_nhl_elite_season_dict(
                nhl_elite_mapper[season], season, season_mapper
                )
        self.db_method.insert_update_or_ignore_on_conflict_bulk(
            db.NHLEliteNameMapper, self.input_player_mapper_list,
            self.update_on_conflict,
            TABLE_CONFIG["mappers"][db.NHLEliteNameMapper]["index_update"]
            )
        logger.info("Elite NHL mapper succesfully inputted into db")


    def _input_nhl_elite_season_dict(
            self, season_player_mapper: dict, season: str, 
            season_mapper: dict) -> None:
        for team_id in season_player_mapper:
            self._input_nhl_elite_team_mapper(
                season_player_mapper[team_id], season, team_id, season_mapper
                )


    def _input_nhl_elite_team_mapper(
            self, team_mapper: dict, season: str, team_id: int, 
            season_mapper: dict) -> None:
        
        for nhl_name in team_mapper:
            self._input_nhl_elite_player_mapper(
                team_mapper[nhl_name], season, team_id, nhl_name, season_mapper
                )
            

    def _input_nhl_elite_player_mapper(
            self, player_mapper: dict, season: str, team_id: int,
              nhl_name: str, season_mapper: dict) -> None:
        input_dict = player_mapper
        input_dict["season_id"] = season_mapper[season]
        input_dict["team_id"] = team_id
        input_dict["nhl_name"] = nhl_name
        dict_ = {
            "player_id": input_dict["player_id"],
            "nhl_name": input_dict["nhl_name"], 
            "elite_name": input_dict["db_name"],
            "team_id": input_dict["team_id"], 
            "season_id": input_dict["season_id"],
            "player_number": input_dict["number"]
            }
        self.input_player_mapper_list.append(dict_)


    def _input_stadium_mapper(self, stadium_mapper):
        db_stadium_mapper = self.mappers_o.get_nhl_elite_stadium_mapper()
        stadium_mapper = dict_diff_unique(
            stadium_mapper, db_stadium_mapper)
        for stadium in stadium_mapper:
            self._input_mapped_stadium_into_db(
                stadium, stadium_mapper[stadium])
        logger.info("Stadium mapper succesfully inputted into db")
        self.db_method.insert_update_or_ignore_on_conflict_bulk(
            db.StadiumMapper, self.input_stadium_mapper_list,
            self.update_on_conflict,
            TABLE_CONFIG["mappers"][db.StadiumMapper]["index_update"]
        )


    def _input_mapped_stadium_into_db(
            self, nhl_name: str, elite_name: str) -> None:
        dict_ = {
            "nhl_name": nhl_name, 
            "elite_name": elite_name
                }
        self.input_stadium_mapper_list.append(dict_)
        

    def _input_look_ups(self, look_ups: dict) -> dict:
        for table in look_ups:
            self._input_table_mapper(
                TABLE_CONFIG["reference"][table]["index_update"][0],
                look_ups[table],
                table
                )         


    def _input_table_mapper(
            self, col_name: str, table_mapper: dict, table: Table) -> None:
         inserts = self.create_table_dict(col_name, table_mapper)
         if inserts == []:
             return
         self.db_method.insert_update_or_ignore_on_conflict_bulk(
                table, inserts, self.update_on_conflict, 
                TABLE_CONFIG["reference"][table]["index_update"]
                )


    def create_table_dict(self, col_name: str, table_mapper: dict) -> list:
        inserts = []
        for val in table_mapper:
            insert_dict = self.create_value_dict(
                table_mapper[val], col_name, val
                )
            inserts.append(insert_dict)

        return inserts
    
    
    def create_value_dict(
            self, id: int, col_name: str, value: int|str) -> dict:
        return {
            "id": id, 
            col_name: value
        }
        
        
class InputGameInfo():


    def __init__(
            self,  db_session: Session, match_player_mapper: dict, 
            mappers: dict, update_on_conflict: bool
            ):
        self.db_session = db_session
        self.mappers_o = db_mapper.GetDBID(session=self.db_session)
        self.input_gi = InputGeneralInfo(
            db_session=self.db_session, 
            stadium_mapper=mappers["stadium"], update_on_conflict=update_on_conflict
            )
        self.input_shifts = InputShifts(
            db_session=self.db_session, match_player_mapper=match_player_mapper
            )
        self.input_PBP = InputPBP(
            db_session=self.db_session, 
            look_ups=mappers["look_ups"], update_on_conflict=update_on_conflict
            )

    @time_execution
    def input_game_dict(self, game: dict) -> None:

        match_id = self.input_gi._input_general_info(game)
        self.input_shifts._input_shifts(
            game["shifts"], game["HT"], game["VT"], match_id)
        self.input_PBP._input_PBP(game["PBP"], match_id)
        self.db_session.commit()


class InputGeneralInfo():


    def __init__(self, db_session: Session, 
                 stadium_mapper: dict, update_on_conflict: bool):
        self.db_method =  db_insert.DatabaseMethods(db_session)
        self.db_query = db_insert.Query(db_session)
        self.stadium_mapper = stadium_mapper
        self.update_on_conflict = update_on_conflict


    @time_execution
    def _input_general_info(self, game) -> int:
        stadium_id = self._get_stadium_id(game["stadium"])
        input_dict = self._get_general_info_input_dict(game, stadium_id)
        match_id = self.db_method.insert_update_or_ignore_on_conflict(
              db.Match,
              {
                  "match_id": input_dict["match_id"],
                  "stadium_id": input_dict["stadium_id"],
                  "date": input_dict["date"],
                  "time": input_dict["time"],
                  "attendance": input_dict["attendance"],
                  "home_team_id": input_dict["HT"],
                  "away_team_id": input_dict["VT"]
                  },
              self.update_on_conflict,
              TABLE_CONFIG["reference"][db.Match]["index_update"],
              True
              )

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
    

    def _get_general_info_input_dict(
            self, game: dict, stadium_id: int) -> dict:
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


    def __init__(
            self, db_session: Session, match_player_mapper: dict):
        self.db_method =  db_insert.DatabaseMethods(db_session)
        self.match_player_mapper = match_player_mapper
        self.input_shift_list = []
        self.update_on_conflict = False


    @time_execution
    def _input_shifts(
            self, shifts: dict, HT_id: int, VT_id: int, match_id :int) -> None:
        ids = {"TH": HT_id, "TV": VT_id}
        for team_type in ids:
            self._input_team_shifts(
                shifts[team_type], ids[team_type], match_id)
        self.db_method.insert_update_or_ignore_on_conflict_bulk(
            db.PlayerShift, 
            self.input_shift_list, 
            self.update_on_conflict,
            TABLE_CONFIG["reference"][db.PlayerShift]["index_update"]
            )


    def _input_team_shifts(
            self, shifts: list, team_id: int, match_id: int) -> None:
        for player_info in shifts:
            self._input_player_shifts(
                player_info, shifts[player_info], team_id, match_id)
            

    def _input_player_shifts(
            self, player_info: tuple, shifts: list, team_id: int, 
            match_id: int) -> None:
        player_id = self.match_player_mapper[team_id][player_info]
        for shift in shifts:
            shift_dict = self._get_shift_dict(
                match_id, player_id, team_id, shift)
            self.input_shift_list.append(shift_dict)


    def _get_shift_dict(
            self, match_id: int, player_id: int, team_id: int, shift: dict) -> dict:
        return {
              "match_id": match_id,
              "player_id": player_id,
              "team_id": team_id,
              "period": shift["period"],
              "shift_start": shift["shift_start"],
              "shift_end": shift["shift_end"]
        }
    

class PBPDB():


     def __init__(
             self, db_session: Session, look_ups: dict, 
             update_on_conflict: bool
             ):
        self.db_method = db_insert.DatabaseMethods(db_session)
        self.look_ups = look_ups
        self.update_on_conflict = update_on_conflict


     def _input_broken_play_info(self, play_id: int, play_desc: str) -> None:
         self.db_method.insert_update_or_ignore_on_conflict(
             db.BrokenPBP,
            {
                "play_id": play_id,
                "play_desc": play_desc
                },
            self.update_on_conflict,
            TABLE_CONFIG["reference"][db.BrokenPBP]["index_update"],
            )
          

     def _input_play_info(self, play: dict, play_id: int) -> int:
          pass
     

     def _input_broken_poi(
               self, play_id: int, team_id: int, poi: str, 
               error_type: str) -> None:
          self.db_method.insert_update_or_ignore_on_conflict(
              db.BrokenPOI,
              {
                  "play_id": play_id,
                  "team_id": team_id,
                  "poi": poi,
                  "error_type": error_type 
                  },
               self.update_on_conflict,
               TABLE_CONFIG["reference"][db.BrokenPOI]["index_update"]
               )

     
     def _get_reference_table_value(
             self, table: Table, val: str, optional=False):
         if val is None:
             if optional:
               return None
             else:
                 raise NoneReferenceValueError
         if val not in self.look_ups[table]:
             max_value = max(
                 self.look_ups[table].values(), default=1
                 )
             self.look_ups[table][val] = max_value + 1
             logger.info(
                 "New value %s added to table %s", val, table.__tablename__
                 )
             
         return self.look_ups[table][val]
     
                                                          
class BlockedShotDB(PBPDB):


    def _input_play_info(self, play: dict, play_id: int) -> None:
         blocker_type_id = self._get_reference_table_value(
            db.BlockerType, play["blocked_by"]
         )
         shot_type_id = self._get_reference_table_value(
             db.ShotType, play["shot_type"]
         )
         zone_id = self._get_reference_table_value(
              db.ZoneType, play["zone"]
         )
         
         self.db_method.insert_update_or_ignore_on_conflict(
             db.BlockedShotPlay,
             {
                   "play_id": play_id,
                   "shooter_id": play["shooter_id"],
                   "shooter_team_id": play["shooter_team_id"],
                   "blocker_type_id": blocker_type_id,
                   "blocker_id": play["blocker_id"],
                   "blocker_team_id": play["blocker_team_id"],
                   "zone_id": zone_id,
                   "shot_type_id": shot_type_id,
                   "broken_stick": play["broken_stick"],
                   "over_board": play["over_board"]
             },
             self.update_on_conflict,
             TABLE_CONFIG["reference"][db.BlockedShotPlay]["index_update"]
         )

    
class ChallengeDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:

          reason_id = self._get_reference_table_value(
               db.ChallengeReason, play["reason"]
          )
          result_id = self._get_reference_table_value(
               db.ChallengeResult, play["result"]
          )
          play_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.ChallengePlay,
               {
                    "play_id": play_id,
                    "team_id": play["team_id"],
                    "reason_id": reason_id,
                    "result_id": result_id,
                    "league_challenge": play["league_challenge"]
                    },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.ChallengePlay]["index_update"]

          )


class FaceOffDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          zone_id = self._get_reference_table_value(
              db.ZoneType, play["zone"]
          )
          self.db_method.insert_update_or_ignore_on_conflict(
               db.FaceoffPlay,
               {
                "play_id": play_id,
                "winner_id": play["faceoff_winner_id"],
                "loser_id": play["faceoff_loser_id"],
                "winner_team_id": play["winner_team_id"],
                "loser_team_id": play["losing_team_id"],
                "zone_id": zone_id
               },
               self.update_on_conflict,
               TABLE_CONFIG["reference"][db.FaceoffPlay]["index_update"]
          )


class GiveAwayDB(PBPDB):


     def _input_play_info(self, play: dict, play_id) -> None:
          zone_id = self._get_reference_table_value(
              db.ZoneType, play["zone"]
          )
          self.db_method.insert_update_or_ignore_on_conflict(
               db.GiveawayPlay,
               {
                "play_id": play_id,
                "player_id": play["player_id"],
                "team_id": play["team_id"],
                "zone_id": zone_id
               },
               self.update_on_conflict,
               TABLE_CONFIG["reference"][db.GiveawayPlay]["index_update"],
          )

     

class GoalDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          zone_id = self._get_reference_table_value(
              db.ZoneType, play["zone"]
          )
          shot_type_id = self._get_reference_table_value(
              db.ShotType, play["shot_type"], True
          )
          deflection_type_id = self._get_reference_table_value(
              db.DeflectionType, play["deflection_type"], True
          )
          goal_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.GoalPlay,
               {
                    "play_id": play_id,
                    "distance": play["distance"],
                    "penalty_shot": play["penalty_shot"],
                    "own_goal": play["own_goal"],
                    "team_id": play["team_id"],
                    "player_id": play["player_id"],
                    "shot_type_id": shot_type_id,
                    "deflection_type_id": deflection_type_id,
                    "zone_id": zone_id
                    },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.GoalPlay]["index_update"],
                True
          )

          if "assists" not in play:
               return play_id
          
          for assist in play["assists"]:
               self.db_method.insert_update_or_ignore_on_conflict(
                    db.AssistPlay,
                    {
                        "goal_id": goal_id,
                        "player_id": assist["player_id"],
                        "is_primary": assist["is_primary"]
                        },
                        self.update_on_conflict,
                        TABLE_CONFIG["reference"][db.AssistPlay]["index_update"]
               )

     
class HitDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          zone_id = self._get_reference_table_value(
               db.ZoneType, play["zone"]
               )
          self.db_method.insert_update_or_ignore_on_conflict(
               db.HitPlay,
               {
                   "play_id": play_id,
                   "hitter_id": play["hitter_id"],
                   "hitter_team_id": play["hitter_team_id"],
                   "victim_id": play["victim_id"],
                   "victim_team_id": play["victim_team_id"],
                   "zone_id": zone_id
                   },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.HitPlay]["index_update"]
          )


class MissedShotDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
         shot_result_id = self._get_reference_table_value(
               db.ShotResult, play["shot_result"], True
               )
         zone_id = self._get_reference_table_value(
               db.ZoneType, play["zone"], True
               )
         shot_type_id = self._get_reference_table_value(
               db.ShotType, play["shot_type"], True
               )
         self.db_method.insert_update_or_ignore_on_conflict(
              db.MissedShotPlay,
              {
                   "play_id": play_id,
                   "player_id": play["player_id"],
                   "team_id": play["team_id"],
                   "zone_id": zone_id,
                   "shot_type_id": shot_type_id,
                   "shot_result_id": shot_result_id,
                   "distance": play["distance"],
                   "broken_stick": play["broken_stick"],
                   "over_board": play["over_board"]
              },
              self.update_on_conflict,
              TABLE_CONFIG["reference"][db.MissedShotPlay]["index_update"]
         )


class PeriodDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          time_zone_id = self._get_reference_table_value(
               db.TimeZone, play["timezone"]
               )
          period_type_id = self._get_reference_table_value(
               db.PeriodType, play["period_type"]
               )
          play_id = self.db_method.insert_update_or_ignore_on_conflict(
              db.PeriodPlay,
              {
                   "play_id": play_id,
                   "time": play["time"],
                   "time_zone_id": time_zone_id,
                   "period_type_id": period_type_id
                    },
              self.update_on_conflict,
              TABLE_CONFIG["reference"][db.PenaltyPlay]["index_update"]
         )


class PenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          penalty_type_id = self._get_reference_table_value(
               db.PenaltyType, play["penalty_type"]
               )
          zone_id = self._get_reference_table_value(
               db.ZoneType, play["zone"]
               )  
          play_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.PenaltyPlay,
               {
                    "play_id": play_id,
                    "offender_id": play["offender_id"],
                    "offender_team_id": play["offender_team_id"],
                    "served_by_id": play["served_player_id"],
                    "victim_id": play["victim_id"],
                    "victim_team_id": play["victim_team_id"],
                    "zone_id": zone_id,
                    "penalty_type_id": penalty_type_id,
                    "penalty_minutes": play["penalty_minutes"],
                    "major_penalty": play["major_penalty"]
                    },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.PenaltyPlay]["index_update"]
                    )
          

class ShotDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          zone_id =self._get_reference_table_value(
               db.ZoneType, play["zone"]
               )  
          shot_type_id = self._get_reference_table_value(
               db.ShotType, play["shot_type"]
               )  
          deflection_type_id = self._get_reference_table_value(
               db.DeflectionType, play["deflection_type"], True
               )

          self.db_method.insert_update_or_ignore_on_conflict(
              db.ShotPlay,
              {
                   "play_id": play_id,
                   "player_id": play["player_id"],
                   "team_id": play["team_id"],
                   "zone_id": zone_id,
                   "shot_type_id": shot_type_id,
                   "distance": play["distance"],
                   "penalty_shot": play["penalty_shot"],
                   "broken_stick": play["broken_stick"],
                   "over_board": play["over_board"],
                   "deflection_type_id": deflection_type_id
              },
              self.update_on_conflict,
              TABLE_CONFIG["reference"][db.ShotPlay]["index_update"]
         )
          

class TakeAwayDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          zone_id = self._get_reference_table_value(
               db.ZoneType, play["zone"]
               )  
          self.db_method.insert_update_or_ignore_on_conflict(
               db.TakeawayPlay,
               {
                   "play_id": play_id,
                   "player_id": play["player_id"],
                   "team_id": play["team_id"],
                   "zone_id": zone_id
                   },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.TakeawayPlay]["index_update"],
          )
     

class DelayedPenaltyDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          play_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.DelayedPenaltyPlay,
               {
                   "play_id": play_id,
                   "team_id": play["team_id"]
                   },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.DelayedPenaltyPlay]["index_update"],
          )


class GameStopageDB(PBPDB):


     def _input_play_info(self, play: dict, play_id: int) -> None:
          stopage_type_id = self._get_reference_table_value(
               db.GameStopageType, play["stopage_type"]
               )  
          play_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.GameStopagePlay,
               {
                   "play_id": play_id,
                   "stopage_type_id": stopage_type_id
                   },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.GameStopagePlay]["index_update"]
          )

     
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
            self, db_session: Session, look_ups: dict, 
            update_on_conflict: bool
            ):
        self.db_method =  db_insert.DatabaseMethods(db_session)
        self.db_session = db_session
        self.input_pbp = PBPDB(
            db_session, look_ups, update_on_conflict
            )
        self.input_poi_list = []
        self.look_ups = look_ups
        self.update_on_conflict = update_on_conflict


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
        self.db_method.insert_update_or_ignore_on_conflict_bulk(
            db.PlayerOnIce, self.input_poi_list, self.update_on_conflict,
            TABLE_CONFIG["reference"][db.PlayerOnIce]["index_update"] 
            )
            

    def _input_play(self, play: dict, match_id: int) -> int:

          play_type_id = self.input_pbp._get_reference_table_value(
              db.PlayType, play["play_type"]
         )

          play_id = self.db_method.insert_update_or_ignore_on_conflict(
               db.Play,
               {
                    "play_type_id": play_type_id,
                    "match_id": match_id,
                    "period": play["period"],
                    "time": play["time"]
                    },
                self.update_on_conflict,
                TABLE_CONFIG["reference"][db.Play]["index_update"],
                True
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
          
          return self.INPUT_CLASSES[play_type](
              self.db_session, self.look_ups, self.update_on_conflict)


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
            self._add_poi_dict(play_id, player_id, team_id)


    def _add_poi_dict(
            self, play_id: int, player_id: int, team_id: int) -> None:
        
        poi = {
            "play_id": play_id,
            "player_id": player_id,
            "team_id": team_id
        }
        self.input_poi_list.append(poi)

























    