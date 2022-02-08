class Errors:
    def __init__(self) -> None:
        pass

    @Exception
    class ProtectError(Exception):
        def __init__(self, code: int) -> None:
            self.code = code

    @Exception
    class DownloadFailed(Exception):
        pass

    @Exception
    class AuthorizationFailed(Exception):
        pass
