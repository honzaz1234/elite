class EmptyReturnXpathValueError(ValueError):

    def __init__(self, xpath, value):
        message = (
            f"Extracted value from XPath ({xpath}) is {value}"
            f".Extraction failed"
                  )
        super().__init__(message)


class WrongPlayDesc(AttributeError):

    def __init__(self, play_desc, play_type):
        message = (
            f"Play Description {play_desc} of type {play_type}"
            f" can not be scraped."
            f"It will be saved into WrongPlayDesc Table."
                  )
        super().__init__(message)
        self.play_desc = play_desc
        self.play_type = play_type


class MissingPlayerID(KeyError):


    def __init__(self, team_id, team_abb, player_number):
        message = (
            f"No player id found in the db_mapper for player from team"
            f" {team_abb} ('team id': {team_id}) with number: {player_number}"
                  )
        super().__init__(message)


class UpdateGameDataError(Exception):

    def __init__(self, game_id, team_home, team_away, date):
        message = (
            f"Error in updating game data of game {game_id} between "
            f"teams {team_home} and {team_away} "
            f"from data {date}"
                  )
        super().__init__(message)


class UpdatePlayKeyError(KeyError):



    def __init__(self, play: dict):
        message = {
            f"Key missing in dict {play}"
        }
        super().__init__(message)



