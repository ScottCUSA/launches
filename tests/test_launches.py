"""unittests for launches

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from launches.errors import LaunchesError, NotificationError
from launches.launches import (
    check_for_upcoming_launches,
    get_upcoming_launches,
    get_window_datetime,
    send_notification,
)


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime():
    """get_window_datetime should return a datetime object # hours in the future"""
    assert get_window_datetime(1) == datetime(2023, 11, 19, 7, 55, 0, tzinfo=timezone.utc)
    assert get_window_datetime(24) == datetime(2023, 11, 20, 6, 55, 0, tzinfo=timezone.utc)


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime_negative():
    """get_window_datetime should raise ValueError if window_hours is negative"""
    with pytest.raises(ValueError, match="window_hours must be a positive int") as ex:
        get_window_datetime(-1)
    assert str(ex.value) == "window_hours must be a positive int"


@patch("launches.launches.LaunchLibrary2Client")
def test_get_upcoming_launches(mock_client):
    """get_upcoming_launches should call the LaunchLibrary2Client and return its response"""
    # setup
    mock_client.return_value.get_upcoming_launches_within_window.return_value = {
        "count": 1,
        "results": [{}],
    }

    # test
    result = get_upcoming_launches(1, "prod")

    # assert
    assert result == {"count": 1, "results": [{}]}
    mock_client.assert_called_once_with("prod")
    mock_client.return_value.get_upcoming_launches_within_window.assert_called_once()


def test_send_notification(single_launch):
    # setup
    notification_handlers = [MagicMock()]

    # test
    send_notification(single_launch, notification_handlers)

    # assert
    notification_handlers[0].send.assert_called_with(single_launch)


def test_send_notification_exception(single_launch):
    # setup
    notification_handlers = [MagicMock(send=MagicMock(side_effect=NotificationError))]

    # test
    send_notification(single_launch, notification_handlers)

    # assert
    notification_handlers[0].send.assert_called_with(single_launch)


@patch("launches.launches.send_notification")
@patch("launches.launches.LaunchLibrary2Client")
def test_check_for_upcoming_launches_with_launches(mock_client, mock_send_notification):
    """check_for_upcoming_launches should send notifications if launches are found"""
    # setup
    mock_client.return_value.get_upcoming_launches_within_window.return_value = {
        "count": 1,
        "results": [{}],
    }
    notification_handlers = [MagicMock()]

    # test
    check_for_upcoming_launches(1, notification_handlers, mock_client.return_value)

    # assert
    mock_client.return_value.get_upcoming_launches_within_window.assert_called_once()
    mock_send_notification.assert_called_once_with(
        {"count": 1, "results": [{}]}, notification_handlers
    )


@patch("launches.launches.send_notification")
@patch("launches.launches.LaunchLibrary2Client")
def test_check_for_upcoming_launches_no_launches(mock_client, mock_send_notification):
    """check_for_upcoming_launches should not send notifications if no launches are found"""
    # setup
    mock_client.return_value.get_upcoming_launches_within_window.return_value = {
        "count": 0,
        "results": [],
    }
    notification_handlers = [MagicMock()]

    # test
    check_for_upcoming_launches(1, notification_handlers, mock_client.return_value)

    # assert
    mock_client.return_value.get_upcoming_launches_within_window.assert_called_once()
    mock_send_notification.assert_not_called()


@patch("launches.launches.LaunchLibrary2Client")
def test_check_for_upcoming_launches_exception(mock_client):
    """check_for_upcoming_launches should handle exceptions gracefully"""
    # setup
    mock_client.return_value.get_upcoming_launches_within_window.side_effect = LaunchesError
    notification_handlers = [MagicMock()]

    # test
    check_for_upcoming_launches(1, notification_handlers, mock_client.return_value)

    # assert
    mock_client.return_value.get_upcoming_launches_within_window.assert_called_once()
