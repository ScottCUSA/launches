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

from launches.cache import LaunchCache
from launches.config import load_config
from launches.launches import (
    check_for_upcoming_launches,
    run_upcoming_launches_daily,
    run_upcoming_launches_periodic,
)
from launches.ll2 import LaunchLibrary2Client
from launches.notifications.handlers import (
    get_notification_handlers,
)

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_CHECK_INTERVAL_HOURS = 24  # default hours between checks for periodic upcoming launches
DEFAULT_FORECAST_WINDOW_HOURS = 48  # default hours in future to check for upcoming launches
DEFAULT_DAILY_CHECK_TIMES = ["07:00", "19:00"]  # default times to check for upcoming launches
DEFAULT_TIMEZONE = "America/Chicago"  # default daily schedule timezone
DEFAULT_CACHE_DIR = "./.launches_cache"


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
        help=(
            "specify the time window to find launches "
            f"# Default: {DEFAULT_FORECAST_WINDOW_HOURS} hours"
        ),
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
        help='specify the ll2 environment # Default "prod"',
    )
    parser.add_argument(
        "--cache-dir",
        metavar="CACHE_DIR",
        dest="cache_dir",
        help="specify the directory to store cache files # Default: ./",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        dest="no_cache",
        help="disable caching of launch data",
    )
    arg_group = parser.add_argument_group("service mode arguments")
    arg_group.add_argument(
        "--periodic",
        action="store_true",
        dest="periodic",
        help="run checks periodically rather than at specific times",
    )
    arg_group.add_argument(
        "--interval",
        metavar="INTERVAL",
        type=int,
        dest="interval",
        help=f"specify the check inverval (hours) # Default: {DEFAULT_CHECK_INTERVAL_HOURS} hours",
    )
    arg_group.add_argument(
        "--times",
        metavar="TIMES",
        dest="times",
        action="append",
        help=(
            'specify one or more daily check times format: "HH:MM" '
            f"# Default: {', '.join(DEFAULT_DAILY_CHECK_TIMES)}"
        ),
    )
    arg_group.add_argument(
        "--timezone",
        metavar="TIMEZONE",
        dest="timezone",
        help=f"specify the IANA timezone for times # Default: {DEFAULT_TIMEZONE} ",
    )
    return parser.parse_args()


def configure_logging(args):
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


def get_search_window(config, args):
    """
    Determines the search window duration based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.window)
    2. Configuration value (config.search_window_hours)
    3. Default value (DEFAULT_FORECAST_WINDOW_HOURS)

    Args:
        config: An object that may contain the attribute `search_window_hours`.
        args: An object that contains the attribute `window`.

    Returns:
        int: The search window duration in hours.
    """
    if args.window is not None:
        return args.window

    if hasattr(config, "search_window_hours") and config.search_window_hours is not None:
        return config.search_window_hours

    return DEFAULT_FORECAST_WINDOW_HOURS


def get_cache_directory(config, args):
    """
    Retrieves the cache directory based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.cache_dir)
    2. Configuration value (config.cache_directory)
    3. Default value ("./launches_cache")

    Args:
        config (object): The configuration object which may contain a
                         `cache_directory` attribute.
        args: An object containing command-line arguments, including the
              `cache_dir` attribute.

    Returns:
        str: The path to the cache directory.
    """
    if args.cache_dir is not None:
        return args.cache_dir

    if hasattr(config, "cache_directory") and config.cache_directory is not None:
        return config.cache_directory

    return DEFAULT_CACHE_DIR


def get_cache(config, args):
    """
    Creates and returns a LaunchCache instance if caching is enabled in the given configuration.

    Priority order for cache enabling:
    1. Command line argument (args.no_cache) - disables cache if true
    2. Configuration value (config.cache_enabled)

    Args:
        config: An object containing configuration attributes. It should have a
                'cache_enabled' attribute to determine if caching is enabled.
        args: Command line arguments (used for cache directory configuration).

    Returns:
        LaunchCache: An instance of LaunchCache with the cache directory set, if caching
                     is enabled in the configuration and not disabled by command line.
        None: If caching is not enabled in the configuration or disabled by command line.
    """
    # If --no-cache is specified, disable caching regardless of config
    if args.no_cache:
        return None

    # Otherwise, check the configuration
    return (
        LaunchCache(cache_dir=get_cache_directory(config, args), enabled=True)
        if hasattr(config, "cache_enabled") and config.cache_enabled
        else None
    )


