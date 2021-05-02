import json
import os
import pytest
import responses as responses_
import shutil

from datetime import datetime

from protect_archiver.client import ProtectClient
from protect_archiver.dataclasses import Camera


@pytest.fixture
def sample_bootstrap_json():
    with open("fixtures/bootstrap.json") as fp:
        return json.load(fp)


@pytest.fixture
def sample_token_json():
    with open("fixtures/token.json") as fp:
        return json.load(fp)


@pytest.fixture
def sample_access_key_json():
    with open("fixtures/access-key.json") as fp:
        return json.load(fp)


@pytest.fixture
def sample_camera():
    return Camera(
        id="exteriorCameraId",
        name="Exterior",
        recording_start=datetime(2020, 1, 8, 23, 26, 9, 586000),
    )


@pytest.fixture
def test_output_dest():
    test_output_dest = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(test_output_dest)
    yield test_output_dest
    shutil.rmtree(test_output_dest, ignore_errors=False, onerror=None)


@pytest.fixture
def client(test_output_dest):
    return ProtectClient(
        destination_path=test_output_dest, password="test", download_timeout=0.01
    )


@pytest.yield_fixture
def responses():
    # XXX(dcramer): pytest-responses doesnt let you change this behavior yet
    with responses_.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
