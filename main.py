#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

""" Tool to download footage within a given time range from a local UniFi Protect system """

import argparse
import datetime
import dateutil.parser
import time
from os import path, makedirs
import requests
import urllib3

__author__ = "Daniel Fernau"
__copyright__ = "Copyright 2019, Daniel Fernau"
__license__ = "GPLv3"
__version__ = "1.1.1"


parser = argparse.ArgumentParser(description='Tool to download footage from a local UniFi Protect system')
parser.add_argument("--address", default=None, type=str, required=True, dest="address",
                    help="CloudKey IP address or hostname")
parser.add_argument("--port", default="7443", type=str, required=False, dest="port",
                    help="UniFi Protect service port")
parser.add_argument("--verify-ssl", default=False, action='store_true', required=False, dest="verify_ssl",
                    help="Verify CloudKey SSL certificate")
parser.add_argument("--username", default=None, type=str, required=True, dest="username",
                    help="Username of user with local access")
parser.add_argument("--password", default=None, type=str, required=True, dest="password",
                    help="Password of user with local access")
parser.add_argument("--cameras", default=None, type=str, required=True, dest="camera_ids",
                    help="Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). " +
                         "Use '--cameras=all' to download footage of all available cameras.")
parser.add_argument("--channel", default=0, type=str, required=False, dest="channel",
                    help="Channel")
parser.add_argument("--start", default=None, type=str, required=False, dest="start",
                    help="Start time in dateutil.parser compatible format, for example \"YYYY-MM-DD HH:MM:SS+0000\"")
parser.add_argument("--end", default=None, type=str, required=False, dest="end",
                    help="End time in dateutil.parser compatible format, for example \"YYYY-MM-DD HH:MM:SS+0000\"")
parser.add_argument("--dest", default="./", type=str, required=False, dest="destination_path",
                    help="Destination directory path")
parser.add_argument("--wait-between-downloads", default=0, type=int, required=False, dest="download_wait",
                    help="Time to wait between file downloads, in seconds (Default: 0)")
parser.add_argument("--downloads-before-key-refresh", default=3, type=int, required=False,
                    dest="max_downloads_with_key",
                    help="Maximum number of downloads with the same API Access Key (Default: 3)")
parser.add_argument("--downloads-before-auth-refresh", default=10, type=int, required=False,
                    dest="max_downloads_with_auth",
                    help="Maximum number of downloads with the same API Authentication Token (Default: 10)")
parser.add_argument("--ignore-failed-downloads", action='store_true', required=False,
                    dest="ignore_failed_downloads",
                    help="Ignore failed downloads and continue with next download (Default: False)")
parser.add_argument("--skip-existing-files", action='store_true', required=False,
                    dest="skip_existing_files",
                    help="Skip downloading files which already exist on disk (Default: False)")
parser.add_argument("--touch-files", action='store_true', required=False,
                    dest="touch_files",
                    help="Create local file without content for current download (Default: False) - "
                         "useful in combination with '--skip-existing-files' to skip problematic segments")
parser.add_argument("--use-subfolders", action='store_true', required=False,
                    dest="use_subfolders",
                    help="Save footage to folder structure with format 'YYYY/MM/DD/camera_name/' (Default: False)")
parser.add_argument("--download-request-timeout", default=60, type=int, required=False,
                    dest="download_timeout",
                    help="Time to wait before aborting download request, in seconds (Default: 60)")
parser.add_argument("--snapshot", action='store_true', required=False,
                    dest="create_snapshot",
                    help="Capture and download a snapshot from the specified camera(s)")

args = parser.parse_args()

# check the provided command line arguments
if not (args.create_snapshot or (args.start and args.end)):
    print("Please use the --snapshot option, or provide --start and --end timestamps")
    exit(6)

if args.create_snapshot:
    if args.start or args.end:
        print("The arguments --start and --end are ignored when using the --snapshot option")
    date_time_obj_start = datetime.datetime.now()
    js_timestamp_start = int(date_time_obj_start.timestamp()) * 1000

# normalize path to destination directory and check if it exists
target_dir = path.abspath(args.destination_path)
if not path.isdir(target_dir):
    print("Video file destination directory '" + str(target_dir) + "' is invalid or does not exist!")
    exit(1)

if not args.create_snapshot:
    # parse date and time from '--start' and '--end' command line arguments
    date_time_obj_start = dateutil.parser.parse(args.start)
    js_timestamp_start = int(date_time_obj_start.timestamp()) * 1000

    date_time_obj_end = dateutil.parser.parse(args.end)
    js_timestamp_end = int(date_time_obj_end.timestamp()) * 1000

