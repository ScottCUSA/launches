"""unittests for launches

Copyright ©️ 2023 Scott Cummings

"""
from datetime import datetime
import pytest
import io
from unittest.mock import MagicMock

import pytz
from freezegun import freeze_time

from launches.launches import load_config

from test_ll2 import VALID_LAUNCHES_DICT

VALID_TEST_CONFIG_JSON = """{
    "notification_handlers": [
        {
            "service": "stdout",
            "render": "text",
            "parameters": {}
        }
    ]
}"""

INVALID_TEST_CONFIG_JSON = """{
    "handlers": []
}"""

TEST_CONFIG = {
    "notification_handlers": [{"service": "stdout", "render": "text", "parameters": {}}]
}


def test_load_config(monkeypatch):

    mock_open = MagicMock(return_value=io.StringIO(VALID_TEST_CONFIG_JSON))
    monkeypatch.setattr("builtins.open", mock_open)
    config = load_config("config.json")
    assert config == TEST_CONFIG
    mock_open.assert_called_with("config.json", encoding="utf-8")


def test_load_config_error(monkeypatch):
    from launches.launches import ConfigError, load_config

    mock_open = MagicMock(return_value=io.StringIO(INVALID_TEST_CONFIG_JSON))
    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(ConfigError) as ex:
        config = load_config("config.json")
    assert str(ex.value) == "malformed configuration"
    mock_open.assert_called_with("config.json", encoding="utf-8")


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime():
    from launches.launches import get_window_datetime

    assert get_window_datetime(1) == datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    assert get_window_datetime(24) == datetime(2023, 11, 20, 6, 55, 0, tzinfo=pytz.utc)


@freeze_time("2023-11-19T06:55:00")
def test_get_window_datetime_negative():
    from launches.launches import get_window_datetime

    with pytest.raises(ValueError) as ex:
        get_window_datetime(-1)
    assert str(ex.value) == "window_hours must be a positive int"


def test_get_upcoming_launches(monkeypatch):
    import launches.launches as project
    from launches.launches import get_upcoming_launches

    mock_get_window_datetime = MagicMock(
        return_value=datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    )
    mock_get_upcoming_launches_within_window = MagicMock(
        return_value=VALID_LAUNCHES_DICT
    )
    monkeypatch.setattr(
        project,
        "get_upcoming_launches_within_window",
        mock_get_upcoming_launches_within_window,
    )
    monkeypatch.setattr(
        project,
        "get_window_datetime",
        mock_get_window_datetime,
    )
    launches = get_upcoming_launches(12)
    assert launches == VALID_LAUNCHES_DICT
    mock_get_window_datetime.assert_called_once()
    mock_get_window_datetime.assert_called_with(12)
    mock_get_upcoming_launches_within_window.assert_called_once()
    mock_get_upcoming_launches_within_window.assert_called_with(
        datetime(2023, 11, 19, 7, 55, 0, tzinfo=pytz.utc)
    )
