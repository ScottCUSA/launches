"""
# Space Launch Notifications - Module 

A tool/library which checks for upcoming space launches via an API
and can send a notifications if there are any upcoming space launch events.

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Any

import pytz

from .ll2 import get_upcoming_launches_within_window
from .notifications.services import NotificationError
from .notifications.handlers import NotificationHandler


class ConfigError(Exception):
    """project configuration error"""


def load_config(config_path: str) -> dict[str, Any]:
    """load project config from JSON
    Example JSON:
    {
        "notification_handlers": [
            {
                "service": "stdout",
                "render": "plaintext",
                "parameters": {}
            },
            {
                "service":"email",
                "render": "plaintext",
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
        logging.info("Attempting to load configuration file: `%s`", config_path)
        with open(config_path, encoding="utf-8") as fp:
            config = json.load(fp)
    except IOError as ex:
        logging.error("Unable to read config file: %s", ex)
        sys.exit(1)
    except json.JSONDecodeError as ex:
        logging.error("Unable to decode the config file as JSON: %s", ex)
        sys.exit(1)

    if (
        config is None
        or not isinstance(config, dict)
        or "notification_handlers" not in config
        or not isinstance(config["notification_handlers"], list)
    ):
        raise ConfigError("malformed configuration")

    return config


def get_window_datetime(window_hours: int) -> datetime:
    """Get API compatible timestamp for
    CHECK_EVERY_HOURS number of hours in the future"""
    if window_hours <= 0:
        raise ValueError("window_hours must be a positive int")
    return datetime.now(pytz.utc) + timedelta(hours=window_hours)


def get_upcoming_launches(window_hours: int) -> dict[str, Any] | None:
    """call ll2 get upcoming launch library"""
    window = get_window_datetime(window_hours)
    return get_upcoming_launches_within_window(window)


def send_notification(
    launches: dict[str, Any],
    notification_handlers: list[NotificationHandler],
):
    """Build and send a notification using the provided launches,
    subject_render, body_renderer, and notification service"""
    logging.info(
        "%s upcoming launches, attempting to send notifications",
        launches["count"],
    )

    # attempt to send the notification
    try:
        for notification_handler in notification_handlers:
            notification_handler.send(launches)
    except NotificationError as ex:
        logging.error("Error encounted attempting to send notification: %s", ex)
