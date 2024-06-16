"""Space Launch Notifications - CLI Entry Point

A tool/library which checks for upcoming space launches via an API
and can send a notifications if there are any upcoming space launch events.

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import argparse
import os
import sys
import time

import schedule
from loguru import logger

from launches.config import load_config
from launches.errors import LaunchesError
from launches.launches import (
    get_upcoming_launches,
    send_notification,
)
from launches.notifications.handlers import (
    NotificationHandler,
    get_notification_handlers,
)
from launches.notifications.renderers import JinjaRenderer
from launches.notifications.services import StdOutNotificationService

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_REPEAT_HOURS = 24  # number of hours between checks for upcoming launches
DEFAULT_WINDOW_HOURS = 24  # number of hours in future to check for upcoming launches
SECONDS_IN_HOUR = 3600  # time between requests in seconds
REQUEST_ERROR_COOLDOWN = 600  # time between requests if there is an error


def get_env_bool(env_var: str) -> bool:
    """get a boolean value from an environment variable"""
    if env_var not in os.environ:
        return False
    return os.environ[env_var].lower().strip() in ["t", "true", "1"]


def get_env_with_default(env_var: str, default: str) -> str:
    """get an environment variable with a default value"""
    if env_var not in os.environ:
        return default
    return os.environ[env_var]


def parse_args() -> dict:
    """parse arguments and return them as a dict"""
    parser = argparse.ArgumentParser(
        description="A tool which checks for upcoming space launches "
        "using the free tier of the space launch library 2 API. "
        "More information about the API can be found here: https://thespacedevs.com/llapi"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug_logging",
        default=get_env_bool("LAUNCHES_DEBUG"),
        help="enable debug logging",
    )
    parser.add_argument(
        "-w",
        metavar="WINDOW",
        dest="window",
        type=int,
        help="find launches within WINDOW hours",
        default=DEFAULT_WINDOW_HOURS,
    )
    parser.add_argument(
        "--notif",
        action="store_true",
        dest="normal_notif",
        help="send a notification if upcoming launches within WINDOW (ignored in service mode)",
    )
    parser.add_argument(
        "--service-mode",
        action="store_true",
        dest="service_mode",
        help="repeatedly check for upcoming launches until user exits with `Ctrl+C`",
    )
    parser.add_argument(
        "-r",
        metavar="REPEAT",
        type=int,
        dest="repeat",
        help="repeat checks ever REPEAT hours (service mode only)",
        default=DEFAULT_REPEAT_HOURS,
    )
    parser.add_argument(
        "--config-path",
        type=str,
        dest="config_path",
        help=f"notification service config path default=`{DEFAULT_CONFIG_PATH}`",
        default=get_env_with_default("LAUNCHES_CONFIG", DEFAULT_CONFIG_PATH),
    )
    args = parser.parse_args()
    return vars(args)


def check_for_upcoming_launches(
    window_hours: int,
    notification_handlers: list[NotificationHandler],
) -> None:
    """run a check for upcoming launches"""
    logger.info("Checking for upcoming launches within a {} hour window", window_hours)

    try:
        launches = get_upcoming_launches(window_hours)
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
) -> None:
    """run a check for upcoming launches in service mode"""

    schedule.every(repeat_hours).hours.do(
        check_for_upcoming_launches, window_hours, notification_handlers
    )

    # run a check immediately
    check_for_upcoming_launches(window_hours, notification_handlers)

    while True:
        schedule.run_pending()
        time.sleep(1)


def cli():
    """command line interface entrypoint"""

    # handle tool argument parsing
    args = parse_args()

    # configure logging
    logger.remove()
    if args["debug_logging"]:
        # debugging level override
        logger.add(sys.stderr, level="DEBUG")
    elif args["service_mode"]:
        # configure info level logging by default in service mode
        logger.add(sys.stderr, level="INFO")
    else:
        # configure warning level logging otherwise
        logger.add(sys.stderr, level="WARNING")

    logger.debug("args: {}", args)

    # load config
    config = load_config(args["config_path"])
    window_hours = (
        config.search_window_hours if config.search_window_hours is not None else args["window"]
    )
    repeat_hours = (
        config.search_repeat_hours if config.search_repeat_hours is not None else args["repeat"]
    )

    if args["service_mode"] or args["normal_notif"]:
        notification_handlers = get_notification_handlers(config.notification_handlers)
    else:
        notification_handlers = [NotificationHandler(JinjaRenderer(), StdOutNotificationService())]

    if args["service_mode"]:
        check_for_upcoming_launches_scheduled(window_hours, repeat_hours, notification_handlers)
    else:
        check_for_upcoming_launches(window_hours, notification_handlers)
