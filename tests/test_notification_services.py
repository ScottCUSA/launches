"""unittests for launches.notifications.services

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import base64

import pytest

from launches.config import NotificationHandlerConfig
from launches.errors import ConfigError
from launches.notifications.services import (
    SMTPEmaiLNotificationService,
    StdOutNotificationService,
    get_notification_service,
)


def test_get_notification_service_stdout():
    """get_notification_service should return a StdOutNotificationService if service is stdout"""
    service_config = NotificationHandlerConfig(service="stdout", renderer="text", parameters={})

    notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, StdOutNotificationService)


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

    notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, SMTPEmaiLNotificationService)


def test_get_notification_service_unknown_service():
    """get_notification_service should raise ValueError if service is unknown"""
    service_config = NotificationHandlerConfig(
        service="unknown",
        renderer="text",
        parameters={},
    )

    with pytest.raises(ConfigError):
        get_notification_service(service_config)
