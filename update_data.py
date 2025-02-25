import re

from logger.logger import logger


class UpdatePBP():


    PATTERN = (
        rf"(?P<number>\d+)\s+(?P<surname>[A-Z]+),\s+"
        rf"(?P<first_name>[A-Z]+)"
        )
    
    def __init__(self):
        pass


    def update_players_shifts(self, shifts: dict) -> dict:

        updated_dict = {}
        for player_name_number in shifts:
            updated_name, number, updated_shifts = self.get_player_shift(
                player_name_number = player_name_number
                shifts=shifts[player_name])
            updated_dict[(updated_name, number)] = updated_shifts

        return updated_shifts
    
    
    def update_player_shifts(
            self, player_name_number: str, shifts: dict) -> tuple:

        updated_name, number = self.get_name_number(
            player_name_number=player_name_number)
        shifts = self.update_shifts(shifts=shifts)

        return updated_name, number, shifts
    

    def get_name_number(self, player_name_number: str) -> tuple:

        match = re.match(self.PATTERN, player_name_number)

        if not match:
            logger.error(f"Regex failed to match pattern for input: '"
                         f"{player_name_number}'")
            raise ValueError(f"Invalid player name/number format: '"
                             f"{player_name_number}'")

        player_dict = match.groupdict()
        player_name = f"{player_dict['first_name']} {player_dict['surname']}"
        
        return player_name, player_dict["number"]
    

    def update_shifts(self, shifts: dict) -> dict:

        shifts_updated = {}        
        shifts_updated["period"] = self.get_updated_period(shifts["period"])


    def get_updated_period(self, period: str) -> int:

        try:
            result = int(period)

            return result
        
        except ValueError:
            logger.error(f"ValueError: Invalid integer value '{period}'")
            raise ValueError(f"Invalid integer value: {period}")
        except TypeError:
            logger.error(f"TypeError: Expected str, int, or float, but got"
                         f" {type(period).__name__}")
            raise TypeError(f"Expected str, int, or float, but got"
                            f" {type(period).__name__}")
        

    def get_updated_shift(self, shift_string: str):
        try:
            if not isinstance(shift_string, (str, bytes)):
                raise TypeError(f"Expected a string or bytes-like object, but got {type(shift_string).__name__}")

            matches = re.findall(pattern, shift_string)
            logger.info(f"Pattern '{shift_string}' found {len(matches)} matches in text.")
            return matches
        except re.error as e:
            logger.error(f"Regex error: {e}")
            raise
        except TypeError as e:
            logger.error(f"TypeError: {e}")
            raise

        



