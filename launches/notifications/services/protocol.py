"""Space Launch Notifications - NotificationService Protocol

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from typing import Protocol


class NotificationService(Protocol):
    """The protocol a notification service needs to follow"""

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """send notification"""
        raise NotImplementedError()

    def __repr__(self) -> str:
        raise NotImplementedError()
