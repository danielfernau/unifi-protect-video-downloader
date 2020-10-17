import logging
import os
import time

from protect_archiver.dataclasses import Camera
from protect_archiver.utils import calculate_intervals


def download_footage(self, start: datetime, end: datetime, camera: Camera):
    # make camera name safe for use in file name
    camera_name_fs_safe = (
        "".join(
            [c for c in camera.name if c.isalpha() or c.isdigit() or c == " "]
        ).rstrip()
        + f" ({str(camera.id)[-4:]})"
    )

    logging.info(f"Downloading footage for camera '{camera.name}' ({camera.id})")

    # split requested time frame into chunks of 1 hour or less and download them one by one
    for interval_start, interval_end in calculate_intervals(start, end):
        # wait n seconds before starting next download (if parameter is set)
        if self.download_wait != 0 and self.files_downloaded == 0:
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
            if not os.path.isdir(target_with_date_and_name):
                os.makedirs(target_with_date_and_name, exist_ok=True)
                logging.info(f"Created path {target_with_date_and_name}")
                download_dir = target_with_date_and_name
        else:
            download_dir = self.destination_path

        # file name for download
        filename_timestamp = interval_start.strftime("%Y-%m-%d - %H.%M.%S%z")
        filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.mp4"

        logging.info(
            f"Downloading video for time range {interval_start} - {interval_end} to {filename}"
        )

        # create file without content if argument --touch-files is present
        # XXX(dcramer): would be nice to document why you'd ever want this
        if bool(self.touch_files) and not path.exists(filename):
            logging.debug(
                f"Argument '--touch-files' is present. Creating file at {filename}"
            )
            open(filename, "a").close()

        # build video export API address
        address = f"https://{self.address}:{self.port}/api/video/export?&camera={camera.id}" \
                  f"&start={js_timestamp_range_start}&end={js_timestamp_range_end}"

        # download the file
        self.download_file(address, filename)
