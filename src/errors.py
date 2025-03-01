class EmptyReturnXpathValueError(ValueError):

    def __init__(self, xpath, value):
        message = (
            f"Extracted value from XPath ({xpath}) is {value}"
            f".Extraction failed"
                  )
        super().__init__(message)
