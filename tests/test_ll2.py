"""unittests for launches.ll2

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from launches.ll2 import (
    LL2_UPCOMING_ENDPOINT,
    LL2RequestError,
    check_response,
    get_upcoming_launches_within_window,
    ll2_get,
)


def test_check_valid_response(valid_launches):
    """check_response should return None if response is valid"""
    assert check_response(valid_launches) is None


def test_check_error_response(invalid_launches):
    """check_response should raise LL2RequestError if response is an error"""
    with pytest.raises(LL2RequestError):
        check_response(invalid_launches)


def test_ll2_get(mock_requests_get):
    # setup
    mock_requests_get.return_value = MagicMock()
    # test
    ll2_get("test_endpoint", {"test": "test"})
    # assert
    mock_requests_get.assert_called_once()


def test_ll2_get_exception(mock_requests_get):
    # setup
    mock_requests_get.side_effect = requests.exceptions.RequestException
    # test
    with pytest.raises(LL2RequestError):
        ll2_get("test_endpoint", {"test": "test"})
    # assert
    mock_requests_get.assert_called_once()


@patch("launches.ll2.check_response")
def test_get_upcoming_launches_within_window(mock_check_response: MagicMock, mock_ll2_get):
    # setup
    response = {"count": 10}
    mock_ll2_get.return_value = MagicMock(json=MagicMock(return_value=response))
    mock_check_response.return_value = None
    window_start = datetime(year=2024, month=1, day=1, hour=12, minute=0, second=0)
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
    }

    # test
    launches = get_upcoming_launches_within_window(window_start)

    # assert
    assert launches == response
    mock_ll2_get.assert_called_with(LL2_UPCOMING_ENDPOINT, parameters)
    mock_ll2_get.return_value.json.assert_called_once()


def test_get_upcoming_launches_within_window_invalid_json(mock_ll2_get):
    # setup
    mock_ll2_get.return_value = MagicMock(
        json=MagicMock(side_effect=json.JSONDecodeError("", "", 0))
    )
    window_start = datetime(year=2024, month=1, day=1, hour=12, minute=0, second=0)
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
    }

    # test
    with pytest.raises(LL2RequestError) as exinfo:
        get_upcoming_launches_within_window(window_start)

    # assert
    mock_ll2_get.assert_called_with(LL2_UPCOMING_ENDPOINT, parameters)
    mock_ll2_get.return_value.json.assert_called_once()
    assert str(exinfo.value).startswith("Unable to decode response JSON")


@patch("launches.ll2.check_response")
def test_get_upcoming_launches_within_window_invalid_response(
    mock_check_response: MagicMock, mock_ll2_get
):
    # setup
    mock_ll2_get.return_value = MagicMock()
    mock_check_response.side_effect = LL2RequestError("unexpected response")
    window_start = datetime(year=2024, month=1, day=1, hour=12, minute=0, second=0)
    parameters = {
        "window_start__lt": "2024-01-01T12:00:00Z",
        "hide_recent_previous": True,
    }

    # test
    with pytest.raises(LL2RequestError):
        get_upcoming_launches_within_window(window_start)

    # assert
    mock_ll2_get.assert_called_with(LL2_UPCOMING_ENDPOINT, parameters)
    mock_check_response.assert_called_once()
