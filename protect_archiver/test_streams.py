import json
import os

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import List

import pytest

from click.testing import CliRunner

from protect_archiver.cli.base import cli
from protect_archiver.cli.cameras import format_camera_list
from protect_archiver.dataclasses import Camera
from protect_archiver.dataclasses import Stream
from protect_archiver.downloader import Downloader
from protect_archiver.streams import StreamSelectionError
from protect_archiver.streams import apply_stream_selection
from protect_archiver.streams import parse_stream_selection
from protect_archiver.streams import stream_filename_suffix
from protect_archiver.streams import stream_query_param


def make_streams() -> List[Stream]:
    return [
        Stream(id=0, name="High", width=2688, height=1512, fps=30, bitrate=8_000_000),
        Stream(id=1, name="Medium", width=1280, height=720, fps=30, bitrate=2_000_000),
        Stream(id=2, name="Low", width=640, height=360, fps=15, bitrate=300_000),
    ]


@pytest.fixture
def cameras() -> List[Camera]:
    return [
        Camera(
            id="6a9eef70004eed03e40003f8",
            name="Theaterzaal",
            recording_start=datetime.min,
            streams=make_streams(),
            recording_mode="adaptive",
        ),
        Camera(
            id="6a9f1a260218cf03e4005a7d",
            name="Entree",
            recording_start=datetime.min,
            streams=make_streams(),
        ),
        # a third-party camera with a single stream
        Camera(
            id="6a9ef4d403cfcf03e40008ab",
            name="Dahua NVR",
            recording_start=datetime.min,
            streams=[Stream(id=0, name="High")],
        ),
    ]


def selected(camera_list: List[Camera]) -> List[Any]:
    return [c.selected_stream for c in camera_list]


def test_parse_stream_selection() -> None:
    selection = parse_stream_selection(" low , Theaterzaal = high,6a9f=1 ")
    assert selection.default == "low"
    assert selection.per_camera == {"theaterzaal": "high", "6a9f": "1"}

    assert parse_stream_selection(None).default is None
    assert parse_stream_selection("").per_camera == {}


@pytest.mark.parametrize("spec", ["low,medium", "=low", "Entree=", "a=low,A=high"])
def test_parse_stream_selection_rejects_invalid(spec: str) -> None:
    with pytest.raises(StreamSelectionError):
        parse_stream_selection(spec)


def test_no_selection_leaves_streams_to_protect(cameras: List[Camera]) -> None:
    apply_stream_selection(cameras, None)
    assert selected(cameras) == [None, None, None]
    assert stream_query_param(cameras[0]) == ""
    assert stream_filename_suffix(cameras[0]) == ""


def test_stream_for_every_camera(cameras: List[Camera], caplog: Any) -> None:
    apply_stream_selection(cameras, "LOW")
    # the single-stream camera keeps the default, with a warning
    assert selected(cameras) == [2, 2, None]
    assert "Dahua NVR" in caplog.text


def test_stream_per_camera_by_id_name_and_number(cameras: List[Camera]) -> None:
    apply_stream_selection(cameras, "low,6a9eef70004eed03e40003f8=medium,entree=0")
    assert selected(cameras) == [1, 0, None]


def test_stream_per_camera_must_exist(cameras: List[Camera]) -> None:
    with pytest.raises(StreamSelectionError, match="Dahua NVR.*available: 0 High"):
        apply_stream_selection(cameras, "Dahua NVR=low")


def test_disabled_stream_cannot_be_chosen(cameras: List[Camera]) -> None:
    cameras[0].streams[2].enabled = False
    with pytest.raises(StreamSelectionError, match="2 Low \\(disabled\\)"):
        apply_stream_selection(cameras, "Theaterzaal=low")


def test_unknown_camera_is_rejected(cameras: List[Camera]) -> None:
    with pytest.raises(StreamSelectionError, match="No selected camera matches 'foyer'"):
        apply_stream_selection(cameras, "Foyer=low")


def test_same_camera_by_id_and_name_is_rejected(cameras: List[Camera]) -> None:
    with pytest.raises(StreamSelectionError, match="more than once"):
        apply_stream_selection(cameras, "Entree=low,6a9f1a260218cf03e4005a7d=high")


