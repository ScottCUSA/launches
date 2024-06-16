import io
from unittest.mock import MagicMock

import pytest

from launches.config import LaunchesConfig, NotificationHandlerConfig, load_config
from launches.errors import ConfigError

VALID_TEST_CONFIG_JSON = """{
    "search_window": 24,
    "search_repeat": 8,
    "notification_handlers": [
        {
            "service": "stdout",
            "renderer": "text",
            "parameters": {}
        }
    ]
}"""


VALID_TEST_CONFIG_JSON_2 = """{
    "notification_handlers": [
        {
            "service": "stdout",
            "renderer": "text",
            "parameters": {}
        }
    ]
}"""

INVALID_TEST_CONFIG_JSON = """{
    "handlers": []
}"""

INVALID_TEST_CONFIG_INVALID_JSON = "{"

TEST_CONFIG = {"notification_handlers": [{"service": "stdout", "render": "text", "parameters": {}}]}


def test_load_config(monkeypatch):
    """load config should return a dict from a valid config file"""
    mock_open = MagicMock(return_value=io.StringIO(VALID_TEST_CONFIG_JSON))
    monkeypatch.setattr("builtins.open", mock_open)
    config = load_config("config.json")
    assert config == LaunchesConfig(
        search_window=24,
        search_repeat=8,
        notification_handlers=[
            NotificationHandlerConfig(service="stdout", renderer="text", parameters={})
        ],
    )
    mock_open.assert_called_with("config.json", encoding="utf-8")


def test_load_config_no_window_or_repeat(monkeypatch):
    """load config should return a dict from a valid config file"""
    mock_open = MagicMock(return_value=io.StringIO(VALID_TEST_CONFIG_JSON_2))
    monkeypatch.setattr("builtins.open", mock_open)
    config = load_config("config.json")
    assert config == LaunchesConfig(
        search_window=None,
        search_repeat=None,
        notification_handlers=[
            NotificationHandlerConfig(service="stdout", renderer="text", parameters={})
        ],
    )
    mock_open.assert_called_with("config.json", encoding="utf-8")


def test_load_config_error(monkeypatch):
    """load config should raise ConfigError if config is malformed"""
    mock_open = MagicMock(return_value=io.StringIO(INVALID_TEST_CONFIG_JSON))
    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(ConfigError) as ex:
        _ = load_config("config.json")
    assert str(ex.value) == "malformed configuration"
    mock_open.assert_called_with("config.json", encoding="utf-8")


def test_load_config_io_error(monkeypatch):
    """load config should raise ConfigError if config is malformed"""
    mock_open = MagicMock(side_effect=IOError)
    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(ConfigError) as ex:
        _ = load_config("config.json")
    assert str(ex.value) == "unable to read config file"
    mock_open.assert_called_with("config.json", encoding="utf-8")


def test_load_config_json_decode_error(monkeypatch):
    """load config should raise ConfigError if config is malformed"""
    mock_bad_json = io.StringIO(INVALID_TEST_CONFIG_INVALID_JSON)
    mock_open = MagicMock(return_value=mock_bad_json)
    monkeypatch.setattr("builtins.open", mock_open)
    with pytest.raises(ConfigError) as ex:
        _ = load_config("config.json")
    assert str(ex.value) == "malformed configuration"
