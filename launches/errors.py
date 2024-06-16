class LaunchesException(Exception):
    "Base Launches Library Exception"


class ConfigError(LaunchesException):
    "Configuration Error"


class LL2RequestError(LaunchesException):
    """Launches LL2 API Error"""


class NotificationError(LaunchesException):
    """notification service error"""
