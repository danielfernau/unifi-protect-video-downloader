import logging
import os

from datetime import datetime

from protect_archiver.dataclasses import MotionEvent, Camera


def download_snapshot(self, start: datetime, camera: Camera):
    # make camera name safe for use in file name
    camera_name_fs_safe = (
        "".join(
            [c for c in camera.name if c.isalpha() or c.isdigit() or c == " "]
        ).rstrip()
        + f" ({str(camera.id)[-4:]})"
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
        target_with_date_and_name = f"{self.destination_path}/{dir_by_date_and_name}"

        download_dir = target_with_date_and_name
        if not os.path.isdir(target_with_date_and_name):
            os.makedirs(target_with_date_and_name, exist_ok=True)
            logging.info(f"Created path {target_with_date_and_name}")
            download_dir = target_with_date_and_name
    else:
        download_dir = self.destination_path

    # file name for download
    filename_timestamp = start.strftime("%Y-%m-%d - %H.%M.%S%z")
    filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.jpg"

    logging.info(f"Downloading snapshot for time {start} to {filename}")

    # create file without content if argument --touch-files is present
    if bool(self.touch_files) and not path.exists(filename):
        logging.debug(
            f"Argument '--touch-files' is present. Creating file at {filename}"
        )
        open(filename, "a").close()

    js_timestamp_start = int(start.timestamp()) * 1000
    # build snapshot export API address
    address = f"https://{self.address}:{self.port}/api/cameras/{camera.id}/snapshot?ts={js_timestamp_start}"

    # download the file
    self.download_file(address, filename)
