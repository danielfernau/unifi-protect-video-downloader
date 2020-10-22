class DreamMachineClient:
    def __init__(
        self, address: str, port: int, username: str, password: str, verify_ssl: bool,
    ):
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self._access_key = None
        self._api_token = None

    # TODO
