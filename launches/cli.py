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

from loguru import logger

from launches.config import load_config
from launches.launches import check_for_upcoming_launches, check_for_upcoming_launches_scheduled
from launches.ll2 import LaunchLibrary2Client
from launches.notifications.handlers import (
    get_notification_handlers,
)

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_REPEAT_HOURS = 24  # number of hours between checks for upcoming launches
DEFAULT_WINDOW_HOURS = 48  # number of hours in future to check for upcoming launches
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


def parse_args() -> argparse.Namespace:
    """Configure ArgParse and Parse CLI Arguments"""
    parser = argparse.ArgumentParser(
        description="A tool which checks for upcoming space launches "
        "using the space launch library API. "
        "More information about the API can be found here:"
        " https://thespacedevs.com/llapi"
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
        "--config",
        type=str,
        dest="config",
        help=f"specify the config file path # Default `{DEFAULT_CONFIG_PATH}`",
        default=get_env_with_default("LAUNCHES_CONFIG", DEFAULT_CONFIG_PATH),
    )
    parser.add_argument(
        "--window",
        metavar="WINDOW",
        dest="window",
        type=int,
        help=f"specify the time window to find launches # Default: {DEFAULT_WINDOW_HOURS} hours",
        default=DEFAULT_WINDOW_HOURS,
    )
    parser.add_argument(
        "--service",
        action="store_true",
        dest="service",
        help="run as a service checking for upcoming launches repeatedly",
    )
    parser.add_argument(
        "--env",
        choices=("dev", "prod"),
        dest="env",
        default="prod",
        help="specify the ll2 environment",
    )
    arg_group = parser.add_argument_group("service mode arguments")
    arg_group.add_argument(
        "--repeat",
        metavar="REPEAT",
        type=int,
        dest="repeat",
        help=f"specify the frequency of checks # Default: {DEFAULT_REPEAT_HOURS} hours",
        default=DEFAULT_REPEAT_HOURS,
    )
    return parser.parse_args()


def cli():
    """command line interface entrypoint"""

    # handle tool argument parsing
    args = parse_args()

    # configure logging
    logger.remove()
    if args.debug_logging:
        # debugging level override
        logger.add(sys.stderr, level="DEBUG")
    elif args.service:
        # configure info level logging by default in service mode
        logger.add(sys.stderr, level="INFO")
    else:
        # configure warning level logging otherwise
        logger.add(sys.stderr, level="WARNING")

    logger.debug("args: {}", args)

    # load config
    config = load_config(args.config)
    logger.debug("config: {}", config)

    window_hours = (
        config.search_window_hours if config.search_window_hours is not None else args.window
    )
    repeat_hours = (
        config.search_repeat_hours if config.search_repeat_hours is not None else args.repeat
    )
    env = args.env
    ll2_client = LaunchLibrary2Client(env)

    notification_handlers = get_notification_handlers(config.notification_handlers)

    if args.service:
        check_for_upcoming_launches_scheduled(
            window_hours, repeat_hours, notification_handlers, ll2_client
        )
    else:
        check_for_upcoming_launches(window_hours, notification_handlers, ll2_client)
