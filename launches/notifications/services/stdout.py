"""Space Launch Notifications - StdOut Notification Service

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from loguru import logger


class StdOutNotificationService:
    """A "dummy" notification service which just prints to stdout"""

    def __init__(self, *_args, **_kwargs) -> None:
        logger.info("Initialized {}", self)

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """print notification to stdout"""
        logger.info("Sending StdOut Notification")
        print(subject)
        print(msg)

    def __repr__(self) -> str:
        return "StdOutNotificationService()"
