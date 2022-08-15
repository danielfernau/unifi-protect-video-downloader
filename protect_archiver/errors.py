class Errors:
    def __init__(self) -> None:
        pass

    class ProtectError(Exception):
        def __init__(self, code: int) -> None:
            self.code = code

    class DownloadFailed(Exception):
        pass

    class AuthorizationFailed(Exception):
        pass
