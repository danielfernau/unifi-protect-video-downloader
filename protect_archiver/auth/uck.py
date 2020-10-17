import logging
import requests

from protect_archiver.config import Config
from protect_archiver.errors import Errors
from protect_archiver.downloader import Downloader


class CloudKeyAuth:
    def __init__(
        self,
        address: str = Config.General.ADDRESS,
        port: int = Config.CloudKey.PORT,
        username: str = Config.General.USERNAME,
        password: str = Config.General.PASSWORD,
        verify_ssl: bool = Config.General.VERIFY_SSL,
    ):
        self.address = address
        self.port = port
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self._access_key = None
        self._api_token = None

    # get bearer token using username and password of local user
    def fetch_api_token(self) -> str:
        auth_uri = f"https://{self.address}:{self.port}/api/auth"
        response = requests.post(
            auth_uri,
            json={"username": self.username, "password": self.password},
            verify=self.verify_ssl,
        )
        print(response.status_code)
        if response.status_code != 200:
            if response.status_code == 404:
                logging.info("404 -- UDM?")
                # GET https://192.168.2.1/api/users/self, 401 if not logged in, 200 and user data if logged in
                # GET https://192.168.2.1/api/system, 200 {"hardware": {"shortname": "UDMPRO"}, "name": "UDM Pro"}
                # clear session cookies, then POST to https://192.168.2.1/api/auth/login with JSON payload user/pass
            else:
                logging.error(
                    f"Authentication as user {self.username} failed "
                    f"with status {response.status_code} {response.reason}"
                )
            Downloader.print_download_stats()  # TODO
            raise Errors.ProtectError(2)
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
