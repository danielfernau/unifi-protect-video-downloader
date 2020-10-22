from os import path

from protect_archiver.client.uck import CloudKeyClient
from protect_archiver.client.udm import DreamMachineClient
from protect_archiver.config import Config
from protect_archiver.downloader.get_camera_list import get_camera_list


# TODO(danielfernau): In Python3 all classes are new-style classes, parameter 'object' is no longer necessary, remove it
class ProtectClient(object):
    def __init__(
        self,
        address: str,
        hardware_type: str,
        username: str = Config.General.USERNAME,
        password: str = Config.General.PASSWORD,
        verify_ssl: bool = Config.General.VERIFY_SSL,
        use_unsafe_cookie_jar: bool = False,
        ignore_failed_downloads: bool = False,
        download_wait: int = 0,
        use_subfolders: bool = False,
        skip_existing_files: bool = False,
        destination_path: str = "./",
        touch_files: bool = False,
        # aka read_timeout - time to wait until a socket read response happens
        download_timeout: float = 60.0,
    ):
        self.address = address
        self.hardware_type = hardware_type
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
        self.max_retries = 3

        self._access_key = None
        self._api_token = None

        # TODO
        if self.hardware_type == "uck":
            self.port = Config.CloudKey.PORT
            self.session = CloudKeyClient(
                self.address, self.port, self.username, self.password, self.verify_ssl
            )
        elif self.hardware_type == "udm":
            self.port = Config.DreamMachine.PORT
            self.session = DreamMachineClient(
                self.address, self.port, self.username, self.password, self.verify_ssl
            )

    # TODO
    def get_camera_list(self):
        get_camera_list(self.session)


class ProtectError(object):
    pass
