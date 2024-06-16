"""
# Space Launch Notifications - Module

A tool/library which checks for upcoming space launches via an API
and can send a notifications if there are any upcoming space launch events.

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from datetime import datetime, timedelta
from typing import Any

import pytz
from loguru import logger

from launches.errors import NotificationError

from .ll2 import get_upcoming_launches_within_window
from .notifications.handlers import NotificationHandler


def get_window_datetime(window_hours: int) -> datetime:
    """Get API compatible timestamp for
    CHECK_EVERY_HOURS number of hours in the future"""
    if window_hours <= 0:
        raise ValueError("window_hours must be a positive int")
    return datetime.now(pytz.utc) + timedelta(hours=window_hours)


def get_upcoming_launches(window_hours: int) -> dict[str, Any]:
    """call ll2 get upcoming launch library"""
    window = get_window_datetime(window_hours)
    return get_upcoming_launches_within_window(window)


def send_notification(
    launches: dict[str, Any],
    notification_handlers: list[NotificationHandler],
):
    """Build and send a notification using the provided launches,
    subject_render, body_renderer, and notification service"""
    logger.info(
        "{} upcoming launches, attempting to send notifications",
        launches["count"],
    )
    logger.debug("configured notification handlers {}", notification_handlers)

    # attempt to send the notification
    try:
        for notification_handler in notification_handlers:
            notification_handler.send(launches)
    except NotificationError as ex:
        logger.error("Error encounted attempting to send notification: {}", ex)
