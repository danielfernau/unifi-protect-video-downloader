#!/usr/bin/env python

import argparse
import logging

from datetime import datetime
from os import path

import urllib3

from .sync import ProtectSync
from .client import ProtectClient, ProtectError

# disable InsecureRequestWarning for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(format="%(message)s", level=logging.INFO)


def add_client_options(parser):
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
        default=True,
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


def get_client(args):
    return ProtectClient(
        address=args.address,
        port=args.port,
        username=args.username,
        password=args.password,
        verify_ssl=args.verify_ssl,
        ignore_failed_downloads=args.ignore_failed_downloads,
        destination_path=args.destination_path,
        use_subfolders=args.use_subfolders,
        download_wait=args.download_wait,
        skip_existing_files=args.skip_existing_files,
        touch_files=args.touch_files,
        download_timeout=args.download_timeout,
        max_downloads_with_auth=args.max_downloads_with_auth,
        max_downloads_with_key=args.max_downloads_with_key,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Tool to download footage from a local UniFi Protect system"
    )
    add_client_options(parser)
    parser.add_argument(
        "--cameras",
        default="all",
        type=str,
        dest="camera_ids",
        help="Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        + "Use '--cameras=all' to download footage of all available cameras.",
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
        "--snapshot",
        action="store_true",
        required=False,
        dest="create_snapshot",
        help="Capture and download a snapshot from the specified camera(s)",
    )

    args = parser.parse_args()

    # check the provided command line arguments
    if not (args.create_snapshot or (args.start and args.end)):
        print("Please use --snapshot, or provide --start and --end timestamps")
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

    # disable InsecureRequestWarning for unverified HTTPS requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    client = get_client(args)

    # get camera list
    print("Getting camera list")
    camera_list = client.get_camera_list()

    if args.camera_ids != "all":
        camera_ids = set(args.camera_ids.split(","))
        camera_list = [c for c in camera_list if c["id"] in camera_ids]

    if not args.create_snapshot:
        # noinspection PyUnboundLocalVariable
        print(
            f"Downloading video files between {start} and {end}"
            f" from 'https://{args.address}:{args.port}/api/video/export' \n"
        )

        for camera in camera_list:
            client.download_footage(start, end, camera)
    else:
        print(
            f"Downloading snapshot files for {start}"
            f" from 'https://{args.address}:{args.port}/api/cameras/{args.camera_ids}/snapshot' \n"
        )
        for camera in camera_list:
            client.download_snapshot(start, camera)

    client.print_download_stats()


def sync():
    parser = argparse.ArgumentParser(
        description="Tool to download footage from a local UniFi Protect system"
    )
    add_client_options(parser)
    parser.add_argument(
        "--statefile", default="sync.state", type=str,
    )
    parser.add_argument(
        "--ignore-state", default=False, action="store_true",
    )
    parser.add_argument(
        "--cameras",
        default="all",
        type=str,
        dest="camera_ids",
        help="Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        + "Use '--cameras=all' to download footage of all available cameras.",
    )
    args = parser.parse_args()

    # normalize path to destination directory and check if it exists
    destination_path = path.abspath(args.destination_path)
    if not path.isdir(destination_path):
        print(
            f"Video file destination directory '{destination_path} is invalid or does not exist!"
        )
        exit(1)

    client = get_client(args)

    # get camera list
    print("Getting camera list")
    camera_list = client.get_camera_list()

    if args.camera_ids != "all":
        camera_ids = set(args.camera_ids.split(","))
        camera_list = [c for c in camera_list if c["id"] in camera_ids]

    process = ProtectSync(
        client=client, destination_path=destination_path, statefile=args.statefile
    )
    process.run(camera_list, ignore_state=args.ignore_state)

    client.print_download_stats()


if __name__ == "__main__":
    try:
        main()
    except ProtectError as e:
        exit(e.code)
