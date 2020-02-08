import os
import pytest

from datetime import datetime


@pytest.fixture(autouse=True)
def mock_api(
    responses, sample_bootstrap_json, sample_token_json, sample_access_key_json
):
    responses.add(
        responses.POST,
        "https://unifi:7443/api/auth",
        headers={"Authorization": "token.token.token"},
        json=sample_token_json,
    )
    responses.add(
        responses.POST,
        "https://unifi:7443/api/auth/access-key",
        json=sample_access_key_json,
    )
    responses.add(
        responses.GET, "https://unifi:7443/api/bootstrap", json=sample_bootstrap_json
    )


def test_get_camera_list(client):
    results = client.get_camera_list()

    assert len(results) == 1
    assert results[0].id == "exteriorCameraId"
    assert results[0].name == "Exterior"
    assert results[0].recording_start == datetime(2020, 1, 8, 23, 26, 9, 586000)


def test_get_camera_list_with_disconnected(client):
    results = client.get_camera_list(connected=False)

    assert len(results) == 2
    assert results[0].id == "exteriorCameraId"
    assert results[0].name == "Exterior"
    assert results[0].recording_start == datetime(2020, 1, 8, 23, 26, 9, 586000)

    assert results[1].id == "testCameraId"
    assert results[1].name == "Test"
    assert results[1].recording_start == datetime(2019, 10, 20, 18, 0, 0, 134000)


def test_download_footage(responses, client, sample_camera, test_output_dest):
    responses.add(
        responses.GET,
        "https://unifi:7443/api/video/export?accessKey=access:key:example&camera=exteriorCameraId&start=1578553200000&end=1578556739000",
        body="abcdefg",
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": "7",
            "Content-Disposition": 'attachment; filename="FCECDA8FE96B_0_1578622522000_1578625200000.mp4"',
        },
    )

    start = datetime(2020, 1, 8, 23, 0, 0)
    end = datetime(2020, 1, 8, 23, 59, 0)

    client.download_footage(start, end, sample_camera)

    file_name = os.path.join(
        test_output_dest, "Exterior_raId_2020-01-08--23-00-00_2020-01-08--23-58-59.mp4",
    )

    assert os.path.exists(file_name)

    with open(file_name) as fp:
        assert fp.read() == "abcdefg"
