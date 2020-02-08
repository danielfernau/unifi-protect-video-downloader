import click

from datetime import datetime
from os import path

from .base import cli
from ..client import ProtectClient, ProtectError


@cli.command("download", help="Download footage from a local UniFi Protect system")
@click.argument("dest")
@click.option("--address", default="unifi", help="CloudKey IP address or hostname")
@click.option("--port", default=7443, help="UniFi Protect service port")
@click.option(
    "--username", default="ubnt", help="Username of user with local access",
)
@click.option(
    "--password", required=True, help="Password of user with local access",
)
@click.option(
    "--verify-ssl", default=False, help="Verify CloudKey SSL certificate",
)
@click.option(
    "--cameras",
    default="all",
    help=(
        "Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        "Use '--cameras=all' to download footage of all available cameras."
    ),
)
@click.option(
    "--wait-between-downloads",
    "download_wait",
    default=0,
    help="Time to wait between file downloads, in seconds (Default: 0)",
)
@click.option(
    "--ignore-failed-downloads",
    is_flag=True,
    default=False,
    help="Ignore failed downloads and continue with next download (Default: False)",
)
@click.option(
    "--skip-existing-files",
    is_flag=True,
    default=False,
    help="Skip downloading files which already exist on disk (Default: False)",
)
@click.option(
    "--touch-files",
    default=False,
    is_flag=True,
    help=(
        "Create local file without content for current download (Default: False) - "
        "useful in combination with '--skip-existing-files' to skip problematic segments"
    ),
)
@click.option(
    "--use-subfolders/--no-use-subfolders",
    default=True,
    help="Save footage to folder structure with format 'YYYY/MM/DD/camera_name/' (Default: False)",
)
@click.option(
    "--download-request-timeout",
    "download_timeout",
    default=60.0,
    help="Time to wait before aborting download request, in seconds (Default: 60)",
)
@click.option(
    "--start",
    required=False,
    help='Start time in dateutil.parser compatible format, for example "YYYY-MM-DD HH:MM:SS+0000"',
)
@click.option(
    "--end",
    type=str,
    required=False,
    help='End time in dateutil.parser compatible format, for example "YYYY-MM-DD HH:MM:SS+0000"',
)
@click.option(
    "--snapshot",
    "create_snapshot",
    default=False,
    is_flag=True,
    help="Capture and download a snapshot from the specified camera(s)",
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
    if not (create_snapshot or (start and end)):
        click.echo("Please use --snapshot, or provide --start and --end timestamps")
        exit(6)

    if create_snapshot:
        if start or end:
            click.echo(
                "The arguments --start and --end are ignored when using the --snapshot option"
            )
        start = datetime.now()

    # normalize path to destination directory and check if it exists
    dest = path.abspath(dest)
    if not path.isdir(dest):
        click.echo(
            f"Video file destination directory '{dest}' is invalid or does not exist!"
        )
        exit(1)

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
            # noinspection PyUnboundLocalVariable
            click.echo(
                f"Downloading video files between {start} and {end}"
                f" from 'https://{address}:{port}/api/video/export' \n"
            )

            for camera in camera_list:
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
