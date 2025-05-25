"""
# Space Launch Notifications - Configuration Module

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from typing import Any

from loguru import logger
from pydantic import BaseModel, ValidationError

from launches.errors import ConfigError


class NotificationHandlerConfig(BaseModel):
    service: str
    renderer: str
    parameters: dict[str, Any]


class LaunchesConfig(BaseModel):
    periodic: bool = False
    search_window_hours: int | None = None
    search_repeat_hours: int | None = None
    daily_check_times: list[str] | None = None
    time_zone: str | None = None
    notification_handlers: list[NotificationHandlerConfig]
    cache_enabled: bool = True
    cache_directory: str | None = None


def load_config(config_path: str) -> LaunchesConfig:
    """load project config from JSON
    Example JSON:
    {
        "search_window_hours": 24,
        "search_repeat_hours": 24,
        "notification_handlers": [
            {
                "service": "stdout",
                "renderer": "plaintext",
                "parameters": {}
            },
            {
                "service":"email",
                "renderer": "plaintext",
                "parameters":{
                    "smtp_server":"smtp-server",
                    "smtp_port": 587,
                    "smtp_username":"",
                    "smtp_password":"",
                    "sender":"",
                    "recipients": ["",""]
                }
            },
            {
                "service":"gmail",
                "renderer": "html",
                "parameters":{
                    "credentials_file":"credentials.json",
                    "token_file":"token.json",
                    "sender":"",
                    "recipients": ["",""]
                }
            }
        ]
    }
    """
    # attempt to load the configuration
    try:
        logger.info("Attempting to load configuration file: `{}`", config_path)
        with open(config_path, encoding="utf-8") as fp:
            try:
                model = LaunchesConfig.model_validate_json(fp.read())
            except ValidationError as ex:
                logger.error("Invalid configuration: {}", ex)
                raise ConfigError("malformed configuration") from ex
    except IOError as ex:
        logger.error("Unable to read config file: {}", ex)
        raise ConfigError("unable to read config file") from ex

    return model
