import logging

from typing import Optional

import requests

from protect_archiver.errors import DownloadFailed
from protect_archiver.errors import ProtectError


class UniFiOSClient:
    def __init__(
        self,
        protocol: str,
        address: str,
        port: int,
        username: str,
        password: str,
        verify_ssl: bool,
    ) -> None:
        self.protocol = protocol
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self._access_key: Optional[str] = None
        self._api_token: Optional[str] = None

        self.authority = f"{self.protocol}://{self.address}:{self.port}"
        self.base_path = "/proxy/protect/api"

    def fetch_session_cookie_token(self) -> str:
        auth_uri = f"{self.protocol}://{self.address}:{self.port}/api/auth/login"

        response = requests.post(
            auth_uri,
            json={"username": self.username, "password": self.password},
            verify=self.verify_ssl,
        )

        if response.status_code != 200:
            logging.info(
                f"Authentication failed with status code {response.status_code}! Check username and"
                " password."
            )
            raise ProtectError(2)

        logging.debug("Successfully authenticated user using a session cookie")

        session_cookie_token = response.cookies.get("TOKEN")

        assert session_cookie_token
        return session_cookie_token

    def get_api_token(self, force: bool = False) -> str:
        if force:
            self._api_token = None

        if self._api_token is None:
            self._api_token = self.fetch_session_cookie_token()

        return self._api_token