def get_time_zone(config, args):
    """
    Determines the time zone to use based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.timezone)
    2. Configuration value (config.time_zone)
    3. Default value (DEFAULT_TIMEZONE)

    Args:
        config: An object that may contain a `time_zone` attribute.
        args: An object that may contain a `timezone` attribute.

    Returns:
        str: The time zone to be used.
    """
    if args.timezone is not None:
        return args.timezone

    if hasattr(config, "time_zone") and config.time_zone is not None:
        return config.time_zone

    return DEFAULT_TIMEZONE


def get_check_times(config, args):
    """
    Determines the check times based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.times)
    2. Configuration value (config.daily_check_times)
    3. Default value (DEFAULT_DAILY_CHECK_TIMES)

    Args:
        config: An object containing configuration settings, including
                `daily_check_times`.
        args: An object containing command-line arguments, including `times`.

    Returns:
        list: The check times as specified in arguments, configuration, or default.
    """
    if args.times is not None:
        return args.times

    if hasattr(config, "daily_check_times") and config.daily_check_times is not None:
        return config.daily_check_times

    return DEFAULT_DAILY_CHECK_TIMES


def get_search_interval(config, args):
    """
    Determines the search interval based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.interval)
    2. Configuration value (config.search_repeat_hours)
    3. Default value (DEFAULT_CHECK_INTERVAL_HOURS)

    Args:
        config: An object containing configuration settings, including the
                `search_repeat_hours` attribute.
        args: An object containing command-line arguments, including the
              `interval` attribute.

    Returns:
        int: The search interval in hours.
    """
    if args.interval is not None:
        return args.interval

    if hasattr(config, "search_repeat_hours") and config.search_repeat_hours is not None:
        return config.search_repeat_hours

    return DEFAULT_CHECK_INTERVAL_HOURS


def get_periodic(config, args):
    """
    Determines the periodic value based on command line arguments,
    configuration settings, and default values.

    Priority order:
    1. Command line argument (args.periodic)
    2. Configuration value (config.periodic)
    3. Default is False if neither is set

    Args:
        config: An object containing configuration settings, expected to have a 'periodic' attribute.
        args: An object containing command-line arguments, expected to have a 'periodic' attribute.

    Returns:
        bool: The periodic value according to priority order.
    """
    if args.periodic:
        return True

    if hasattr(config, "periodic") and config.periodic:
        return True

    return False


def cli():
    """command line interface entrypoint"""

    # handle tool argument parsing
    args = parse_args()
    configure_logging(args)

    logger.debug("args: {}", args)

    # load config
    config = load_config(args.config)
    logger.debug("config: {}", config)

    notification_handlers = get_notification_handlers(config.notification_handlers)
    env = args.env

    # Create Launch Library client
    ll2_client = LaunchLibrary2Client(env=env)

    window_hours = get_search_window(config, args)
    cache = get_cache(config, args)
    time_zone = get_time_zone(config, args)
    times = get_check_times(config, args)
    search_interval = get_search_interval(config, args)
    periodic = get_periodic(config, args)

    if not args.service:
        check_for_upcoming_launches(window_hours, notification_handlers, ll2_client, None)
        return

    if periodic:
        logger.info(
            "Starting periodic launch checks every {} hours with {}h window",
            search_interval,
            window_hours,
        )
        run_upcoming_launches_periodic(
            window_hours, search_interval, notification_handlers, ll2_client, cache
        )
    else:
        logger.info(
            "Starting scheduled launch checks at {} ({}) with {}h window",
            times,
            time_zone,
            window_hours,
        )
        run_upcoming_launches_daily(
            window_hours, times, time_zone, notification_handlers, ll2_client, cache
        )
