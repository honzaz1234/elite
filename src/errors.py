class EmptyReturnXpathValueError(ValueError):

    def __init__(self, xpath: str, value: str):
        message = (
            f"Extracted value from XPath ({xpath}) is {value}"
            f".Extraction failed"
                  )
        super().__init__(message)


class WrongPlayDesc(AttributeError):

    def __init__(self, play_desc: dict, play_type: str):
        message = (
            f"Play Description {play_desc} of type {play_type}"
            f" can not be scraped."
            f"It will be saved into WrongPlayDesc Table."
                  )
        super().__init__(message)
        self.play_desc = play_desc
        self.play_type = play_type


class MissingPlayerID(KeyError):


    def __init__(self, team_id: int, team_abb: str, player_number: int):
        message = (
            f"No player id found in the db_mapper for player from team"
            f" {team_abb} ('team id': {team_id}) with number: {player_number}"
                  )
        super().__init__(message)


class MissingPlayer(KeyError):


    def __init__(self, player_id: int, team_abb: str, team_id: int):
        message = (
            "No player was found for player_id %s in the db_mapper for "
            "team %s ('team id': %s)" % (
            player_id, team_abb, team_id
            )
        )
        super().__init__(message)


class UpdateGameDataError(Exception):

    def __init__(
            self, match_id: int, team_home: str, team_away: str, date: str):
        message = (
            f"Error in updating game data of game {match_id} between "
            f"teams {team_home} and {team_away} "
            f"from data {date}"
                  )
        super().__init__(message)


class UpdatePlayError(KeyError):



    def __init__(self, play: dict):
        message = {
            f"Error raised while updating following play dict: {play}"
        }
        super().__init__(message)


class TooManyPOIError(ValueError):


    def __init__(self, poi: list, team_abb: str):
        message = {
            f"There is too many players on ice: {poi} for team {team_abb}"
        }
        super().__init__(message)


class MissingPlayKeyError(KeyError):


    def __init__(self, play_info: dict):
        message = {
            f"There is a missing key in play info dict: {play_info}"
        }
        super().__init__(message)


class GameDataError(Exception):


    def __init__(self, game_id: int, season: str):
        message = {
            f"Game Data Pipe Line failed for game {game_id} in season {season}"
        }
        super().__init__(message)

class InputPlayDBError(Exception):


    def __init__(self, original_message: str, play_type: str, play: dict):
        message = {
            f"{original_message} ({play_type}) ({play})"
        }
        super().__init__(message)


class NoneReferenceValueError(TypeError):
    def __init__(self, table: str):
        message = {
            f"Mandatory value for column from table {table}"
            f" is equal to None"
        }
        super().__init__(message)









