class Errors:
    def __init__(self):
        pass

    @Exception
    class ProtectError(Exception):
        def __init__(self, code):
            self.code = code

    @Exception
    class DownloadFailed(Exception):
        pass

    @Exception
    class AuthorizationFailed(Exception):
        pass
