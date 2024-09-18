import logging

from typing import Optional

import requests

from protect_archiver.errors import ProtectError


class LegacyClient:
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
        self.base_path = "/api"

    # get bearer token using username and password of local user
    def fetch_api_token(self) -> str:
        auth_uri = f"{self.protocol}://{self.address}:{self.port}/api/auth"

        response = requests.post(
            auth_uri,
            json={"username": self.username, "password": self.password},
            verify=self.verify_ssl,
        )

        if response.status_code != 200:
            if response.status_code == 404:
                logging.info("404 -- UniFi OS?")
                # GET https://192.168.2.1/api/users/self, 401 if not logged in, 200 and user data if logged in
                # GET https://192.168.2.1/api/system, 200 {"hardware": {"shortname": "UDMPRO"}, "name": "UDM Pro"}
                # clear session cookies, then POST to https://192.168.2.1/api/auth/login with JSON payload user/pass
            else:
                logging.error(
                    f"Authentication as user {self.username} failed "
                    f"with status {response.status_code} {response.reason}"
                )
            # Downloader.print_download_stats()  # TODO
            raise ProtectError(2)

        logging.info(f"Successfully authenticated as user {self.username}")

        authorization_header = response.headers["Authorization"]

        assert authorization_header
        return authorization_header

    def get_api_token(self, force: bool = False) -> str:
        if force:
            self._api_token = None

        if self._api_token is None:
            # get new API auth bearer token and access key
            self._api_token = self.fetch_api_token()

        return self._api_token
