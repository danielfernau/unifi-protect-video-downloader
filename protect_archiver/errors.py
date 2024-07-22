class Errors(Exception):
    """Base class for exceptions in your project."""
    pass


class ProtectError(Errors):
    """Exception raised when a general error in `protect_archiver` occurs.

    Attributes:
        code -- error code
    """

    def __init__(self, code: int):
        self.code = code


class DownloadFailed(Errors):
    """Exception raised when a file download fails."""
    pass


class AuthorizationFailed(Errors):
    """Exception raised for failed authorization attempts."""
    pass
