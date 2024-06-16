"""
# Space Launch Notifications - Configuration Module

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2024 Scott Cummings
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
    search_window: int | None = None
    search_repeat: int | None = None
    notification_handlers: list[NotificationHandlerConfig]


def load_config(config_path: str) -> LaunchesConfig:
    """load project config from JSON
    Example JSON:
    {
        "search_window": 24,
        "search_repeat": 24,
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
                raise ConfigError("malformed configuration")
    except IOError as ex:
        logger.error("Unable to read config file: {}", ex)
        raise ConfigError("unable to read config file")

    return model
