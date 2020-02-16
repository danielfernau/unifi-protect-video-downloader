import click

from datetime import datetime

from .base import cli
from ..client import ProtectClient, ProtectError


@cli.command("download", help="Download footage from a local UniFi Protect system")
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
    help="Username of user with local access.",
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
    required=False,
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
    required=False,
    help=(
        "Download range end time. "
        # TODO(danielfernau): uncomment the next line as soon as the feature is implemented
        # "If omitted, the time of the last available recording for each camera will be used."
    ),
)
@click.option(
    "--snapshot",
    "create_snapshot",
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Capture and download a snapshot from the specified camera(s). "
        "This flag cannot be used in combination with the normal video download mode."
    ),
)
def download(
    dest,
    address,
    port,
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
    create_snapshot,
):
    # check the provided command line arguments
    # TODO(danielfernau): remove exit codes 1 (path invalid) and 6 (start/end/snapshot) from docs: no longer valid

    if create_snapshot:
        if start or end:
            click.echo(
                "The arguments --start and --end are ignored when using the --snapshot option"
            )
        start = datetime.now()

    client = ProtectClient(
        address=address,
        port=port,
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

        if cameras != "all":
            cameras = set(cameras.split(","))
            camera_list = [c for c in camera_list if c["id"] in cameras]

        if not create_snapshot:
            for camera in camera_list:
                # noinspection PyUnboundLocalVariable
                click.echo(
                    f"Downloading video files between {start} and {end}"
                    f" from 'https://{address}:{port}/api/video/export' for camera {camera.name} \n"
                )

                client.download_footage(start, end, camera)
        else:
            click.echo(
                f"Downloading snapshot files for {start}"
                f" from 'https://{address}:{port}/api/cameras/{cameras}/snapshot' \n"
            )
            for camera in camera_list:
                client.download_snapshot(start, camera)

        client.print_download_stats()
    except ProtectError as e:
        exit(e.code)
