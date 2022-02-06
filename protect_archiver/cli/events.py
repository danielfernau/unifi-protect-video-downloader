import click

from protect_archiver.cli.base import cli
from protect_archiver.client import ProtectClient
from protect_archiver.config import Config
from protect_archiver.downloader import Downloader
from protect_archiver.errors import Errors
from protect_archiver.utils import print_download_stats


@cli.command(
    "events", help="Download event recordings from UniFi Protect to a local destination"
)
@click.argument("dest", type=click.Path(exists=True, writable=True, resolve_path=True))
@click.option(
    "--address",
    default=Config.ADDRESS,
    show_default=True,
    required=True,
    help="IP address or hostname of the UniFi Protect Server",
)
@click.option(
    "--port",
    default=Config.PORT,
    show_default=True,
    required=False,
    help="The port of the UniFi Protect Server",
)
@click.option(
    "--not-unifi-os",
    is_flag=True,
    default=False,
    show_default=True,
    help="Use this for systems without UniFi OS",
)
@click.option(
    "--username",
    required=True,
    help="Username of user with local access",
    prompt="Username of local Protect user",
)
@click.option(
    "--password",
    required=True,
    help="Password of user with local access",
    prompt="Password for local Protect user",
    hide_input=True,
)
@click.option(
    "--verify-ssl",
    is_flag=True,
    default=False,
    show_default=True,
    help="Verify Protect SSL certificate",
)
@click.option(
    "--cameras",
    default="all",
    show_default=True,
    help=(
        "Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        "Use '--cameras=all' to download footage of all available cameras."
    ),
)
@click.option(
    "--wait-between-downloads",
    "download_wait",
    default=0,
    show_default=True,
    help="Time to wait between file downloads, in seconds",
)
@click.option(
    "--ignore-failed-downloads",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore failed downloads and continue with next download",
)
@click.option(
    "--skip-existing-files",
    is_flag=True,
    default=False,
    show_default=True,
    help="Skip downloading files which already exist on disk",
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
)
@click.option(
    "--use-subfolders/--no-use-subfolders",
    default=True,
    show_default=True,
    help="Save footage to folder structure with format 'YYYY/MM/DD/camera_name/'",
)
@click.option(
    "--download-request-timeout",
    "download_timeout",
    default=60.0,
    show_default=True,
    help="Time to wait before aborting download request, in seconds",
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
)
@click.option(
    "--download-motion-heatmaps",
    is_flag=True,
    default=False,
    show_default=True,
    help="Also download motion heatmaps for event recordings",
)
def events(
    dest,
    address,
    port,
    not_unifi_os,
    username,
    password,
    verify_ssl,
    cameras,
    download_wait,
    download_timeout,
    use_subfolders,
    touch_files,
    skip_existing_files,
    ignore_failed_downloads,
    start,
    end,
    download_motion_heatmaps,
):
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
    )

    try:
        # get camera list
        click.echo("Getting camera list")
        camera_list = client.get_camera_list()

        # get motion event list
        click.echo("Getting motion event list")
        motion_event_list = client.get_motion_event_list(start, end, camera_list)

        if cameras != "all":
            cameras = set(cameras.split(","))
            # keep only selected cameras in list
            camera_list = [camera for camera in camera_list if camera["id"] in cameras]
            # keep only events for selected cameras
            motion_event_list = [
                event for event in motion_event_list if event.camera_id in cameras
            ]

        click.echo(
            f"Downloading motion event video files between {start} and {end}"
            f" from '{client.session.authority}{client.session.base_path}/video/export'"
        )

        for motion_event in motion_event_list:
            # client.download_event(MotionEvent, Camera, bool)
            if not (
                [
                    camera
                    for camera in camera_list
                    if camera["id"] == motion_event.camera_id
                ]
            ):
                click.echo(
                    f"Unable to download event {motion_event.id[-4:]} at {motion_event.start}: camera is not available"
                )
                continue

            Downloader.download_motion_event(
                client,
                motion_event,
                [
                    camera
                    for camera in camera_list
                    if camera["id"] == motion_event.camera_id
                ][0],
                download_motion_heatmaps,
            )

        print_download_stats(client)

    except Errors.ProtectError as e:
        exit(e.code)
