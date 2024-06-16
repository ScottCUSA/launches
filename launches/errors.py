"""
# Space Launch Notifications - Errors Module

# README.md
See the readme for additional documentation on the tool/service

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

class LaunchesException(Exception):
    """Base Launches Library Exception"""


class ConfigError(LaunchesException):
    """Configuration Error"""


class LL2RequestError(LaunchesException):
    """Launches LL2 API Error"""


class NotificationError(LaunchesException):
    """notification service error"""
