"""
    File for declaring custom exceptions.
"""


class UserError(Exception):
    """
        This error should be raised every time there is a user error, e.g. invalid data formatting. 
    """

    def __init__(self, message="Client error, please correct input data"):
        self.message = message
        super().__init__(self.message)
