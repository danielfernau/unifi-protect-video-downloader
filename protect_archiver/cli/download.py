from datetime import datetime

import click

from protect_archiver.cli.base import cli
from protect_archiver.client import ProtectClient
from protect_archiver.config import Config
from protect_archiver.downloader import Downloader
from protect_archiver.errors import Errors
from protect_archiver.utils import print_download_stats


@cli.command("download", help="Download footage from a local UniFi Protect system")
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
    help="Username of user with local access.",
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
    required=False,
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
    required=False,
    help=(
        "Download range end time. "
        # TODO(danielfernau): uncomment the next line as soon as the feature is implemented
        # "If omitted, the time of the last available recording for each camera will be used."
    ),
    envvar="PROTECT_END_TIME",
    show_envvar=True,
)
@click.option(
    "--disable-alignment",
    "disable_alignment",
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Disables alignment of the 1-hour segments to absolute hours. "
        "If set, results in 8:45, 9:45, 10:45 instead of 8:45, 9:00, 10:00, 10:45."
    ),
    envvar="PROTECT_DISABLE_ALIGNMENT",
    show_envvar=True,
)
@click.option(
    "--disable-splitting",
    "disable_splitting",
    is_flag=True,
    default=False,
    show_default=True,
    help=(
        "Disables splitting the datetime selection in 1-hour segments. "
        "USE WITH CAUTION: requesting segments longer than 1 hour via the "
        "API can cause the Protect console to crash and restart unexpectedly."
    ),
    envvar="PROTECT_DISABLE_SPLITTING",
    show_envvar=True,
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
    envvar="PROTECT_CREATE_SNAPSHOT",
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
def download(
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
    disable_alignment: bool,
    disable_splitting: bool,
    create_snapshot: bool,
    use_utc_filenames: bool,
) -> None:
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
        session = client.get_session()

        if cameras != "all":
            camera_s = set(cameras.split(","))
            camera_list = [c for c in camera_list if c["id"] in camera_s]

        if not create_snapshot:
            for camera in camera_list:
                # noinspection PyUnboundLocalVariable
                click.echo(
                    f"Downloading video files between {start} and {end} from"
                    f" '{session.authority}{session.base_path}/video/export' for camera"
                    f" {camera.name}"
                )

                Downloader.download_footage(
                    client, start, end, camera, disable_alignment, disable_splitting
                )
        else:
            click.echo(
                f"Downloading snapshot files for {start.ctime()}"
                f" from '{session.authority}{session.base_path}/cameras/[camera_id]/snapshot'"
            )
            for camera in camera_list:
                Downloader.download_snapshot(client, start, camera)

        print_download_stats(client)

    except Errors.ProtectError as e:
        exit(e.code)
