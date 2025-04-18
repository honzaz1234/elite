class EmptyReturnXpathValueError(ValueError):

    def __init__(self, xpath, value):
        message = (
            f"Extracted value from XPath ({xpath}) is {value}"
            f".Extraction failed"
                  )
        super().__init__(message)

class WrongPlayDesc(ValueError):

    def __init__(self, play_desc, play_type):
        message = (
            f"Play Description {play_desc} of type {play_type}"
            f" can not be scraped."
            f"It will be saved into WrongPlayDesc Table."
                  )
        super().__init__(message)
        self.play_desc = play_desc
        self.play_type = play_type

