"""
# Space Launch Notifications

A tool/service which checks for upcoming space launches
and sends a notification if there are any upcoming space launch events.

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2023 Scott Cummings

"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
import time
from typing import Any

import pytz

from .ll2 import get_upcoming_launches_within_window
from .notifications.templates import TextRenderer
from .notifications.services import NotificationError, StdOutNotificationService
from .notifications.handlers import NotificationHandler, get_notification_handlers

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_REPEAT_HOURS = 24  # number of hours between checks for upcoming launches
DEFAULT_WINDOW_HOURS = 24  # number of hours in future to check for upcoming launches
SECONDS_IN_HOUR = 3600  # time between requests in seconds
REQUEST_ERROR_COOLDOWN = 600  # time between requests if there is an error


class ConfigError(Exception):
    """project configuration error"""


def load_config(config_path: str) -> dict[str, Any]:
    """load project config from JSON
    Example JSON:
    {
        "notification_handlers": [
            {
                "service": "stdout",
                "render": "text",
                "parameters": {}
            },
            {
                "service":"email",
                "render": "text",
                "parameters":{
                    "smtp_server":"smtp-server",
                    "smtp_port": 587,
                    "smtp_username":"",
                    "smtp_password":"",
                    "email_sender":"",
                    "email_recipients": ["",""]
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
        "--normal-mode-notif",
        action="store_true",
        dest="normal_notif",
        help="send a notification if upcoming launches within WINDOW in normal mode",
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


def run_normal_mode(
    args: dict[str, Any],
    notification_handlers: list[NotificationHandler],
) -> None:
    """run in "normal" mode"""
    launches = get_upcoming_launches(args["window"])
    if launches is None:
        print("Error attempting to get launches")
        sys.exit(1)

    if launches["count"] > 0:
        # render subject and body for notification
        send_notification(launches, notification_handlers)
    else:
        print(f"No upcoming launches found within {args['window']} hour window")


def run_service_mode(
    args: dict[str, Any],
    notification_handlers: list[NotificationHandler],
) -> None:
    """run space launch notification in service mode"""
    # continue making requests repeatedly until user quits
    while True:
        launches = get_upcoming_launches(args["window"])
        if launches is None:
            # sleep before making another request
            time.sleep(REQUEST_ERROR_COOLDOWN)
            continue

        # if there are upcoming launches send notification
        if launches["count"] > 0:
            send_notification(launches, notification_handlers)
        else:
            logging.info("No upcoming launches found within window")
        # sleep before making another request
        logging.info("Sleeping for %s seconds", SECONDS_IN_HOUR * args["repeat"])
        time.sleep(SECONDS_IN_HOUR * args["repeat"])


def main():
    """entrypoint"""

    # handle tool argument parsing
    args = parse_args()

    # configure logging
    if args["debug_logging"]:
        # debugging level override
        logging.basicConfig(level=logging.DEBUG)
    elif args["service_mode"]:
        # configure info level logging by default in service mode
        logging.basicConfig(level=logging.INFO)
    else:
        # configure warning level logging otherwise
        logging.basicConfig(level=logging.WARNING)

    logging.debug("args: %s", args)

    # load config
    config = load_config(args["config_path"])

    # load notification services from the config if in normal mode
    # with notification enabled or in service mode
    if args["service_mode"] or args["normal_notif"]:
        notification_handlers = get_notification_handlers(
            config["notification_handlers"]
        )
    else:
        notification_handlers = [
            NotificationHandler(TextRenderer(), StdOutNotificationService())
        ]

    if not args["service_mode"]:
        run_normal_mode(args, notification_handlers)
    else:
        run_service_mode(args, notification_handlers)


if __name__ == "__main__":
    main()
