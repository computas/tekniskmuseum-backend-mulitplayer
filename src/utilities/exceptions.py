"""
    File for declaring custom exceptions.
"""


class UserError(Exception):
    def __init__(self, message="Client error, please correct input data"):
        self.message = message
        super().__init__(self.message)
