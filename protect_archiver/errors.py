class Errors:
    def __init__(self) -> None:
        pass

    class ProtectError(Exception):
        def __init__(self, code: int) -> None:
            self.code = code
            super().__init__(f"ProtectError with code: {code}")
