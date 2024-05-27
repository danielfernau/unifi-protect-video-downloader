import logging
import time

from datetime import datetime
from datetime import timezone
from os import path
from typing import Any

from protect_archiver.dataclasses import Camera
from protect_archiver.downloader.download_file import download_file
from protect_archiver.utils import build_download_dir
from protect_archiver.utils import calculate_intervals
from protect_archiver.utils import make_camera_name_fs_safe


def download_footage(
    client: Any,
    start: datetime,
    end: datetime,
    camera: Camera,
    disable_alignment: bool = False,
    disable_splitting: bool = False,
) -> None:
    # make camera name safe for use in file name
    camera_name_fs_safe = make_camera_name_fs_safe(camera)

    logging.info(f"Downloading footage for camera '{camera.name}' ({camera.id})")

    # split requested time frame into chunks of 1 hour or less and download them one by one
    for interval_start, interval_end in calculate_intervals(
        start,
        end,
        disable_alignment,
        disable_splitting,
    ):
        # wait n seconds before starting next download (if parameter is set)
        if client.download_wait != 0 and client.files_downloaded == 0:
            logging.debug(
                "Command line argument '--wait-between-downloads' is set to"
                f" {client.download_wait} second(s)... \n"
            )
            time.sleep(int(client.download_wait))

        # start and end time of the video segment to be downloaded
        js_timestamp_range_start = int(interval_start.timestamp() * 1e3)
        js_timestamp_range_end = int(interval_end.timestamp() * 1e3)

        # support selection between local time zone and UTC for file names
        interval_start_tz = (
            interval_start.astimezone(timezone.utc) if client.use_utc_filenames else interval_start
        )

        download_dir = build_download_dir(
            use_subfolders=client.use_subfolders,
            destination_path=client.destination_path,
            interval_start_tz=interval_start_tz,
            camera_name_fs_safe=camera_name_fs_safe,
        )

        # file name for download
        filename_timestamp = interval_start_tz.strftime("%Y-%m-%d - %H.%M.%S%z")
        filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.mp4"

        logging.info(
            f"Downloading video for time range {interval_start} - {interval_end} to {filename}"
        )

        # create file without content if argument --touch-files is present
        # XXX(dcramer): would be nice to document why you'd ever want this
        if bool(client.touch_files) and not path.exists(filename):
            logging.debug(f"Argument '--touch-files' is present. Creating file at {filename}")
            open(filename, "a").close()

        # build video export query
        video_export_query = f"/video/export?camera={camera.id}&start={js_timestamp_range_start}&end={js_timestamp_range_end}"

        # download the file
        download_file(client, video_export_query, filename)
