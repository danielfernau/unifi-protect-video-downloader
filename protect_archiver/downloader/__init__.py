from protect_archiver.config import Config
from protect_archiver.utils import format_bytes


class Downloader:
    def __init__(
        self,
        ignore_failed_downloads: bool = Config.General.IGNORE_FAILED_DOWNLOADS,
        download_timeout: float = Config.General.DOWNLOAD_TIMEOUT,
        verify_ssl: bool = Config.General.VERIFY_SSL,
        max_retries: int = Config.General.MAX_RETRIES,
        skip_existing_files: bool = Config.General.SKIP_EXISTING_FILES,
        download_wait: int = Config.General.DOWNLOAD_WAIT,
    ):
        self.ignore_failed_downloads = ignore_failed_downloads
        self.download_timeout = download_timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.skip_existing_files = skip_existing_files
        self.download_wait = download_wait

        self.files_downloaded = 0
        self.bytes_downloaded = 0
        self.files_skipped = 0

        self.auth = Auth()

    def print_download_stats(self):
        files_total = self.files_downloaded + self.files_skipped
        print(
            f"{self.files_downloaded} files downloaded ({format_bytes(self.bytes_downloaded)}), "
            f"{self.files_skipped} files skipped, {files_total} files total"
        )


