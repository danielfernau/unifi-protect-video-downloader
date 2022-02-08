from datetime import datetime
from os import path
from typing import Any
from typing import List
from typing import Optional

from protect_archiver.client.legacy import LegacyClient
from protect_archiver.client.unifi_os import UniFiOSClient
from protect_archiver.config import Config
from protect_archiver.downloader import Downloader


class ProtectClient:
    def __init__(
        self,
        address: str = Config.ADDRESS,
        port: int = Config.PORT,
        protocol: str = Config.PROTOCOL,
        username: str = Config.USERNAME,
        password: Optional[str] = Config.PASSWORD,
        verify_ssl: bool = Config.VERIFY_SSL,
        not_unifi_os: bool = False,
        # use_unsafe_cookie_jar: bool = Config.USE_UNSAFE_COOKIE_JAR,
        ignore_failed_downloads: bool = Config.IGNORE_FAILED_DOWNLOADS,
        download_wait: int = Config.DOWNLOAD_WAIT,
        use_subfolders: bool = Config.USE_SUBFOLDERS,
        skip_existing_files: bool = Config.SKIP_EXISTING_FILES,
        destination_path: str = Config.DESTINATION_PATH,
        touch_files: bool = Config.TOUCH_FILES,
        # aka read_timeout - time to wait until a socket read response happens
        download_timeout: float = Config.DOWNLOAD_TIMEOUT,
    ) -> None:
        self.protocol = protocol
        self.address = address
        self.port = port if port is not None else 7443 if not_unifi_os else 443
        self.not_unifi_os = not_unifi_os
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self.ignore_failed_downloads = ignore_failed_downloads
        self.download_wait = download_wait
        self.download_timeout = download_timeout
        self.use_subfolders = use_subfolders
        self.skip_existing_files = skip_existing_files
        self.touch_files = touch_files

        self.destination_path = path.abspath(destination_path)

        self.files_downloaded = 0
        self.bytes_downloaded = 0
        self.files_skipped = 0
        self.files_failed = 0
        self.max_retries = 3

        self._access_key = None
        self._api_token = None

        if not_unifi_os:
            self.port = 7443
            self.base_path = "/api"

            assert self.password
            self.session: Any = LegacyClient(
                self.protocol,
                self.address,
                self.port,
                self.username,
                self.password,
                self.verify_ssl,
            )
        else:
            self.port = 443
            assert self.password
            self.session = UniFiOSClient(
                self.protocol,
                self.address,
                self.port,
                self.username,
                self.password,
                self.verify_ssl,
            )

    def get_camera_list(self, connected: bool = True) -> List[Any]:
        return Downloader.get_camera_list(self.session, connected)

    def get_motion_event_list(
        self, start: datetime, end: datetime, camera_list: List[Any]
    ) -> List[Any]:
        return Downloader.get_motion_event_list(self.session, start, end, camera_list)

    def get_session(self) -> Any:
        return self.session


# TODO
# class ProtectError(object):
#     pass
