from datetime import datetime

import click

from protect_archiver.cli.base import cli
from protect_archiver.client import ProtectClient
from protect_archiver.config import Config
from protect_archiver.downloader import Downloader
from protect_archiver.errors import Errors
from protect_archiver.utils import print_download_stats


@cli.command("events", help="Download event recordings from UniFi Protect to a local destination")
@click.argument("dest", type=click.Path(exists=True, writable=True, resolve_path=True))
@click.option(
    "--address",
    default=Config.ADDRESS,
    show_default=True,
    required=True,
    help="IP address or hostname of the UniFi Protect Server",
    envvar="PROTECT_ADDRESS",
    show_envvar=True,
)
@click.option(
    "--port",
    default=Config.PORT,
    show_default=True,
    required=False,
    help="The port of the UniFi Protect Server",
    envvar="PROTECT_PORT",
    show_envvar=True,
)
@click.option(
    "--not-unifi-os",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use this for systems without UniFi OS",
    envvar="PROTECT_NOT_UNIFI_OS",
    show_envvar=True,
)
@click.option(
    "--username",
    required=True,
    help="Username of user with local access",
    prompt="Username of local Protect user",
    envvar="PROTECT_USERNAME",
    show_envvar=True,
)
@click.option(
    "--password",
    required=True,
    help="Password of user with local access",
    prompt="Password for local Protect user",
    hide_input=True,
    envvar="PROTECT_PASSWORD",
    show_envvar=True,
)
@click.option(
    "--verify-ssl",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verify Protect SSL certificate",
    envvar="PROTECT_VERIFY_SSL",
    show_envvar=True,
)
@click.option(
    "--cameras",
    default="all",
    show_default=True,
    help=(
        "Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        "Use '--cameras=all' to download footage of all available cameras."
    ),
    envvar="PROTECT_CAMERAS",
    show_envvar=True,
)
@click.option(
    "--wait-between-downloads",
    "download_wait",
    default=0,
    show_default=True,
    help="Time to wait between file downloads, in seconds",
    envvar="PROTECT_WAIT_BETWEEN_DOWNLOADS",
    show_envvar=True,
)
@click.option(
    "--ignore-failed-downloads",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore failed downloads and continue with next download",
    envvar="PROTECT_IGNORE_FAILED_DOWNLOADS",
    show_envvar=True,
)
@click.option(
    "--skip-existing-files",
    is_flag=True,
    default=False,
    show_default=True,
    help="Skip downloading files which already exist on disk",
    envvar="PROTECT_SKIP_EXISTING",
    show_envvar=True,
)
@click.option(
    "--touch-files",
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Create local file without content for current download - "
        "useful in combination with '--skip-existing-files' to skip problematic segments"
    ),
    envvar="PROTECT_TOUCH_FILES",
    show_envvar=True,
)
@click.option(
    "--use-subfolders/--no-use-subfolders",
    default=True,
    show_default=True,
    help="Save footage to folder structure with format 'YYYY/MM/DD/camera_name/'",
    envvar="PROTECT_USE_SUBFOLDERS",
    show_envvar=True,
)
@click.option(
    "--download-request-timeout",
    "download_timeout",
    default=60.0,
    show_default=True,
    help="Time to wait before aborting download request, in seconds",
    envvar="PROTECT_DOWNLOAD_TIMEOUT",
    show_envvar=True,
)
@click.option(
    "--start",
    type=click.DateTime(
        formats=[
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S%z",
        ]
    ),
    required=True,
    help=(
        "Download range start time. "
        # TODO(danielfernau): uncomment the next line as soon as the feature is implemented
        # "If omitted, the time of the first available recording for each camera will be used."
    ),
    envvar="PROTECT_START_TIME",
    show_envvar=True,
)
@click.option(
    "--end",
    type=click.DateTime(
        formats=[
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S%z",
        ]
    ),
    required=True,
    help=(
        "Download range end time. "
        # TODO(danielfernau): uncomment the next line as soon as the feature is implemented
        # "If omitted, the time of the last available recording for each camera will be used."
    ),
    envvar="PROTECT_END_TIME",
    show_envvar=True,
)
@click.option(
    "--download-motion-heatmaps",
    is_flag=True,
    default=False,
    show_default=True,
    help="Also download motion heatmaps for event recordings",
    envvar="PROTECT_DOWNLOAD_MOTION_HEATMAPS",
    show_envvar=True,
)
@click.option(
    "--use-utc-filenames",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use UTC timestamp in file names instead of local time",
    envvar="PROTECT_USE_UTC",
    show_envvar=True,
)
def events(
    dest: str,
    address: str,
    port: int,
    not_unifi_os: bool,
    username: str,
    password: str,
    verify_ssl: bool,
    cameras: str,
    download_wait: int,
    download_timeout: int,
    use_subfolders: bool,
    touch_files: bool,
    skip_existing_files: bool,
    ignore_failed_downloads: bool,
    start: datetime,
    end: datetime,
    download_motion_heatmaps: bool,
    use_utc_filenames: bool,
) -> None:
    client = ProtectClient(
        address=address,
        port=port,
        not_unifi_os=not_unifi_os,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        ignore_failed_downloads=ignore_failed_downloads,
        destination_path=dest,
        use_subfolders=use_subfolders,
        download_wait=download_wait,
        skip_existing_files=skip_existing_files,
        touch_files=touch_files,
        download_timeout=download_timeout,
        use_utc_filenames=use_utc_filenames,
    )

    try:
        # get camera list
        click.echo("Getting camera list")
        camera_list = client.get_camera_list()

        # get motion event list
        click.echo("Getting motion event list")
        motion_event_list = client.get_motion_event_list(start, end, camera_list)

        if cameras != "all":
            camera_s = set(cameras.split(","))
            # keep only selected cameras in list
            camera_list = [camera for camera in camera_list if camera["id"] in camera_s]
            # keep only events for selected cameras
            motion_event_list = [event for event in motion_event_list if event.camera_id in cameras]

        click.echo(
            f"Downloading motion event video files between {start} and {end}"
            f" from '{client.session.authority}{client.session.base_path}/video/export'"
        )

        for motion_event in motion_event_list:
            # client.download_event(MotionEvent, Camera, bool)
            if not ([camera for camera in camera_list if camera["id"] == motion_event.camera_id]):
                click.echo(
                    f"Unable to download event {motion_event.id[-4:]} at {motion_event.start}:"
                    " camera is not available"
                )
                continue

            Downloader.download_motion_event(
                client,
                motion_event,
                [camera for camera in camera_list if camera["id"] == motion_event.camera_id][0],
                download_motion_heatmaps,
            )

        print_download_stats(client)

    except Errors.ProtectError as e:
        exit(e.code)
