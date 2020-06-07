import click

from .base import cli
from ..client import ProtectClient, ProtectError


@cli.command(
    "events", help="Download event recordings from UniFi Protect to a local destination"
)
@click.argument("dest", type=click.Path(exists=True, writable=True, resolve_path=True))
@click.option(
    "--address",
    default="unifi",
    show_default=True,
    required=True,
    help="CloudKey IP address or hostname",
)
@click.option(
    "--port", default=7443, show_default=True, help="UniFi Protect service port"
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
    help="Verify CloudKey SSL certificate",
)
@click.option(
    "--ignore-failed-downloads",
    is_flag=True,
    default=False,
    show_default=True,
    help="Ignore failed downloads and continue with next download",
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
    "--skip-existing-files",
    is_flag=True,
    default=False,
    show_default=True,
    help="Skip downloading files which already exist on disk",
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
    username,
    password,
    verify_ssl,
    ignore_failed_downloads,
    cameras,
    download_timeout,
    use_subfolders,
    skip_existing_files,
    start,
    end,
    download_motion_heatmaps,
):
    client = ProtectClient(
        destination_path=dest,
        address=address,
        port=port,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        ignore_failed_downloads=ignore_failed_downloads,
        download_timeout=download_timeout,
        use_subfolders=use_subfolders,
        skip_existing_files=skip_existing_files,
    )

    try:
        # get camera list
        click.echo("Getting camera list")
        camera_list = client.get_camera_list()

        # get motion event list
        click.echo("Getting motion event list")
        motion_event_list = client.get_motion_event_list(start, end)

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
            f" from 'https://{address}:{port}/api/video/export' \n"
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

            client.download_motion_event(
                motion_event,
                [
                    camera
                    for camera in camera_list
                    if camera["id"] == motion_event.camera_id
                ][0],
                download_motion_heatmaps,
            )

        client.print_download_stats()
    except ProtectError as e:
        exit(e.code)
