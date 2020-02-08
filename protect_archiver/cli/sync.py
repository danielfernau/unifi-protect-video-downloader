import click

from os import path

from .base import cli
from ..client import ProtectClient
from ..sync import ProtectSync


@cli.command("sync", help="Synchronize your Unifi video footage to a local destination")
@click.argument("dest")
@click.option("--address", default="unifi", help="CloudKey IP address or hostname")
@click.option("--port", default=7443, help="UniFi Protect service port")
@click.option(
    "--username", default="ubnt", help="Username of user with local access",
)
@click.option(
    "--password", required=True, help="Password of user with local access",
)
@click.option("--statefile", default="sync.state")
@click.option("--ignore-state", is_flag=True, default=False)
@click.option(
    "--verify-ssl", is_flag=True, default=False, help="Verify CloudKey SSL certificate",
)
@click.option(
    "--ignore-failed-downloads",
    is_flag=True,
    default=False,
    help="Ignore failed downloads and continue with next download (Default: False)",
)
@click.option(
    "--cameras",
    default="all",
    help=(
        "Comma-separated list of one or more camera IDs ('--cameras=\"id_1,id_2,id_3,...\"'). "
        "Use '--cameras=all' to download footage of all available cameras."
    ),
)
def sync(
    dest,
    address,
    port,
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

    client.print_download_stats()
