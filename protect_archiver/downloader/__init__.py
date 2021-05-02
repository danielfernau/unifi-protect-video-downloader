from protect_archiver.config import Config
from protect_archiver.downloader.download_file import download_file
from protect_archiver.downloader.download_footage import download_footage
from protect_archiver.downloader.download_motion_event import download_motion_event
from protect_archiver.downloader.download_snapshot import download_snapshot
from protect_archiver.downloader.get_camera_list import get_camera_list
from protect_archiver.downloader.get_motion_event_list import get_motion_event_list


class Downloader:
    def __init__(
        self,
        ignore_failed_downloads: bool = Config.IGNORE_FAILED_DOWNLOADS,
        download_timeout: float = Config.DOWNLOAD_TIMEOUT,
        verify_ssl: bool = Config.VERIFY_SSL,
        max_retries: int = Config.MAX_RETRIES,
        skip_existing_files: bool = Config.SKIP_EXISTING_FILES,
        download_wait: int = Config.DOWNLOAD_WAIT,
    ):
        self.ignore_failed_downloads = ignore_failed_downloads
        self.download_timeout = download_timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.skip_existing_files = skip_existing_files
        self.download_wait = download_wait

    @staticmethod
    def get_camera_list(session):
        return get_camera_list(session)

    @staticmethod
    def get_motion_event_list(session, start, end):
        return get_motion_event_list(session, start, end)

    @staticmethod
    def download_file(client, video_export_query, filename):
        return download_file(client, video_export_query, filename)

    @staticmethod
    def download_footage(client, start, end, camera):
        return download_footage(client, start, end, camera)

    @staticmethod
    def download_snapshot(client, start, camera):
        return download_snapshot(client, start, camera)

    @staticmethod
    def download_motion_event(client, motion_event, camera, download_motion_heatmaps):
        download_motion_event(client, motion_event, camera, download_motion_heatmaps)
