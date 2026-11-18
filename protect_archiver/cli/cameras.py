import json

from dataclasses import asdict
from typing import List

import click

from protect_archiver.cli.base import cli
from protect_archiver.client import ProtectClient
from protect_archiver.config import Config
from protect_archiver.dataclasses import Camera
from protect_archiver.dataclasses import Stream
from protect_archiver.errors import ProtectError
from protect_archiver.utils import json_encode


def format_stream(stream: Stream) -> str:
    parts = [f"{stream.id}  {stream.name:<8}", f"{stream.resolution:>9}"]
    parts.append(f"{stream.fps:>3} fps" if stream.fps else "  - fps")
    parts.append(f"{stream.bitrate / 1e6:>5.1f} Mbps" if stream.bitrate else "    - Mbps")
    if not stream.enabled:
        parts.append("(disabled)")
    return "  ".join(parts)


def format_camera_list(camera_list: List[Camera]) -> str:
    lines: List[str] = []
    for camera in camera_list:
        lines.append(camera.name)
        lines.append(f"  ID:         {camera.id}")
        if camera.recording_mode:
            lines.append(f"  Recording:  {camera.recording_mode}")
        if camera.streams:
            for index, stream in enumerate(camera.streams):
                label = "  Streams:    " if index == 0 else "              "
                lines.append(label + format_stream(stream))
        else:
            lines.append("  Streams:    none reported")
        lines.append("")

    lines.append(
        "Choose a stream per camera when downloading with --stream, for example"
        ' --stream "<camera id>=medium" or --stream low for every camera.'
    )
    return "\n".join(lines)


@cli.command("cameras", help="List the cameras of a UniFi Protect system and their video streams")
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
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    show_default=True,
    help="Print the cameras and their streams as JSON",
)
def cameras(
    address: str,
    port: int,
    not_unifi_os: bool,
    username: str,
    password: str,
    verify_ssl: bool,
    as_json: bool,
) -> None:
    client = ProtectClient(
        address=address,
        port=port,
        not_unifi_os=not_unifi_os,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
    )

    try:
        camera_list = client.get_camera_list()
    except ProtectError as e:
        exit(e.code)

    if as_json:
        click.echo(
            json.dumps(
                [
                    {k: v for k, v in asdict(camera).items() if k != "selected_stream"}
                    for camera in camera_list
                ],
                default=json_encode,
                indent=2,
            )
        )
    else:
        click.echo(format_camera_list(camera_list))
