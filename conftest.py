import json
import pytest


@pytest.fixture
def sample_bootstrap_json():
    with open("fixtures/bootstrap.json") as fp:
        return json.load(fp)
