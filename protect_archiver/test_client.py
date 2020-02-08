from datetime import datetime

from .client import ProtectClient


def test_get_camera_list(responses, sample_bootstrap_json):
    responses.add(
        responses.POST,
        "https://unifi:7443/api/auth",
        headers={"Authorization": "Bearer tokenid"},
    )
    responses.add(
        responses.POST,
        "https://unifi:7443/api/auth/access-key",
        json={"accessKey": "access:key"},
    )
    responses.add(
        responses.GET, "https://unifi:7443/api/bootstrap", json=sample_bootstrap_json
    )

    client = ProtectClient(password="test")
    results = client.get_camera_list()

    assert len(results) == 2
    assert results[0].id == "exteriorCameraId"
    assert results[0].name == "Exterior"
    assert results[0].recording_start == datetime(2020, 1, 8, 23, 26, 9, 586000)

    assert results[1].id == "testCameraId"
    assert results[1].name == "Test"
    assert results[1].recording_start == datetime(2019, 10, 20, 18, 0, 0, 134000)
