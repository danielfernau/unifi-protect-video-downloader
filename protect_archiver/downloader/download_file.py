# file downloader
import json
import logging
import os
import time

from typing import Any

import requests

from protect_archiver.errors import Errors
from protect_archiver.utils import format_bytes
from protect_archiver.utils import print_download_stats


def download_file(client: Any, query: str, filename: str) -> None:
    exit_code = 1
    retry_delay = max(client.download_wait, 3)
    uri = f"{client.session.authority}{client.session.base_path}{query}"

    # skip downloading files that already exist on disk if argument --skip-existing-files is present
    # TODO(dcramer): sanity check on filesize would be valuable here
    if bool(client.skip_existing_files) and os.path.exists(filename):
        logging.info(
            f"File {filename} already exists on disk and argument '--skip-existing-files' "
            "is present - skipping download \n"
        )
        client.files_skipped += 1
        return  # skip the download

    for retry_num in range(client.max_retries):
        # make the GET request to retrieve the video file or snapshot
        try:
            start = time.monotonic()
            response = (
                requests.get(
                    uri,
                    cookies={"TOKEN": client.session.get_api_token()},
                    verify=client.verify_ssl,
                    timeout=client.download_timeout,
                    stream=True,
                )
                if client.session.__class__.__name__ == "UniFiOSClient"
                else requests.get(
                    uri,
                    headers={"Authorization": f"Bearer {client.session.get_api_token()}"},
                    verify=client.verify_ssl,
                    timeout=client.download_timeout,
                    stream=True,
                )
            )

            if response.status_code == 401:
                # invalid current api token - we special case this
                # as we dont want to retry on consecutive auth failures
                # TODO: refactor this
                start = time.monotonic()
                response = (
                    requests.get(
                        uri,
                        cookies={"TOKEN": client.session.get_api_token(force=True)},
                        verify=client.verify_ssl,
                        timeout=client.download_timeout,
                        stream=True,
                    )
                    if client.session.__class__.__name__ == "UniFiOSClient"
                    else requests.get(
                        uri,
                        headers={
                            "Authorization": f"Bearer {client.session.get_api_token(force=True)}"
                        },
                        verify=client.verify_ssl,
                        timeout=client.download_timeout,
                        stream=True,
                    )
                )

            # write file to disk if response.status_code is 200,
            # otherwise log error and then either exit or skip the download
            if response.status_code != 200:
                try:
                    data = json.loads(response.content)
                except Exception:
                    data = None

                error_message = data.get("error") or data or "(no information available)"

                # TODO
                logging.exception(
                    f"Download failed with status {response.status_code} {response.reason}:\n"
                    f"{error_message}"
                )
                client.files_failed += 1
                # if response.status_code == 401:
                #     cls = Errors.AuthorizationFailed
                # else:
                #     cls = Errors.DownloadFailed
                # raise cls(
                #     f"Download failed with status {response.status_code} {response.reason}:\n{error_message}"
                # )

            else:
                total_bytes = int(response.headers.get("content-length") or 0)
                cur_bytes = 0
                if not total_bytes:
                    with open(filename, "wb") as fp:
                        content = response.content
                        cur_bytes = len(content)
                        total_bytes = cur_bytes
                        fp.write(content)

                else:
                    # skip download if remote file is smaller than 300b
                    if total_bytes < 300:
                        logging.warning(
                            "File is smaller than 300 bytes (empty video clip) - skipping download"
                        )
                        client.files_skipped += 1
                        return

                    with open(filename, "wb") as fp:
                        for chunk in response.iter_content(None):
                            cur_bytes += len(chunk)
                            fp.write(chunk)
                            # TODO
                            # done = int(50 * cur_bytes / total_bytes)
                            # sys.stdout.write("\r[%s%s] %sps" % ('=' * done, ' ' * (50-done),
                            #   format_bytes(cur_bytes//(time.monotonic() - start))))
                            # print('')

                elapsed = time.monotonic() - start
                logging.info(
                    f"Download successful after {int(elapsed)}s ({format_bytes(cur_bytes)}, "
                    f"{format_bytes(int(cur_bytes // elapsed))}ps)"
                )
                client.files_downloaded += 1
                client.bytes_downloaded += cur_bytes

        except requests.exceptions.RequestException as request_exception:
            # clean up
            if os.path.exists(filename):
                os.remove(filename)
            logging.exception(f"Download failed: {request_exception}")
            exit_code = 5
        except Errors.DownloadFailed:
            # clean up
            if os.path.exists(filename):
                os.remove(filename)
            logging.exception(
                f"Download failed with status {response.status_code} {response.reason}"
            )
            exit_code = 4
        else:
            return

        logging.warning(f"Retrying in {retry_delay} second(s)...")
        time.sleep(retry_delay)

    if not client.ignore_failed_downloads:
        logging.info(
            "To skip failed downloads and continue with next file, add argument"
            " '--ignore-failed-downloads'"
        )
        print_download_stats(client)
        raise Errors.ProtectError(exit_code)
    else:
        logging.info(
            "Argument '--ignore-failed-downloads' is present, continue downloading files..."
        )
        client.files_skipped += 1
