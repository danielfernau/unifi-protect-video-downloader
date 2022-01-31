import click

from os import path

from protect_archiver.cli.base import cli
from protect_archiver.client import ProtectClient
from protect_archiver.config import Config
from protect_archiver.sync import ProtectSync
from protect_archiver.utils import print_download_stats


@cli.command(
    "sync", help="Synchronize your UniFi Protect footage to a local destination"
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
    "--port",
    default=Config.PORT,
    show_default=True,
    required=False,
    help="CloudKey port number",
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
    "--statefile", default="sync.state", show_default=True,
)
@click.option(
    "--ignore-state", is_flag=True, default=False, show_default=True,
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
def sync(
    dest,
    address,
    port,
    not_unifi_os,
    username,
    password,
    verify_ssl,
    statefile,
    ignore_state,
    ignore_failed_downloads,
    cameras,
):
    # normalize path to destination directory and check if it exists
    dest = path.abspath(dest)
    if not path.isdir(dest):
        click.echo(
            f"Video file destination directory '{dest} is invalid or does not exist!"
        )
        exit(1)

    client = ProtectClient(
        address=address,
        port=port,
        not_unifi_os=not_unifi_os,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        destination_path=dest,
        ignore_failed_downloads=ignore_failed_downloads,
        use_subfolders=True,
    )

    # get camera list
    print("Getting camera list")
    camera_list = client.get_camera_list()

    if cameras != "all":
        camera_ids = set(cameras.split(","))
        camera_list = [c for c in camera_list if c.id in camera_ids]

    process = ProtectSync(client=client, destination_path=dest, statefile=statefile)
    process.run(camera_list, ignore_state=ignore_state)

    print_download_stats(client)
