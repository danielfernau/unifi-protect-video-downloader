class Error(Exception):
    """Base class for all custom exceptions in this project.

    This class can be used as a catch-all for project-specific exceptions, allowing 
    for uniform handling or logging of errors unique to this application.
    """
    pass


class ProtectError(Error):
    """Handles errors related to core application functionality.

    Attributes:
        code (int): Numeric identifier for the type of error encountered, useful for 
                    diagnostics or user feedback.
    """

    def __init__(self, code: int):
        # Assign the error code for further reference
        self.code = code
        # Construct the base exception message with the specific error code
        super().__init__(f"ProtectError with error code: {code}")


class DownloadFailed(Error):
    """Signifies that a file download process has been unsuccessful.

    Raises when there are issues with downloading files, excluding authorization 
    problems, which are handled by `AuthorizationFailed`. Common causes might include 
    network failures or file access issues.
    """
    pass


class AuthorizationFailed(Error):
    """Represents failures in the authorization or authentication process.

    This should be used when access is denied due to invalid credentials, expired sessions, 
    or any other issues specifically related to gaining authorized access.
    """
    pass