# disable InsecureRequestWarning for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# API Authentication
# get bearer token using username and password of local user
def get_api_auth_bearer_token(username, password):
    auth_uri = "https://" + str(args.address) + ":" + str(args.port) + "/api/auth"
    response = requests.post(auth_uri, json={"username": username, "password": password}, verify=args.verify_ssl)
    if response.status_code == 200:
        print("Successfully authenticated as user " + str(username))
        authorization_header = response.headers['Authorization']
        return authorization_header
    else:
        print("Authentication as user " + str(username) + " failed with status " +
              str(response.status_code) + " " + str(response.reason))
        print_download_stats()
        exit(2)


# get access key using bearer token
def get_api_access_key(bearer_token):
    access_key_uri = "https://" + str(args.address) + ":" + str(args.port) + "/api/auth/access-key"
    response = requests.post(access_key_uri, headers={'Authorization': 'Bearer ' + bearer_token},
                             verify=args.verify_ssl)
    if response.status_code == 200:
        print("Successfully requested API Access Key")
        json_response = response.json()
        access_key = json_response['accessKey']
        return access_key
    else:
        print("Failed to get access key from API. " + str(response.status_code) + " " + str(response.reason))
        print_download_stats()
        exit(3)


# get camera list
def get_camera_list(bearer_token):
    bootstrap_uri = "https://" + str(args.address) + ":" + str(args.port) + "/api/bootstrap"
    response = requests.get(bootstrap_uri, headers={'Authorization': 'Bearer ' + bearer_token}, verify=args.verify_ssl)
    if response.status_code == 200:
        print("Successfully retrieved data from /api/bootstrap")
        json_response = response.json()
        cameras = json_response['cameras']

        print("Cameras found:")
        camera_list = []
        for camera in cameras:
            print(str(camera['name']) + " (" + str(camera['id']) + ")")
            camera_list.append({"name": str(camera['name']), "id": str(camera['id'])})

        return camera_list


# file downloader
def download_file(uri, file_name):
    global files_downloaded, files_skipped

    # make the GET request to retrieve the video file or snapshot
    try:
        response = requests.get(uri, verify=args.verify_ssl, timeout=args.download_timeout)

        # write file to disk if response.status_code is 200,
        # otherwise log error and then either exit or skip the download
        if response.status_code == 200:
            with open(file_name, "wb") as file:
                file.write(response.content)
                print("Download successful \n")
                files_downloaded += 1
        else:
            print("Download failed with status " + str(response.status_code) + " " + str(response.reason) + "\n")
            if not bool(args.ignore_failed_downloads):
                print("To skip failed downloads and continue with next file, add argument '--ignore-failed-downloads'")
                print_download_stats()
                exit(4)
            else:
                print("Argument '--ignore-failed-downloads' is present, continue downloading files...")
                files_skipped += 1

    except requests.exceptions.RequestException as request_exception:
        print("Download failed: " + str(request_exception) + "\n")
        print_download_stats()
        exit(5)


def print_download_stats():
    global files_downloaded, files_skipped
    files_total = files_downloaded + files_skipped
    print(str(files_downloaded) + " files downloaded, " +
          str(files_skipped) + " files skipped, " +
          str(files_total) + " files total")


# return time difference between given date_time_object and next full hour
def diff_round_up_to_full_hour(date_time_object):
    if date_time_object.minute != 0 or date_time_object.second != 0:
        return date_time_object.replace(second=0, microsecond=0, minute=0, hour=date_time_object.hour) + \
               datetime.timedelta(hours=1, minutes=0)
    else:
        return date_time_object.replace(second=0, microsecond=0, minute=0, hour=date_time_object.hour) + \
               datetime.timedelta(hours=0, minutes=0)


# return time difference between given date_time_object and past full hour
def diff_round_down_to_full_hour(date_time_object):
    return date_time_object.replace(second=0, microsecond=0, minute=0, hour=date_time_object.hour) + \
           datetime.timedelta(hours=0, minutes=0)


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
        yield start + datetime.timedelta(seconds=n * 3600), start + datetime.timedelta(seconds=((n + 1) * 3600) - 1)

    if original_end != full_hour_end:
        # if end is not on full hour, yield the interval between the last full hour and the end
        yield full_hour_end, original_end - datetime.timedelta(seconds=1)


