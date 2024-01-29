import os

from datetime import datetime
from datetime import timezone
from typing import Any

import pytest

from protect_archiver.downloader import Downloader


@pytest.fixture(autouse=True)
def mock_api(
    responses: Any, sample_bootstrap_json: Any, sample_token_json: Any, sample_access_key_json: Any
) -> None:
    responses.add(
        responses.POST,
        "https://unifi:443/api/auth/login",
        headers={"Set-Cookie": "TOKEN=token.token.token"},
        json=sample_token_json,
    )
    responses.add(
        responses.POST,
        "https://unifi:7443/api/auth/access-key",
        json=sample_access_key_json,
    )
    responses.add(responses.GET, "https://unifi:7443/api/bootstrap", json=sample_bootstrap_json)
    responses.add(
        responses.GET,
        "https://unifi:443/proxy/protect/api/cameras",
        json=sample_bootstrap_json["cameras"],
    )


def test_get_camera_list(client: Any) -> None:
    results = client.get_camera_list()

    assert len(results) == 3
    assert results[0].id == "exteriorCameraId"
    assert results[0].name == "Exterior"
    assert results[0].recording_start == datetime(2020, 1, 8, 23, 26, 9, 586000)

    assert results[1].id == "testCameraId"
    assert results[1].name == "Test"
    assert results[1].recording_start == datetime(2019, 10, 20, 18, 0, 0, 134000)

    assert results[2].id == "offlineCameraId"
    assert results[2].name == "Offline"
    assert results[2].recording_start == datetime.min


def test_download_footage(
    responses: Any, client: Any, sample_camera: Any, test_output_dest: Any
) -> None:
    responses.add(
        responses.GET,
        "https://unifi:443/proxy/protect/api/video/export?camera=exteriorCameraId&start=1578524400000&end=1578527939000",
        # 320 bytes of demo data
        body=(
            "12572d283469d8c82413787fd73e0c91456c49ea991b2d5bf5e9c87bc3633566"
            "c8825185f86ab64ae748342f0030cf5dcabf49090a98d06c019024883d2bdd57"
            "35704f975f15344cbd0771597ceb50d1062402e64555157abcb3a362290aa818"
            "e1d02d3942f029bec370e7d12bd62bec347b373c66bccced3a1071fc69cef311"
            "d19e46501c94273a42fb72f694ddbf1fcb22c257970b206e981dab011915aa42"
        ),
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": "320",
            "Content-Disposition": (
                'attachment; filename="FCECDA8FE96B_0_1578622522000_1578625200000.mp4"'
            ),
        },
    )

    start = datetime(2020, 1, 8, 23, 0, 0, tzinfo=timezone.utc)
    end = datetime(2020, 1, 8, 23, 59, 0, tzinfo=timezone.utc)

    Downloader.download_footage(
        client, start, end, sample_camera, disable_alignment=False, disable_splitting=False
    )

    file_name = os.path.join(
        test_output_dest,
        "Exterior (raId) - 2020-01-08 - 23.00.00+0000.mp4",
    )

    assert os.path.exists(file_name)

    with open(file_name) as fp:
        assert (
            fp.read() == "12572d283469d8c82413787fd73e0c91456c49ea991b2d5bf5e9c87bc3633566"
            "c8825185f86ab64ae748342f0030cf5dcabf49090a98d06c019024883d2bdd57"
            "35704f975f15344cbd0771597ceb50d1062402e64555157abcb3a362290aa818"
            "e1d02d3942f029bec370e7d12bd62bec347b373c66bccced3a1071fc69cef311"
            "d19e46501c94273a42fb72f694ddbf1fcb22c257970b206e981dab011915aa42"
        )
