"""
# Space Launch Notifications - Module

A tool/library which checks for upcoming space launches via an API
and can send a notifications if there are any upcoming space launch events.

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import time
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any

import schedule
from loguru import logger

from launches.errors import LaunchesError, NotificationError

from .ll2 import LaunchLibrary2Client
from .notifications.handlers import NotificationHandler


def get_window_datetime(window_hours: int) -> datetime:
    """Get API compatible timestamp for
    CHECK_EVERY_HOURS number of hours in the future"""
    if window_hours <= 0:
        raise ValueError("window_hours must be a positive int")
    return datetime.now(timezone.utc) + timedelta(hours=window_hours)


def get_upcoming_launches(window_hours: int, env: str = "prod") -> dict[str, Any]:
    """call ll2 get upcoming launch library"""
    window = get_window_datetime(window_hours)
    ll2_client = LaunchLibrary2Client(env)
    return ll2_client.get_upcoming_launches_within_window(window)


def send_notification(
    launches: dict[str, Any],
    notification_handlers: Sequence[NotificationHandler],
) -> None:
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


def check_for_upcoming_launches(
    window_hours: int,
    notification_handlers: Sequence[NotificationHandler],
    ll2_client: LaunchLibrary2Client,
) -> None:
    """run a check for upcoming launches"""
    logger.info("Checking for upcoming launches within a {} hour window", window_hours)

    from datetime import datetime, timedelta

    try:
        window_start_lt = datetime.now(tz=timezone.utc) + timedelta(hours=window_hours)
        launches = ll2_client.get_upcoming_launches_within_window(window_start_lt)
    except LaunchesError as ex:
        logger.exception("Exception occured while attempting to get upcoming launches", ex)
        return

    if launches["count"] > 0:
        # render subject and body for notification
        send_notification(launches, notification_handlers)
    else:
        logger.info(f"No upcoming launches found within a {window_hours} hour window.")


def check_for_upcoming_launches_scheduled(
    window_hours: int,
    repeat_hours: int,
    notification_handlers: list[NotificationHandler],
    ll2_client: LaunchLibrary2Client,
) -> None:
    """run a check for upcoming launches in service mode"""

    schedule.every(repeat_hours).hours.do(
        check_for_upcoming_launches, window_hours, notification_handlers, ll2_client
    )

    # run a check immediately
    check_for_upcoming_launches(window_hours, notification_handlers, ll2_client)

    while True:
        schedule.run_pending()
        time.sleep(1)