def download_footage(camera_id, camera_name):
    global api_auth_bearer_token, api_access_key
    global first_download, downloads_with_current_api_auth, downloads_with_current_api_key
    global files_downloaded, files_skipped
    global target_dir

    # make camera name safe for use in file name
    camera_name_fs_safe = "".join(
        [c for c in camera_name if c.isalpha() or c.isdigit() or c == ' ']
    ).rstrip().replace(" ", "_") + "_" + str(camera_id)[-4:]

    print("Downloading footage for camera '" + str(camera_name) + "' (" + str(camera_id) + ")")

    # split requested time frame into chunks of 1 hour or less and download them one by one
    for date_time_interval_start, date_time_interval_end in calculate_intervals(date_time_obj_start, date_time_obj_end):
        # wait n seconds before starting next download (if parameter is set)
        if int(args.download_wait) != 0 and not first_download:
            print("Command line argument '--wait-between-downloads' is set to " + str(args.download_wait) +
                  " second(s)... \n")
            time.sleep(int(args.download_wait))

        # start and end time of the video segment to be downloaded
        js_timestamp_range_start = int(date_time_interval_start.timestamp()) * 1000
        js_timestamp_range_end = int(date_time_interval_end.timestamp()) * 1000

        # file path for download
        download_dir = target_dir
        if bool(args.use_subfolders):
            folder_year = date_time_interval_start.strftime("%Y")
            folder_month = date_time_interval_start.strftime("%m")
            folder_day = date_time_interval_start.strftime("%d")

            dir_by_date_and_name = folder_year + "/" + folder_month + "/" + folder_day + "/" + camera_name_fs_safe
            target_with_date_and_name = target_dir + "/" + dir_by_date_and_name

            download_dir = target_with_date_and_name
            if not path.isdir(target_with_date_and_name):
                makedirs(target_with_date_and_name, exist_ok=True)
                print("Created path " + str(target_with_date_and_name))
                download_dir = target_with_date_and_name

        # file name for download
        filename_timestamp_start = date_time_interval_start.strftime("%Y-%m-%d--%H-%M-%S%z")
        filename_timestamp_end = date_time_interval_end.strftime("%Y-%m-%d--%H-%M-%S%z")
        filename_timestamp = filename_timestamp_start + "_" + filename_timestamp_end
        filename = str(download_dir) + "/" + str(camera_name_fs_safe) + "_" + filename_timestamp + ".mp4"

        print("Downloading video for time range " +
              str(date_time_interval_start) + " - " + str(date_time_interval_end) + " to " + filename)

        # skip downloading files that already exist on disk if argument --skip-existing-files is present
        if bool(args.skip_existing_files) and path.exists(filename):
            print("File already exists on disk and argument '--skip-existing-files' is present - skipping download \n")
            files_skipped += 1
            continue

        # create file without content if argument --touch-files is present
        if bool(args.touch_files) and not path.exists(filename):
            print("Argument '--touch-files' is present. Creating file at " + str(filename))
            open(filename, 'a').close()

        # build video export API address
        address = "https://" + str(args.address) + ":" + str(args.port) + "/api/video/export?accessKey=" + \
                  str(api_access_key) + "&camera=" + str(camera_id) + \
                  "&start=" + str(js_timestamp_range_start) + "&end=" + str(js_timestamp_range_end)

        # download the file
        download_file(address, filename)
        first_download = False

        # use the same API Authentication Token (login session) for set number of downloads only (default: 10)
        if downloads_with_current_api_auth == int(args.max_downloads_with_auth):
            print("API Authentication Token has been used for " + str(downloads_with_current_api_auth) +
                  " download(s) - requesting new session token...")

            # get new API auth bearer token and access key
            api_auth_bearer_token = get_api_auth_bearer_token(str(args.username), str(args.password))
            api_access_key = get_api_access_key(api_auth_bearer_token)
            downloads_with_current_api_auth = 1
            downloads_with_current_api_key = 1
        else:
            print("API Authentication Token has been used for " + str(downloads_with_current_api_auth) +
                  " download(s). Maximum is set to " + str(args.max_downloads_with_auth) + ".")
            downloads_with_current_api_auth += 1

        # use the same API Access Key for set number of downloads only (default: 3)
        if downloads_with_current_api_key == int(args.max_downloads_with_key):
            print("API Access Key has been used for " + str(downloads_with_current_api_key) +
                  " download(s) - requesting new access key...")

            # request new access key
            api_access_key = get_api_access_key(api_auth_bearer_token)
            downloads_with_current_api_key = 1
        else:
            print("API Access Key has been used for " + str(downloads_with_current_api_key) +
                  " download(s). Maximum is set to " + str(args.max_downloads_with_key) + ".")
            downloads_with_current_api_key += 1


