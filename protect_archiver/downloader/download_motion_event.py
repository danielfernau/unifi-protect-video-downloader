import logging

from typing import Any

from protect_archiver.dataclasses import Camera
from protect_archiver.dataclasses import MotionEvent
from protect_archiver.downloader.download_file import download_file
from protect_archiver.utils import make_camera_name_fs_safe, build_download_dir


def download_motion_event(
    client: Any, motion_event: MotionEvent, camera: Camera, download_motion_heatmaps: bool
) -> None:
    # make camera name safe for use in file name
    camera_name_fs_safe = make_camera_name_fs_safe(camera)

    # start and end time of the video segment to be downloaded
    js_timestamp_start = int(motion_event.start.timestamp()) * 1000
    js_timestamp_end = int(motion_event.end.timestamp()) * 1000

    download_dir, interval_start_tz = build_download_dir(
        use_subfolders=client.use_subfolders,
        destination_path=client.destination_path,
        interval_start=motion_event.start,
        use_utc_filenames=client.use_utc_filenames,
        camera_name_fs_safe=camera_name_fs_safe,
    )

    # file name for download
    filename_timestamp = interval_start_tz.strftime("%Y-%m-%d - %H.%M.%S%z")
    filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.mp4"

    logging.info(
        f"Downloading motion event with ID '{motion_event.id[-4:]}' starting at"
        f" {motion_event.start.ctime()} ({int((motion_event.end - motion_event.start).total_seconds())}s"
        f" long) for camera '{camera.name}' ({camera.id}) to {filename}"
    )

    # build video export query
    video_export_query = (
        f"/video/export?camera={camera.id}&start={js_timestamp_start}&end={js_timestamp_end}"
    )

    # download the file
    download_file(client, video_export_query, filename)

    # download motion heatmap if enabled and event has heatmap available
    if download_motion_heatmaps and motion_event.heatmap_id:
        logging.info(f"Downloading heat map for motion event with ID '{motion_event.id[-4:]}'")

        heatmap_filename = f"{download_dir}/{camera_name_fs_safe} - {filename_timestamp}.pgm"
        heatmap_export_query = f"/heatmaps/{motion_event.heatmap_id}"
        download_file(client, heatmap_export_query, heatmap_filename)