def test_query_param_and_file_suffix(cameras: List[Camera]) -> None:
    apply_stream_selection(cameras, "Theaterzaal=low,Entree=high")
    assert stream_query_param(cameras[0]) == "&channel=2"
    assert stream_filename_suffix(cameras[0]) == " (Low)"
    # High keeps the file names of a download without --stream
    assert stream_query_param(cameras[1]) == "&channel=0"
    assert stream_filename_suffix(cameras[1]) == ""


def test_format_camera_list(cameras: List[Camera]) -> None:
    output = format_camera_list(cameras)
    assert "Theaterzaal\n  ID:         6a9eef70004eed03e40003f8\n  Recording:  adaptive" in output
    assert "  Streams:    0  High      2688x1512   30 fps    8.0 Mbps" in output
    assert "              2  Low         640x360   15 fps    0.3 Mbps" in output
    assert "0  High        unknown    - fps      - Mbps" in output


@pytest.fixture
def mock_api(responses: Any, sample_bootstrap_json: Any, sample_token_json: Any) -> None:
    responses.add(
        responses.POST,
        "https://unifi:443/api/auth/login",
        headers={"Set-Cookie": "TOKEN=token.token.token"},
        json=sample_token_json,
    )
    responses.add(
        responses.GET,
        "https://unifi:443/proxy/protect/api/cameras",
        json=sample_bootstrap_json["cameras"],
    )


def test_camera_list_includes_streams(mock_api: None, client: Any) -> None:
    camera = client.get_camera_list()[1]
    assert camera.name == "Test"
    assert camera.recording_mode == "always"
    assert [(s.id, s.name, s.resolution, s.fps, s.bitrate) for s in camera.streams] == [
        (0, "High", "3840x2160", 24, 6000000),
        (1, "Medium", "1280x720", 15, 1200000),
        (2, "Low", "640x360", 15, 200000),
    ]


def test_cameras_command(mock_api: None) -> None:
    args = ["cameras", "--address", "unifi", "--username", "u", "--password", "p"]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0, result.output
    assert "Exterior\n  ID:         exteriorCameraId\n  Recording:  always" in result.output
    assert "1  Medium     1280x720   15 fps    1.2 Mbps" in result.output

    result = CliRunner().invoke(cli, args + ["--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert [c["name"] for c in data] == ["Exterior", "Test", "Offline"]
    assert data[0]["streams"][2] == {
        "id": 2,
        "name": "Low",
        "enabled": True,
        "width": 640,
        "height": 360,
        "fps": 15,
        "bitrate": 200000,
    }
    assert "selected_stream" not in data[0]


def test_download_with_bad_stream_fails_before_downloading(
    mock_api: None, test_output_dest: str
) -> None:
    result = CliRunner().invoke(
        cli,
        [
            "download",
            test_output_dest,
            "--address=unifi",
            "--username=u",
            "--password=p",
            "--start=2020-01-08 23:00:00",
            "--end=2020-01-08 23:59:00",
            "--stream=Exterior=ultra",
        ],
    )
    assert result.exit_code == 2
    assert "Camera 'Exterior' has no enabled stream 'ultra'" in result.output
    assert os.listdir(test_output_dest) == []


def test_download_footage_requests_selected_stream(
    responses: Any, client: Any, sample_camera: Camera, test_output_dest: str
) -> None:
    sample_camera.streams = make_streams()
    apply_stream_selection([sample_camera], "low")
    responses.add(
        responses.GET,
        "https://unifi:443/proxy/protect/api/video/export?camera=exteriorCameraId"
        "&start=1578524400000&end=1578527939999&channel=2",
        body="x" * 320,
        headers={"Content-Type": "video/mp4", "Content-Length": "320"},
    )
    responses.add(
        responses.POST,
        "https://unifi:443/api/auth/login",
        headers={"Set-Cookie": "TOKEN=token.token.token"},
        json={},
    )

    Downloader.download_footage(
        client,
        datetime(2020, 1, 8, 23, 0, 0, tzinfo=timezone.utc),
        datetime(2020, 1, 8, 23, 59, 0, tzinfo=timezone.utc),
        sample_camera,
    )

    assert os.path.exists(
        os.path.join(test_output_dest, "Exterior (raId) - 2020-01-08 - 23.00.00+0000 (Low).mp4")
    )