def download_snapshot(camera_id, camera_name):
    global api_auth_bearer_token, api_access_key
    global first_download, downloads_with_current_api_auth, downloads_with_current_api_key
    global first_download, files_skipped
    global target_dir

    # make camera name safe for use in file name
    camera_name_fs_safe = "".join(
        [c for c in camera_name if c.isalpha() or c.isdigit() or c == ' ']
    ).rstrip().replace(" ", "_") + "_" + str(camera_id)[-4:]

    print("Downloading snapshot for camera '" + str(camera_name) + "' (" + str(camera_id) + ")")

    # file path for download
    download_dir = target_dir
    if bool(args.use_subfolders):
        folder_year = date_time_obj_start.strftime("%Y")
        folder_month = date_time_obj_start.strftime("%m")
        folder_day = date_time_obj_start.strftime("%d")

        dir_by_date_and_name = folder_year + "/" + folder_month + "/" + folder_day + "/" + camera_name_fs_safe
        target_with_date_and_name = target_dir + "/" + dir_by_date_and_name

        download_dir = target_with_date_and_name
        if not path.isdir(target_with_date_and_name):
            makedirs(target_with_date_and_name, exist_ok=True)
            print("Created path " + str(target_with_date_and_name))
            download_dir = target_with_date_and_name

    # file name for download
    filename_timestamp = date_time_obj_start.strftime("%Y-%m-%d--%H-%M-%S%z")
    filename = str(download_dir) + "/" + str(camera_name_fs_safe) + "_" + filename_timestamp + ".jpg"

    print("Downloading snapshot for time " +
          str(date_time_obj_start) + " to " + filename)

    # create file without content if argument --touch-files is present
    if bool(args.touch_files) and not path.exists(filename):
        print("Argument '--touch-files' is present. Creating file at " + str(filename))
        open(filename, 'a').close()

    # build snapshot export API address
    address = "https://" + str(args.address) + ":" + str(args.port) + "/api/cameras/" + str(camera_id) + \
              "/snapshot?accessKey=" + str(api_access_key) + "&ts=" + str(js_timestamp_start)

    # download the file
    download_file(address, filename)
    first_download = False

    # use the same API Authentication Token (login session) for set number of downloads only (default: 10)
    if downloads_with_current_api_auth == int(args.max_downloads_with_auth):
        print("API Authentication Token has been used for " + str(downloads_with_current_api_auth) +
              " download(s) - requesting new session token...")

        # get new API auth bearer token and access key
        api_auth_bearer_token = get_api_auth_bearer_token(str(args.username), str(args.password))
        api_access_key = get_api_access_key(api_auth_bearer_token)
        downloads_with_current_api_auth = 1
        downloads_with_current_api_key = 1
    else:
        print("API Authentication Token has been used for " + str(downloads_with_current_api_auth) +
              " download(s). Maximum is set to " + str(args.max_downloads_with_auth) + ".")
        downloads_with_current_api_auth += 1

    # use the same API Access Key for set number of downloads only (default: 3)
    if downloads_with_current_api_key == int(args.max_downloads_with_key):
        print("API Access Key has been used for " + str(downloads_with_current_api_key) +
              " download(s) - requesting new access key...")

        # request new access key
        api_access_key = get_api_access_key(api_auth_bearer_token)
        downloads_with_current_api_key = 1
    else:
        print("API Access Key has been used for " + str(downloads_with_current_api_key) +
              " download(s). Maximum is set to " + str(args.max_downloads_with_key) + ".")
        downloads_with_current_api_key += 1


first_download = True
downloads_with_current_api_auth = 1
downloads_with_current_api_key = 1
files_downloaded = 0
files_skipped = 0

# get API auth bearer token
api_auth_bearer_token = get_api_auth_bearer_token(str(args.username), str(args.password))

# request access key
api_access_key = get_api_access_key(api_auth_bearer_token)

# get camera list
api_camera_list = get_camera_list(api_auth_bearer_token)

if not args.create_snapshot:
    # noinspection PyUnboundLocalVariable
    print("Downloading video files between " + str(date_time_obj_start) + " and " + str(date_time_obj_end) +
          " from 'https://" + str(args.address) + ":" + str(args.port) + "/api/video/export' \n")

    if args.camera_ids == 'all':
        for api_camera in api_camera_list:
            download_footage(api_camera['id'], api_camera['name'])
    else:
        args_camera_ids = (args.camera_ids.split(','))
        for args_camera_id in args_camera_ids:
            for api_camera in api_camera_list:
                if args_camera_id == api_camera['id']:
                    download_footage(api_camera['id'], api_camera['name'])
else:
    print("Downloading snapshot file(s) for " + str(date_time_obj_start) +
          " from 'https://" + str(args.address) + ":" + str(args.port) + "/api/cameras/{camera_id}/snapshot' \n")

    if args.camera_ids == 'all':
        for api_camera in api_camera_list:
            download_snapshot(api_camera['id'], api_camera['name'])
    else:
        args_camera_ids = (args.camera_ids.split(','))
        for args_camera_id in args_camera_ids:
            for api_camera in api_camera_list:
                if args_camera_id == api_camera['id']:
                    download_snapshot(api_camera['id'], api_camera['name'])

print_download_stats()
