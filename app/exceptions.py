class BaseError(Exception):
    """Most base applications exceptions."""

    def __init__(self, message: str = ""):
        """Init class.

        Args:
            message (str): error string
        """
        self.message = message

    def __str__(self):
        return repr(self)

    def __repr__(self):
        repr_msg = f"{self.__class__.__name__}"

        if self.message:
            repr_msg += f": {self.message}"

        return repr_msg


class BaseGameError(BaseError):
    pass


class GameIsNotCreated(BaseGameError):
    pass


class GameIsFinished(BaseGameError):
    pass
