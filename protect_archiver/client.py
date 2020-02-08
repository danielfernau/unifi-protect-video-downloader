#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tool to download footage within a given time range from a local UniFi Protect system """

import json
import logging
import os
import time

from dataclasses import dataclass
from datetime import datetime
from os import path, makedirs
from typing import List

import requests

from .utils import calculate_intervals, format_bytes


@dataclass
class Camera:
    id: str
    name: str
    recording_start: datetime


class DownloadFailed(Exception):
    pass


class ProtectError(Exception):
    def __init__(self, code):
        self.code = code


class AuthorizationFailed(Exception):
    pass


class ProtectClient(object):
    def __init__(
        self,
        address: str = "unifi",
        port: int = 7443,
        username: str = "ubnt",
        password: str = None,
        verify_ssl: bool = False,
        ignore_failed_downloads: bool = False,
        download_wait: int = 0,
        use_subfolders: bool = False,
        skip_existing_files: bool = False,
        destination_path: str = "./",
        touch_files: bool = False,
        # aka read_timeout - time to wait until a socket read response happens
        download_timeout: int = 60,
        max_downloads_with_key: int = 3,
        max_downloads_with_auth: int = 10,
    ):
        self.address = address
        self.port = port
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
        self.files_skipped = 0
        self.max_retries = 3

        self.max_downloads_with_auth = max_downloads_with_auth
        self.max_downloads_with_key = max_downloads_with_key

        self._access_key = None
        self._api_token = None
        self._downloads_with_current_token = 0
        self._downloads_with_current_access_key = 0

    # API Authentication
    # get bearer token using username and password of local user
    def fetch_api_token(self) -> str:
        auth_uri = f"https://{self.address}:{self.port}/api/auth"
        response = requests.post(
            auth_uri,
            json={"username": self.username, "password": self.password},
            verify=self.verify_ssl,
        )
        if response.status_code != 200:
            logging.error(
                f"Authentication as user {self.username} failed with status {response.status_code} {response.reason}"
            )
            self.print_download_stats()
            raise ProtectError(2)
        logging.info(f"Successfully authenticated as user {self.username}")
        authorization_header = response.headers["Authorization"]
        assert authorization_header
        return authorization_header

    # get access key using bearer token
    def fetch_access_key(self, api_token: str) -> str:
        access_key_uri = f"https://{self.address}:{self.port}/api/auth/access-key"
        response = requests.post(
            access_key_uri,
            headers={"Authorization": "Bearer " + api_token},
            verify=self.verify_ssl,
        )
        if response.status_code != 200:
            logging.error(
                f"Failed to get access key from API. {response.status_code} {response.reason}"
            )
            self.print_download_stats()
            raise ProtectError(3)

        logging.info("Successfully requested API Access Key")
        json_response = response.json()
        access_key = json_response["accessKey"]
        return access_key

    def get_api_token(self, force: bool = False) -> str:
        if force:
            self._api_token = None
        # use the same api token (login session) for set number of downloads only (default: 10)
        elif self._downloads_with_current_token == int(self.max_downloads_with_auth):
            logging.info(
                f"API Token has been used for {self._downloads_with_current_token} download(s) - requesting new session token..."
            )
            self._api_token = None

        if self._api_token is None:
            # get new API auth bearer token and access key
            self._api_token = self.fetch_api_token()
            self._access_key = self.fetch_access_key(self._api_token)
            self._downloads_with_current_token = 0
            self._downloads_with_current_access_key = 0

        return self._api_token

    def get_access_key(self, api_token: str = None, force: bool = False) -> str:
        if force:
            self._api_token = None
        # use the same access key for set number of downloads only (default: 3)
        elif self._downloads_with_current_access_key == self.max_downloads_with_key:
            logging.info(
                f"Access Key has been used for {self._downloads_with_current_access_key} download(s) - requesting new access key..."
            )
            self._access_key = None

        if self._access_key is None:
            # request new access key
            self._access_key = self.fetch_access_key(api_token or self.get_api_token())
            self._downloads_with_current_access_key = 0

        return self._access_key

    # file downloader
    def download_file(self, uri: str, file_name: str):
        retry_delay = max(self.download_wait, 3)
        for retry_num in range(self.max_retries):
            self._downloads_with_current_token += 1
            self._downloads_with_current_access_key += 1

            # make the GET request to retrieve the video file or snapshot
            try:
                start = time.monotonic()
                response = requests.get(
                    uri,
                    verify=self.verify_ssl,
                    timeout=self.download_timeout,
                    stream=True,
                )

                # write file to disk if response.status_code is 200,
                # otherwise log error and then either exit or skip the download
                if response.status_code == 401:
                    # invalid current api token - we special case this
                    # as we dont want to retry on consecutive auth failures
                    # TODO: refactor this
                    self.get_api_token(force=True)
                    start = time.monotonic()
                    response = requests.get(
                        uri,
                        verify=self.verify_ssl,
                        timeout=self.download_timeout,
                        stream=True,
                    )
                    if response.status_code == 401:
                        raise AuthorizationFailed
                if response.status_code != 200:
                    try:
                        data = json.loads(response.content)
                    except Exception:
                        data = None

                    error_message = (
                        data.get("error") or data or "(no information available)"
                    )
                    raise DownloadFailed(
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
                            # sys.stdout.write("\r[%s%s] %sps" % ('=' * done, ' ' * (50-done), format_bytes(cur_bytes//(time.monotonic() - start))))
                            # print('')

                elapsed = time.monotonic() - start
                logging.info(
                    f"Download successful after {int(elapsed)}s ({format_bytes(cur_bytes // elapsed)}ps)"
                )
                self.files_downloaded += 1

            except requests.exceptions.RequestException as request_exception:
                # clean up
                if path.exists(file_name):
                    os.remove(file_name)
                logging.exception(f"Download failed: {request_exception}")
                exit_code = 5
            except DownloadFailed:
                # clean up
                if path.exists(file_name):
                    os.remove(file_name)
                logging.exception(
                    f"Download failed with status {response.status_code} {response.reason}"
                )
                exit_code = 4
            else:
                return

            logging.warn(f"Retrying in {retry_delay} second(s)...")
            time.sleep(retry_delay)

        if not self.ignore_failed_downloads:
            logging.info(
                "To skip failed downloads and continue with next file, add argument '--ignore-failed-downloads'"
            )
            self.print_download_stats()
            raise ProtectError(exit_code)
        else:
            logging.info(
                "Argument '--ignore-failed-downloads' is present, continue downloading files..."
            )
            self.files_skipped += 1

    def print_download_stats(self):
        files_total = self.files_downloaded + self.files_skipped
        print(
            f"{self.files_downloaded} files downloaded, {self.files_skipped} files skipped, {files_total} files total"
        )

    # get camera list
    def get_camera_list(self, connected=True) -> List[Camera]:
        bootstrap_uri = f"https://{self.address}:{self.port}/api/bootstrap"
        response = requests.get(
            bootstrap_uri,
            headers={"Authorization": "Bearer " + self.get_api_token()},
            verify=self.verify_ssl,
        )
        if response.status_code != 200:
            return []

        logging.info("Successfully retrieved data from /api/bootstrap")
        json_response = response.json()
        cameras = json_response["cameras"]

        camera_list = []
        for camera in cameras:
            if connected and camera["state"] != "CONNECTED":
                continue
            camera_list.append(
                Camera(
                    id=camera["id"],
                    name=camera["name"],
                    recording_start=datetime.utcfromtimestamp(
                        camera["stats"]["video"]["recordingStart"] / 1000
                    ),
                )
            )

        logging.info(
            "Cameras found:\n{}".format(
                "\n".join(f"- {camera.name} ({camera.id})" for camera in camera_list)
            )
        )

        return camera_list

    def download_footage(self, start: datetime, end: datetime, camera: Camera):
        # make camera name safe for use in file name
        # TODO(dcramer): It'd be nice to map this to something similar to what the UI gives you (somewhat more readable)
        camera_name_fs_safe = (
            "".join([c for c in camera.name if c.isalpha() or c.isdigit() or c == " "])
            .rstrip()
            .replace(" ", "_")
            + "_"
            + str(camera.id)[-4:]
        )

        logging.info(f"Downloading footage for camera '{camera.name}' ({camera.id})")

        # split requested time frame into chunks of 1 hour or less and download them one by one
        for interval_start, interval_end in calculate_intervals(start, end):
            # wait n seconds before starting next download (if parameter is set)
            if self.download_wait != 0 and self.total_downloads == 0:
                logging.debug(
                    f"Command line argument '--wait-between-downloads' is set to {self.download_wait} second(s)... \n"
                )
                time.sleep(int(self.download_wait))

            # start and end time of the video segment to be downloaded
            js_timestamp_range_start = int(interval_start.timestamp()) * 1000
            js_timestamp_range_end = int(interval_end.timestamp()) * 1000

            # file path for download
            if bool(self.use_subfolders):
                folder_year = interval_start.strftime("%Y")
                folder_month = interval_start.strftime("%m")
                folder_day = interval_start.strftime("%d")

                dir_by_date_and_name = (
                    f"{folder_year}/{folder_month}/{folder_day}/{camera_name_fs_safe}"
                )
                target_with_date_and_name = (
                    f"{self.destination_path}/{dir_by_date_and_name}"
                )

                download_dir = target_with_date_and_name
                if not path.isdir(target_with_date_and_name):
                    makedirs(target_with_date_and_name, exist_ok=True)
                    logging.info(f"Created path {target_with_date_and_name}")
                    download_dir = target_with_date_and_name
            else:
                download_dir = self.destination_path

            # file name for download
            filename_timestamp_start = interval_start.strftime("%Y-%m-%d--%H-%M-%S%z")
            filename_timestamp_end = interval_end.strftime("%Y-%m-%d--%H-%M-%S%z")
            filename_timestamp = f"{filename_timestamp_start}_{filename_timestamp_end}"
            filename = f"{download_dir}/{camera_name_fs_safe}_{filename_timestamp}.mp4"

            logging.info(
                f"Downloading video for time range {interval_start} - {interval_end} to {filename}"
            )

            # skip downloading files that already exist on disk if argument --skip-existing-files is present
            # TODO(dcramer): sanity check on filesize would be valuable here
            if bool(self.skip_existing_files) and path.exists(filename):
                logging.debug(
                    "File already exists on disk and argument '--skip-existing-files' is present - skipping download \n"
                )
                self.files_skipped += 1
                continue

            # create file without content if argument --touch-files is present
            # XXX(dcramer): would be nice to document why you'd ever want this
            if bool(self.touch_files) and not path.exists(filename):
                logging.debug(
                    f"Argument '--touch-files' is present. Creating file at {filename}"
                )
                open(filename, "a").close()

            # build video export API address
            address = f"https://{self.address}:{self.port}/api/video/export?accessKey={self.get_access_key()}&camera={camera.id}&start={js_timestamp_range_start}&end={js_timestamp_range_end}"

            # download the file
            self.download_file(address, filename)

    def download_snapshot(self, start: datetime, camera: Camera):
        # make camera name safe for use in file name
        camera_name_fs_safe = (
            "".join([c for c in camera.name if c.isalpha() or c.isdigit() or c == " "])
            .rstrip()
            .replace(" ", "_")
            + "_"
            + str(camera.id)[-4:]
        )

        logging.info(f"Downloading snapshot for camera '{camera.name}' ({camera.id})")

        # file path for download
        if bool(self.use_subfolders):
            folder_year = start.strftime("%Y")
            folder_month = start.strftime("%m")
            folder_day = start.strftime("%d")

            dir_by_date_and_name = (
                f"{folder_year}/{folder_month}/{folder_day}/{camera_name_fs_safe}"
            )
            target_with_date_and_name = (
                f"{self.destination_path}/{dir_by_date_and_name}"
            )

            download_dir = target_with_date_and_name
            if not path.isdir(target_with_date_and_name):
                makedirs(target_with_date_and_name, exist_ok=True)
                logging.info(f"Created path {target_with_date_and_name}")
                download_dir = target_with_date_and_name
        else:
            download_dir = self.destination_path

        # file name for download
        filename_timestamp = start.strftime("%Y-%m-%d--%H-%M-%S%z")
        filename = f"{download_dir}/{camera_name_fs_safe}_{filename_timestamp}.jpg"

        logging.info(f"Downloading snapshot for time {start} to {filename}")

        # create file without content if argument --touch-files is present
        if bool(self.touch_files) and not path.exists(filename):
            logging.debug(
                f"Argument '--touch-files' is present. Creating file at {filename}"
            )
            open(filename, "a").close()

        js_timestamp_start = int(start.timestamp()) * 1000
        # build snapshot export API address
        address = f"https://{self.address}:{self.port}/api/cameras/{camera.id}/snapshot?accessKey={self.get_access_key()}&ts={js_timestamp_start}"

        # download the file
        self.download_file(address, filename)
