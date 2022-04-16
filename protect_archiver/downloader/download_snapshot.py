import logging
import os

from datetime import datetime
from typing import Any

from protect_archiver.dataclasses import Camera
from protect_archiver.downloader.download_file import download_file
from protect_archiver.utils import build_download_dir
from protect_archiver.utils import make_camera_name_fs_safe


def download_snapshot(client: Any, start: datetime, camera: Camera) -> None:
    # make camera name safe for use in file name
    camera_name_fs_safe = make_camera_name_fs_safe(camera)

    download_dir, interval_start_tz = build_download_dir(
        use_subfolders=client.use_subfolders,
        destination_path=client.destination_path,
        interval_start=start,
        use_utc_filenames=client.use_utc_filenames,
        camera_name_fs_safe=camera_name_fs_safe,
    )

    # file name for download
    filename_timestamp = interval_start_tz.strftime("%Y-%m-%d - %H.%M.%S%z")
    filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.jpg"

    logging.info(
        f"Downloading snapshot for camera '{camera.name}' ({camera.id}) at {start.ctime()} to"
        f" {filename}"
    )

    # create file without content if argument --touch-files is present
    if bool(client.touch_files) and not os.path.exists(filename):
        logging.debug(f"Argument '--touch-files' is present. Creating file at {filename}")
        open(filename, "a").close()

    js_timestamp_start = int(start.timestamp()) * 1000

    # build snapshot export API address
    snapshot_export_query = f"/cameras/{camera.id}/snapshot?ts={js_timestamp_start}"

    # download the file
    download_file(client, snapshot_export_query, filename)
