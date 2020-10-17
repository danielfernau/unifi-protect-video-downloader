import logging
import os

from protect_archiver.dataclasses import MotionEvent, Camera


def download_motion_event(
    self, motion_event: MotionEvent, camera: Camera, download_motion_heatmaps: bool
):
    # make camera name safe for use in file name
    camera_name_fs_safe = (
        "".join(
            [c for c in camera.name if c.isalpha() or c.isdigit() or c == " "]
        ).rstrip()
        + f" ({str(camera.id)[-4:]})"
    )

    # start and end time of the video segment to be downloaded
    js_timestamp_start = int(motion_event.start.timestamp()) * 1000
    js_timestamp_end = int(motion_event.end.timestamp()) * 1000

    # file path for download
    if bool(self.use_subfolders):
        folder_year = motion_event.start.strftime("%Y")
        folder_month = motion_event.start.strftime("%m")
        folder_day = motion_event.start.strftime("%d")

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
    filename_timestamp = motion_event.start.strftime("%Y-%m-%d - %H.%M.%S%z")
    filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.mp4"

    logging.info(
        f"Downloading motion event {motion_event.id[-4:]} at {motion_event.start} for camera '{camera.name}' "
        f"({camera.id}) to {filename}"
    )

    # build video export API address
    address = (
        f"https://{self.address}:{self.port}/api/video/export?&camera={camera.id}&start={js_timestamp_start}"
        f"&end={js_timestamp_end}"
    )

    # download the file
    self.download_file(address, filename)

    # download motion heatmap if enabled and event has heatmap available
    if download_motion_heatmaps and motion_event.heatmap_id:
        logging.info(f"Downloading heat map for motion event {motion_event.id[-4:]}")

        heatmap_filename = (
            f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.pgm"
        )
        heatmap_address = (
            f"https://{self.address}:{self.port}/api/heatmaps/{motion_event.heatmap_id}"
        )
        self.download_file(heatmap_address, heatmap_filename)
