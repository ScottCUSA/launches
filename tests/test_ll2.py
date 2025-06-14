"""unittests for launches.ll2

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests.exceptions

from launches.ll2 import LL2_API_URL, LaunchLibrary2Client, LL2RequestError


@pytest.fixture
def client():
    return LaunchLibrary2Client()


def test_init_valid_env():
    c = LaunchLibrary2Client("prod")
    assert c.env == "prod"
    assert c.base_url == LL2_API_URL["prod"]

    c = LaunchLibrary2Client("dev")
    assert c.env == "dev"
    assert c.base_url == LL2_API_URL["dev"]


def test_init_invalid_env():
    with pytest.raises(ValueError, match="Unknown LL2 environment: invalid_env"):
        LaunchLibrary2Client("invalid_env")


def test_check_valid_response(client):
    """check_response should return None if response is valid"""
    valid_launches = {"count": 1, "results": [{}]}
    assert client.check_response(valid_launches) is None


@pytest.mark.parametrize(
    "invalid_launches",
    [
        None,
        [],
        {},
        {"foo": "bar"},
        {"count": 1},
        {"results": []},
    ],
)
def test_check_error_response(client, invalid_launches):
    """check_response should raise LL2RequestError if response is an error"""
    with pytest.raises(LL2RequestError):
        client.check_response(invalid_launches)


@patch("requests.get")
def test_ll2_get_success(mock_requests_get):
    # setup
    mock_requests_get.return_value = MagicMock(status_code=200, raise_for_status=lambda: None)
    c = LaunchLibrary2Client()
    # test
    resp = c.ll2_get("test_endpoint", {"test": "test"})
    # assert
    mock_requests_get.assert_called_once()
    assert resp == mock_requests_get.return_value


@patch("requests.get")
def test_ll2_get_exception(mock_requests_get):
    # setup
    mock_requests_get.side_effect = requests.exceptions.RequestException
    c = LaunchLibrary2Client()
    # test
    with pytest.raises(LL2RequestError):
        c.ll2_get("test_endpoint", {"test": "test"})
    # assert
    mock_requests_get.assert_called_once()


@patch.object(LaunchLibrary2Client, "ll2_get")
@patch.object(LaunchLibrary2Client, "check_response")
def test_get_upcoming_launches_within_window(mock_check_response, mock_ll2_get):
    # setup
    c = LaunchLibrary2Client()
    response = {"count": 10, "results": [{}]}
    mock_ll2_get.return_value = MagicMock(json=MagicMock(return_value=response), text="{}")
    mock_check_response.return_value = None
    window_start_lt = datetime(
        tzinfo=timezone.utc, year=2024, month=1, day=1, hour=12, minute=0, second=0
    )
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
        "mode": "detailed",
    }

    # test
    launches = c.get_upcoming_launches_within_window(window_start_lt)

    # assert
    assert launches == response
    mock_ll2_get.assert_called_with(c.LL2_UPCOMING_ENDPOINT, parameters)
    mock_ll2_get.return_value.json.assert_called_once()


@patch.object(LaunchLibrary2Client, "ll2_get")
def test_get_upcoming_launches_within_window_invalid_json(mock_ll2_get):
    # setup
    c = LaunchLibrary2Client()
    mock_ll2_get.return_value = MagicMock(
        json=MagicMock(side_effect=json.JSONDecodeError("", "", 0)), text="{}"
    )
    window_start_lt = datetime(
        tzinfo=timezone.utc, year=2024, month=1, day=1, hour=12, minute=0, second=0
    )
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
        "mode": "detailed",
    }

    # test
    with pytest.raises(LL2RequestError) as exinfo:
        c.get_upcoming_launches_within_window(window_start_lt)

    # assert
    mock_ll2_get.assert_called_with(c.LL2_UPCOMING_ENDPOINT, parameters)
    mock_ll2_get.return_value.json.assert_called_once()
    assert str(exinfo.value).startswith("Unable to decode response JSON")


@patch.object(LaunchLibrary2Client, "ll2_get")
@patch.object(LaunchLibrary2Client, "check_response")
def test_get_upcoming_launches_within_window_invalid_response(mock_check_response, mock_ll2_get):
    # setup
    c = LaunchLibrary2Client()
    mock_ll2_get.return_value = MagicMock(json=MagicMock(return_value={}), text="{}")
    mock_check_response.side_effect = LL2RequestError("unexpected response")
    window_start_lt = datetime(
        tzinfo=timezone.utc, year=2024, month=1, day=1, hour=12, minute=0, second=0
    )
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
        "mode": "detailed",
    }

    # test
    with pytest.raises(LL2RequestError):
        c.get_upcoming_launches_within_window(window_start_lt)

    # assert
    mock_ll2_get.assert_called_with(c.LL2_UPCOMING_ENDPOINT, parameters)
    mock_check_response.assert_called_once()
