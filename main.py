#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Tool to download footage within a given time range from a local UniFi Protect system """

import argparse
from datetime import datetime, timedelta
import dateutil.parser
import time

from os import path, makedirs
from typing import List, Mapping

import requests
import urllib3

__author__ = "Daniel Fernau"
__copyright__ = "Copyright 2019, Daniel Fernau"
__license__ = "GPLv3"
__version__ = "1.1.1"


# return time difference between given date_time_object and next full hour
def diff_round_up_to_full_hour(date_time_object):
    if date_time_object.minute != 0 or date_time_object.second != 0:
        return date_time_object.replace(
            second=0, microsecond=0, minute=0, hour=date_time_object.hour
        ) + timedelta(hours=1, minutes=0)
    else:
        return date_time_object.replace(
            second=0, microsecond=0, minute=0, hour=date_time_object.hour
        ) + timedelta(hours=0, minutes=0)


# return time difference between given date_time_object and past full hour
def diff_round_down_to_full_hour(date_time_object):
    return date_time_object.replace(
        second=0, microsecond=0, minute=0, hour=date_time_object.hour
    ) + timedelta(hours=0, minutes=0)


# calculate and yield the intervals between the given start and end datetime objects
# example:
#   start = 01.01.1970 08:30:00
#   end = 01.01.1970 13:15:00
#
#   returns:
#       01.01.1970 08:30:00 - 01.01.1970 08:59:59
#       01.01.1970 09:00:00 - 01.01.1970 09:59:59
#       01.01.1970 10:00:00 - 01.01.1970 10:59:59
#       01.01.1970 11:00:00 - 01.01.1970 11:59:59
#       01.01.1970 12:00:00 - 01.01.1970 12:59:59
#       01.01.1970 13:00:00 - 01.01.1970 13:14:59
def calculate_intervals(start, end):
    # calculate time differences to next or past full hour
    start_diff_to_next_full_hour = diff_round_up_to_full_hour(start) - start
    end_diff_to_past_full_hour = end - diff_round_down_to_full_hour(end)

    if start_diff_to_next_full_hour.seconds != 0:
        # start is not on full hour, yield interval from start to first full hour
        yield start, start + start_diff_to_next_full_hour
        start = start + start_diff_to_next_full_hour

    original_end = end
    if end_diff_to_past_full_hour.seconds != 0:
        # end is not on full hour
        full_hour_end = end - end_diff_to_past_full_hour
        end = end - end_diff_to_past_full_hour
    else:
        full_hour_end = end

    # yield all full-hour intervals
    for n in range(int((end - start).total_seconds() / 3600)):
        yield start + timedelta(seconds=n * 3600), start + timedelta(
            seconds=((n + 1) * 3600) - 1
        )

    if original_end != full_hour_end:
        # if end is not on full hour, yield the interval between the last full hour and the end
        yield full_hour_end, original_end - timedelta(seconds=1)


class DownloadFailed(Exception):
    pass


