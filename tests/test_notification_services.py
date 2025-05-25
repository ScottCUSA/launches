"""unittests for launches.notifications.services

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import base64
from unittest.mock import patch

from launches.config import NotificationHandlerConfig
from launches.notifications.services import (
    SMTPEmaiLNotificationService,
    StdOutNotificationService,
    get_notification_service,
)


def test_get_notification_service_stdout():
    """get_notification_service should return a StdOutNotificationService if service is stdout"""
    service_config = NotificationHandlerConfig(service="stdout", renderer="text", parameters={})

    with patch("sys.exit") as mock_exit:
        notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, StdOutNotificationService)
    assert mock_exit.call_count == 0


def test_get_notification_service_email():
    """get_notification_service should return an EmailNotificationService if service is email"""
    service_config = NotificationHandlerConfig(
        service="email",
        renderer="text",
        parameters={
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "use_tls": True,
            "username": "user@example.com",
            "password": base64.b64encode(b"password123").decode("utf-8"),
            "sender": "user@example.com",
            "recipients": "user@example.com",
        },
    )

    with patch("sys.exit") as mock_exit:
        notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, SMTPEmaiLNotificationService)
    assert mock_exit.call_count == 0


def test_get_notification_service_unknown_service():
    """get_notification_service should exit if service is unknown"""
    service_config = NotificationHandlerConfig(
        service="unknown",
        renderer="text",
        parameters={},
    )

    with patch("sys.exit") as mock_exit:
        get_notification_service(service_config)

    assert mock_exit.call_count == 1
