import json
from pathlib import Path
from unittest.mock import patch

import pytest

RESOURCES_DIR = "tests/resources"
SINGLE_LAUNCH_JSON = "single_launch.json"
TWO_LAUNCHES_JSON = "two_launches.json"
INVALID_LAUNCHES_DICT = {"error_message": "something unexpected happened"}


@pytest.fixture
def invalid_launches():
    return INVALID_LAUNCHES_DICT


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as get:
        yield get


@pytest.fixture
def mock_ll2_get():
    with patch("launches.ll2.ll2_get") as get:
        yield get


def get_resources_path():
    return Path(RESOURCES_DIR)


@pytest.fixture
def single_launch():
    with get_resources_path().joinpath(SINGLE_LAUNCH_JSON).open("r") as file:
        return json.load(file)


@pytest.fixture
def two_launches():
    with get_resources_path().joinpath(TWO_LAUNCHES_JSON).open("r") as file:
        return json.load(file)
