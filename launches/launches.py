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
from typing import Any, Optional

import schedule
from loguru import logger

from launches.cache import LaunchCache
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
    cache: Optional[LaunchCache] = None,
) -> None:
    """Run a check for upcoming launches and send notifications if needed.

    Args:
        window_hours (int): Time window in hours to look for upcoming launches.
        notification_handlers (Sequence[NotificationHandler]): Handlers to use for notifications.
        ll2_client (LaunchLibrary2Client): Client for accessing the Launch Library API.
        cache (Optional[LaunchCache]): Cache instance to filter unchanged launches.
            If provided, only changed launches will trigger notifications.
    """
    logger.info("Checking for upcoming launches within a {} hour window", window_hours)

    try:
        # Get the window end time
        window_start_lt = datetime.now(tz=timezone.utc) + timedelta(hours=window_hours)

        # Get launches from the API
        launches = ll2_client.get_upcoming_launches_within_window(window_start_lt)

        # Filter for changes if cache is enabled
        if cache is not None:
            launches = cache.get_changed_launches(launches)
            logger.info(
                "Changed launches: {}/{}", launches["count"], "total count from original response"
            )
    except LaunchesError as ex:
        logger.exception("Exception occured while attempting to get upcoming launches", ex)
        return

    if launches["count"] > 0:
        # Send notification only if there are launches to report
        logger.info("Found {} launches to report", launches["count"])
        send_notification(launches, notification_handlers)
    else:
        logger.info(f"No new or changed launches found within a {window_hours} hour window.")


def run_upcoming_launches_daily(
    search_window_hrs: int,
    specific_times: list[str],
    tz: str,
    notification_handlers: list[NotificationHandler],
    ll2_client: LaunchLibrary2Client,
    cache: Optional[LaunchCache] = None,
) -> None:
    """
    Schedules and runs tasks to check for upcoming rocket launches.

    This function sets up a schedule to check for upcoming launches at specific times
    each day, using the provided search window and notification handlers. It does NOT
    perform an immediate check upon invocation.

    Args:
        search_window_hrs (int): The number of hours ahead to search for upcoming launches.
        specific_times (list[str]): A list time strings in "HH:MM" format
        tz (str): The time zone used for scheduling (must be IANA timezone like "America/Chicago")
        notification_handlers (list[NotificationHandler]): A list of notification handler
            instances to handle notifications for upcoming launches.
        ll2_client (LaunchLibrary2Client): An instance of the LaunchLibrary2Client to
            interact with the launch library API.
        cache (Optional[LaunchCache], optional): Cache instance to filter unchanged launches.
            Defaults to None.

    Returns:
        None
    """
    for time_str in specific_times:
        schedule.every().day.at(time_str, tz).do(
            check_for_upcoming_launches, search_window_hrs, notification_handlers, ll2_client, cache
        )

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        return


def run_upcoming_launches_periodic(
    window_hours: int,
    repeat_hours: int,
    notification_handlers: list[NotificationHandler],
    ll2_client: LaunchLibrary2Client,
    cache: Optional[LaunchCache] = None,
) -> None:
    """
    Periodically checks for upcoming rocket launches and sends notifications.

    This function schedules periodic tasks to check for upcoming rocket launches
    within a specified time window and sends notifications using the provided
    notification handlers. It also performs an immediate check upon invocation.

    Args:
        window_hours (int): The time window (in hours) to look ahead for upcoming launches.
        repeat_hours (int): The interval (in hours) at which to repeat the periodic checks.
        notification_handlers (list[NotificationHandler]): A list of notification handlers
            to process and send notifications for upcoming launches.
        ll2_client (LaunchLibrary2Client): An instance of the Launch Library 2 client
            used to fetch launch data.
        cache (Optional[LaunchCache], optional): Cache instance to filter unchanged launches.
            Defaults to None.

    Returns:
        None
    """

    schedule.every(repeat_hours).hours.do(
        check_for_upcoming_launches, window_hours, notification_handlers, ll2_client, cache
    )

    # run a check immediately
    check_for_upcoming_launches(window_hours, notification_handlers, ll2_client, cache)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        return
