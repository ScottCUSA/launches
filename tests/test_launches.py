"""unittests for launches

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
import pytz
from freezegun import freeze_time

from launches import launches
from launches.errors import NotificationError
from launches.launches import (
    get_upcoming_launches,
    get_window_datetime,
    send_notification,
)


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime():
    """get_window_datetime should return a datetime object # hours in the future"""
    assert get_window_datetime(1) == datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    assert get_window_datetime(24) == datetime(2023, 11, 20, 6, 55, 0, tzinfo=pytz.utc)


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime_negative():
    """get_window_datetime should raise ValueError if window_hours is negative"""
    with pytest.raises(ValueError) as ex:
        get_window_datetime(-1)
    assert str(ex.value) == "window_hours must be a positive int"


def test_get_upcoming_launches(monkeypatch, valid_launches):
    """get_upcoming_launches should return a dict of upcoming launches"""
    mock_get_window_datetime = MagicMock(
        return_value=datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    )
    mock_get_upcoming_launches_within_window = MagicMock(return_value=valid_launches)
    monkeypatch.setattr(
        launches,
        "get_upcoming_launches_within_window",
        mock_get_upcoming_launches_within_window,
    )
    monkeypatch.setattr(
        launches,
        "get_window_datetime",
        mock_get_window_datetime,
    )
    ul = get_upcoming_launches(12)
    assert ul == valid_launches
    mock_get_window_datetime.assert_called_once()
    mock_get_window_datetime.assert_called_with(12)
    mock_get_upcoming_launches_within_window.assert_called_once()
    mock_get_upcoming_launches_within_window.assert_called_with(
        datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    )


def test_send_notification(valid_launches):
    # setup
    notification_handlers = [MagicMock()]

    # test
    send_notification(valid_launches, notification_handlers)  # type: ignore

    # assert
    notification_handlers[0].send.assert_called_with(valid_launches)


def test_send_notification_exception(valid_launches):
    # setup
    notification_handlers = [MagicMock(send=MagicMock(side_effect=NotificationError))]

    # test
    send_notification(valid_launches, notification_handlers)  # type: ignore

    # assert
    notification_handlers[0].send.assert_called_with(valid_launches)
