# file downloader
import json
import logging
import time
import requests
import os

from protect_archiver.errors import Errors
from protect_archiver.utils import format_bytes


def download_file(self, uri: str, file_name: str, auth: Auth):
    exit_code = 1
    retry_delay = max(self.download_wait, 3)

    # skip downloading files that already exist on disk if argument --skip-existing-files is present
    # TODO(dcramer): sanity check on filesize would be valuable here
    if bool(self.skip_existing_files) and os.path.exists(file_name):
        logging.info(
            f"File {file_name} already exists on disk and argument '--skip-existing-files' "
            f"is present - skipping download \n"
        )
        self.files_skipped += 1
        return  # skip the download

    for retry_num in range(self.max_retries):
        # make the GET request to retrieve the video file or snapshot
        try:
            start = time.monotonic()
            response = requests.get(
                uri,
                headers={"Authorization": "Bearer " + auth.get_api_token()},
                verify=self.verify_ssl,
                timeout=self.download_timeout,
                stream=True,
            )

            if response.status_code == 401:
                # invalid current api token - we special case this
                # as we dont want to retry on consecutive auth failures
                # TODO: refactor this
                start = time.monotonic()
                response = requests.get(
                    uri,
                    headers={
                        "Authorization": "Bearer " + auth.get_api_token(force=True)
                    },
                    verify=self.verify_ssl,
                    timeout=self.download_timeout,
                    stream=True,
                )

            # write file to disk if response.status_code is 200,
            # otherwise log error and then either exit or skip the download
            if response.status_code != 200:
                try:
                    data = json.loads(response.content)
                except Exception:
                    data = None

                error_message = (
                    data.get("error") or data or "(no information available)"
                )
                if response.status_code == 401:
                    cls = Errors.AuthorizationFailed
                else:
                    cls = Errors.DownloadFailed
                raise cls(
                    f"Download failed with status {response.status_code} {response.reason}:\n{error_message}"
                )

            total_bytes = int(response.headers.get("content-length") or 0)
            cur_bytes = 0
            if not total_bytes:
                with open(file_name, "wb") as fp:
                    content = response.content
                    cur_bytes = len(content)
                    total_bytes = cur_bytes
                    fp.write(content)

            else:
                with open(file_name, "wb") as fp:
                    for chunk in response.iter_content(4096):
                        cur_bytes += len(chunk)
                        fp.write(chunk)
                        # done = int(50 * cur_bytes / total_bytes)
                        # sys.stdout.write("\r[%s%s] %sps" % ('=' * done, ' ' * (50-done),
                        #   format_bytes(cur_bytes//(time.monotonic() - start))))
                        # print('')

            elapsed = time.monotonic() - start
            logging.info(
                f"Download successful after {int(elapsed)}s ({format_bytes(cur_bytes)}, "
                f"{format_bytes(int(cur_bytes // elapsed))}ps)"
            )
            self.files_downloaded += 1
            self.bytes_downloaded += cur_bytes

        except requests.exceptions.RequestException as request_exception:
            # clean up
            if os.path.exists(file_name):
                os.remove(file_name)
            logging.exception(f"Download failed: {request_exception}")
            exit_code = 5
        except Errors.DownloadFailed:
            # clean up
            if os.path.exists(file_name):
                os.remove(file_name)
            logging.exception(
                f"Download failed with status {response.status_code} {response.reason}"
            )
            exit_code = 4
        else:
            return

        logging.warning(f"Retrying in {retry_delay} second(s)...")
        time.sleep(retry_delay)

    if not self.ignore_failed_downloads:
        logging.info(
            "To skip failed downloads and continue with next file, add argument '--ignore-failed-downloads'"
        )
        self.print_download_stats()
        raise Errors.ProtectError(exit_code)
    else:
        logging.info(
            "Argument '--ignore-failed-downloads' is present, continue downloading files..."
        )
        self.files_skipped += 1
