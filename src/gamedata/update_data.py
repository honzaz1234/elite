import re

import common_functions
from logger.logging_config import logger


class UpdatePBP():


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
        shifts = self.update_shifts(shifts=shifts)

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
        shifts_updated["period"] = self.get_updated_period(shifts["period"])
        shifts_updated["shift_start"] = self.get_updated_shift(
            shifts["shift_start"])
        shifts_updated["shift_end"] = self.get_updated_shift(
            shifts["shift_end"])
        
        return shifts_updated


    def get_updated_period(self, period: str) -> int:

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
        

    def get_updated_shift(self, shift_string: str):
        try:
            if not isinstance(shift_string, (str, bytes)):
                error_message = (
                    f"Expected a string or bytes-like object"
                    f", but got {type(shift_string).__name__}"
                    )
                common_functions.log_and_raise(error_message, TypeError)
            match = re.match(self, shift_string)
            shift = match.group("shift")
            shift_seconds = common_functions.convert_to_seconds(shift)
            logger.debug(f"Pattern '{shift_string}' found")

            return shift_seconds
        except re.error as e:
            common_functions.log_and_raise(e, re.error)
        except TypeError as e:
            common_functions.log_and_raise(e, TypeError)

        



