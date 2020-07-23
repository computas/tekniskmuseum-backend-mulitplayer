"""
    File for declaring custom exceptions.
"""


class UserError(Exception):
    """
        User error to be invoked when the frontend sends invalid requests
    """

    def __init__(self, message="Client error, please correct input data"):
        """
            message -> str: the message to be passed to the user
        """
        self.message = message
        super().__init__(self.message)