class ProtectClient(object):
    def __init__(
        self,
        address: str = "unifi",
        port: int = 7443,
        username: str = None,
        password: str = None,
        verify_ssl: bool = False,
        ignore_failed_downloads: bool = False,
        download_wait: int = 0,
        use_subfolders: bool = False,
        skip_existing_files: bool = False,
        destination_path: str = None,
        touch_files: bool = False,
        download_timeout: int = 60,
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

        self.max_downloads_with_auth = 10
        self.max_downloads_with_key = 3

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
            print(
                f"Authentication as user {username} failed with status {response.status_code} {response.reason}"
            )
            self.print_download_stats()
            exit(2)
        print(f"Successfully authenticated as user {self.username}")
        authorization_header = response.headers["Authorization"]
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
            print(
                f"Failed to get access key from API. {response.status_code} {response.reason}"
            )
            self.print_download_stats()
            exit(3)

        print("Successfully requested API Access Key")
        json_response = response.json()
        access_key = json_response["accessKey"]
        return access_key

    def get_api_token(self) -> str:
        # use the same api token (login session) for set number of downloads only (default: 10)
        if self._downloads_with_current_token == int(self.max_downloads_with_auth):
            print(
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

    def get_access_key(self, api_token: str = None) -> str:
        # use the same access key for set number of downloads only (default: 3)
        if self._downloads_with_current_access_key == self.max_downloads_with_key:
            print(
                f"Access Key has been used for {self._downloads_with_current_access_key} download(s) - requesting new access key..."
            )
            self._access_key = None

        if self._access_key is None:
            # request new access key
            self._access_key = self.fetch_access_key(api_token or self._api_token)
            self._downloads_with_current_access_key = 0

        return self._access_key

    # file downloader
    def download_file(self, uri: str, file_name: str):
        for retry_num in range(self.max_retries):
            self._downloads_with_current_token += 1
            self._downloads_with_current_access_key += 1

            # make the GET request to retrieve the video file or snapshot
            try:
                response = requests.get(
                    uri, verify=self.verify_ssl, timeout=self.download_timeout
                )

                # write file to disk if response.status_code is 200,
                # otherwise log error and then either exit or skip the download
                if response.status_code == 200:
                    with open(file_name, "wb") as fp:
                        fp.write(response.content)
                    print("Download successful \n")
                    self.files_downloaded += 1
                else:
                    raise DownloadFailed(
                        f"Download failed with status {response.status_code} {response.reason}"
                    )

            except requests.exceptions.RequestException as request_exception:
                print(f"Download failed: {request_exception}\n")
                exit_code = 5
            except DownloadFailed as exc:
                print(
                    f"Download failed with status {response.status_code} {response.reason}\n"
                )
                exit_code = 4
            else:
                return

            print("Retrying...")

        if not self.ignore_failed_downloads:
            print(
                "To skip failed downloads and continue with next file, add argument '--ignore-failed-downloads'"
            )
            self.print_download_stats()
            exit(exit_code)
        else:
            print(
                "Argument '--ignore-failed-downloads' is present, continue downloading files..."
            )
            self.files_skipped += 1

    def print_download_stats(self):
        files_total = self.files_downloaded + self.files_skipped
        print(
            f"{self.files_downloaded} files downloaded, {self.files_skipped} files skipped, {files_total} files total"
        )

    # get camera list
    def get_camera_list(self) -> List[Mapping]:
        bootstrap_uri = f"https://{self.address}:{self.port}/api/bootstrap"
        response = requests.get(
            bootstrap_uri,
            headers={"Authorization": "Bearer " + self.get_api_token()},
            verify=self.verify_ssl,
        )
        if response.status_code != 200:
            return []

        print("Successfully retrieved data from /api/bootstrap")
        json_response = response.json()
        cameras = json_response["cameras"]

        print("Cameras found:")
        camera_list = []
        for camera in cameras:
            print(f"{camera['name']} ({camera['id']})")
            camera_list.append({"name": str(camera["name"]), "id": str(camera["id"])})

        return camera_list

    def download_footage(
        self, start: datetime, end: datetime, camera_id: str, camera_name: str
    ):
        # make camera name safe for use in file name
        # TODO(dcramer): It'd be nice to map this to something similar to what the UI gives you (somewhat more readable)
        camera_name_fs_safe = (
            "".join([c for c in camera_name if c.isalpha() or c.isdigit() or c == " "])
            .rstrip()
            .replace(" ", "_")
            + "_"
            + str(camera_id)[-4:]
        )

        print(f"Downloading footage for camera '{camera_name}' ({camera_id})")

        # split requested time frame into chunks of 1 hour or less and download them one by one
        for interval_start, interval_end in calculate_intervals(start, end):
            # wait n seconds before starting next download (if parameter is set)
            if self.download_wait != 0 and self.total_downloads == 0:
                print(
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
                    print(f"Created path {target_with_date_and_name}")
                    download_dir = target_with_date_and_name
            else:
                download_dir = self.destination_path

            # file name for download
            filename_timestamp_start = interval_start.strftime("%Y-%m-%d--%H-%M-%S%z")
            filename_timestamp_end = interval_end.strftime("%Y-%m-%d--%H-%M-%S%z")
            filename_timestamp = f"{filename_timestamp_start}_{filename_timestamp_end}"
            filename = f"{download_dir}/{camera_name_fs_safe}_{filename_timestamp}.mp4"

            print(
                f"Downloading video for time range {interval_start} - {interval_end} to {filename}"
            )

            # skip downloading files that already exist on disk if argument --skip-existing-files is present
            # TODO(dcramer): sanity check on filesize would be valuable here
            if bool(self.skip_existing_files) and path.exists(filename):
                print(
                    "File already exists on disk and argument '--skip-existing-files' is present - skipping download \n"
                )
                self.files_skipped += 1
                continue

            # create file without content if argument --touch-files is present
            # XXX(dcramer): would be nice to document why you'd ever want this
            if bool(self.touch_files) and not path.exists(filename):
                print(
                    f"Argument '--touch-files' is present. Creating file at {filename}"
                )
                open(filename, "a").close()

            # build video export API address
            address = f"https://{self.address}:{self.port}/api/video/export?accessKey={self.get_access_key()}&camera={camera_id}&start={js_timestamp_range_start}&end={js_timestamp_range_end}"

            # download the file
            self.download_file(address, filename)

    def download_snapshot(self, start: datetime, camera_id: str, camera_name: str):
        # make camera name safe for use in file name
        camera_name_fs_safe = (
            "".join([c for c in camera_name if c.isalpha() or c.isdigit() or c == " "])
            .rstrip()
            .replace(" ", "_")
            + "_"
            + str(camera_id)[-4:]
        )

        print(f"Downloading snapshot for camera '{camera_name}' ({camera_id})")

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
                print(f"Created path {target_with_date_and_name}")
                download_dir = target_with_date_and_name
        else:
            download_dir = self.destination_path

        # file name for download
        filename_timestamp = start.strftime("%Y-%m-%d--%H-%M-%S%z")
        filename = f"{download_dir}/{camera_name_fs_safe}_{filename_timestamp}.jpg"

        print(f"Downloading snapshot for time {start} to {filename}")

        # create file without content if argument --touch-files is present
        if bool(self.touch_files) and not path.exists(filename):
            print(f"Argument '--touch-files' is present. Creating file at {filename}")
            open(filename, "a").close()

        js_timestamp_start = int(start.timestamp()) * 1000
        # build snapshot export API address
        address = f"https://{self.address}:{self.port}/api/cameras/{camera_id}/snapshot?accessKey={self.get_access_key()}&ts={js_timestamp_start}"

        # download the file
        self.download_file(address, filename)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to download footage from a local UniFi Protect system"
    )
    parser.add_argument(
        "--address",
        default="unifi",
        type=str,
        dest="address",
        help="CloudKey IP address or hostname",
    )
    parser.add_argument(
        "--port",
        default="7443",
        type=str,
        dest="port",
        help="UniFi Protect service port",
    )
    parser.add_argument(
        "--verify-ssl",
        default=False,
        action="store_true",
        dest="verify_ssl",
        help="Verify CloudKey SSL certificate",
    )
    parser.add_argument(
        "--username",
        default="ubnt",
        type=str,
        dest="username",
        help="Username of user with local access",
    )
    parser.add_argument(
        "--password",
        default=None,
        type=str,
        required=True,
        dest="password",
        help="Password of user with local access",
    )
    parser.add_argument(
        "--cameras",
        default="all",
        type=str,
        dest="camera_ids",
        help="Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        + "Use '--cameras=all' to download footage of all available cameras.",
    )
    parser.add_argument(
        "--channel", default=0, type=str, required=False, dest="channel", help="Channel"
    )
    parser.add_argument(
        "--start",
        default=None,
        type=str,
        required=False,
        dest="start",
        help='Start time in dateutil.parser compatible format, for example "YYYY-MM-DD HH:MM:SS+0000"',
    )
    parser.add_argument(
        "--end",
        default=None,
        type=str,
        required=False,
        dest="end",
        help='End time in dateutil.parser compatible format, for example "YYYY-MM-DD HH:MM:SS+0000"',
    )
    parser.add_argument(
        "--dest",
        default="./",
        type=str,
        required=False,
        dest="destination_path",
        help="Destination directory path",
    )
    parser.add_argument(
        "--wait-between-downloads",
        default=0,
        type=int,
        required=False,
        dest="download_wait",
        help="Time to wait between file downloads, in seconds (Default: 0)",
    )
    parser.add_argument(
        "--downloads-before-key-refresh",
        default=3,
        type=int,
        required=False,
        dest="max_downloads_with_key",
        help="Maximum number of downloads with the same API Access Key (Default: 3)",
    )
    parser.add_argument(
        "--downloads-before-auth-refresh",
        default=10,
        type=int,
        required=False,
        dest="max_downloads_with_auth",
        help="Maximum number of downloads with the same API Authentication Token (Default: 10)",
    )
    parser.add_argument(
        "--ignore-failed-downloads",
        action="store_true",
        required=False,
        dest="ignore_failed_downloads",
        default=False,
        help="Ignore failed downloads and continue with next download (Default: False)",
    )
    parser.add_argument(
        "--skip-existing-files",
        action="store_true",
        required=False,
        dest="skip_existing_files",
        help="Skip downloading files which already exist on disk (Default: False)",
    )
    parser.add_argument(
        "--touch-files",
        action="store_true",
        required=False,
        dest="touch_files",
        help="Create local file without content for current download (Default: False) - "
        "useful in combination with '--skip-existing-files' to skip problematic segments",
    )
    parser.add_argument(
        "--use-subfolders",
        action="store_true",
        required=False,
        dest="use_subfolders",
        help="Save footage to folder structure with format 'YYYY/MM/DD/camera_name/' (Default: False)",
    )
    parser.add_argument(
        "--download-request-timeout",
        default=60,
        type=int,
        required=False,
        dest="download_timeout",
        help="Time to wait before aborting download request, in seconds (Default: 60)",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        required=False,
        dest="create_snapshot",
        help="Capture and download a snapshot from the specified camera(s)",
    )

    args = parser.parse_args()

    # check the provided command line arguments
    if not (args.create_snapshot or (args.start and args.end)):
        print(
            "Please use the --snapshot option, or provide --start and --end timestamps"
        )
        exit(6)

    if args.create_snapshot:
        if args.start or args.end:
            print(
                "The arguments --start and --end are ignored when using the --snapshot option"
            )
        start = datetime.now()

    # normalize path to destination directory and check if it exists
    destination_path = path.abspath(args.destination_path)
    if not path.isdir(destination_path):
        print(
            f"Video file destination directory '{destination_path} is invalid or does not exist!"
        )
        exit(1)

    if not args.create_snapshot:
        # parse date and time from '--start' and '--end' command line arguments
        start = dateutil.parser.parse(args.start).replace(minute=0, second=0)
        end = dateutil.parser.parse(args.end).replace(minute=0, second=0)

    # disable InsecureRequestWarning for unverified HTTPS requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = ProtectClient(
        address=args.address,
        port=args.port,
        username=args.username,
        password=args.password,
        verify_ssl=args.verify_ssl,
        ignore_failed_downloads=args.ignore_failed_downloads,
        destination_path=destination_path,
        use_subfolders=args.use_subfolders,
        download_wait=args.download_wait,
        skip_existing_files=args.skip_existing_files,
        touch_files=args.touch_files,
        download_timeout=args.download_timeout,
    )

    # get camera list
    print("Getting camera list")
    camera_list = client.get_camera_list()

    if not args.create_snapshot:
        # noinspection PyUnboundLocalVariable
        print(
            f"Downloading video files between {start} and {end}"
            f" from 'https://{args.address}:{args.port}/api/video/export' \n"
        )

        if args.camera_ids == "all":
            for api_camera in camera_list:
                client.download_footage(
                    start, end, api_camera["id"], api_camera["name"]
                )
        else:
            args_camera_ids = args.camera_ids.split(",")
            for args_camera_id in args_camera_ids:
                for api_camera in camera_list:
                    if args_camera_id == api_camera["id"]:
                        client.download_footage(
                            start, end, api_camera["id"], api_camera["name"]
                        )
    else:
        print(
            f"Downloading snapshot files for {start}"
            f" from 'https://{args.address}:{args.port}/api/cameras/{args.camera_ids}/snapshot' \n"
        )

        if args.camera_ids == "all":
            for api_camera in camera_list:
                client.download_snapshot(start, api_camera["id"], api_camera["name"])
        else:
            args_camera_ids = args.camera_ids.split(",")
            for args_camera_id in args_camera_ids:
                for api_camera in camera_list:
                    if args_camera_id == api_camera["id"]:
                        client.download_snapshot(
                            start, api_camera["id"], api_camera["name"]
                        )

    client.print_download_stats()


if __name__ == "__main__":
    main()
