import logging
import os
from datetime import datetime

from protect_archiver.dataclasses import Camera
from protect_archiver.downloader.download_file import download_file
from protect_archiver.utils import make_camera_name_fs_safe


def download_snapshot(client, start: datetime, camera: Camera):
    # make camera name safe for use in file name
    camera_name_fs_safe = make_camera_name_fs_safe(camera)

    # file path for download
    if bool(client.use_subfolders):
        folder_year = start.strftime("%Y")
        folder_month = start.strftime("%m")
        folder_day = start.strftime("%d")

        dir_by_date_and_name = (
            f"{folder_year}/{folder_month}/{folder_day}/{camera_name_fs_safe}"
        )
        target_with_date_and_name = f"{client.destination_path}/{dir_by_date_and_name}"

        download_dir = target_with_date_and_name
        if not os.path.isdir(target_with_date_and_name):
            os.makedirs(target_with_date_and_name, exist_ok=True)
            logging.info(f"Created path {target_with_date_and_name}")
            download_dir = target_with_date_and_name
    else:
        download_dir = client.destination_path

    # file name for download
    filename_timestamp = start.strftime("%Y-%m-%d - %H.%M.%S%z")
    filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.jpg"

    logging.info(
        f"Downloading snapshot for camera '{camera.name}' ({camera.id}) at {start.ctime()} to {filename}"
    )

    # create file without content if argument --touch-files is present
    if bool(client.touch_files) and not os.path.exists(filename):
        logging.debug(
            f"Argument '--touch-files' is present. Creating file at {filename}"
        )
        open(filename, "a").close()

    js_timestamp_start = int(start.timestamp()) * 1000

    # build snapshot export API address
    snapshot_export_query = f"/cameras/{camera.id}/snapshot?ts={js_timestamp_start}"

    # download the file
    download_file(client, snapshot_export_query, filename)
