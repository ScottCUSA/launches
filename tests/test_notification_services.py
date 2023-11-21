"""unittests for launches.notifications.services

Copyright ©️ 2023 Scott Cummings

"""
from unittest.mock import patch

from launches.notifications.services import (
    EmailNotificationService,
    StdOutNotificationService,
    get_notification_service,
)
import base64


def test_get_notification_service_stdout():
    service_config = {
        "service": "stdout",
        "renderer": "text",
        "parameters": {},
    }

    with patch("sys.exit") as mock_exit:
        notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, StdOutNotificationService)
    assert mock_exit.call_count == 0


def test_get_notification_service_email():
    service_config = {
        "service": "email",
        "renderer": "text",
        "parameters": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "use_tls": True,
            "username": "user@example.com",
            "password": base64.b64encode(b"password123").decode("utf-8"),
            "sender": "user@example.com",
            "recipients": "user@example.com",
        },
    }

    with patch("sys.exit") as mock_exit:
        notification_service = get_notification_service(service_config)

    assert isinstance(notification_service, EmailNotificationService)
    assert mock_exit.call_count == 0


def test_get_notification_service_unknown_service():
    service_config = {
        "service": "unknown",
        "renderer": "text",
        "parameters": {},
    }

    with patch("sys.exit") as mock_exit, patch("logging.error") as mock_logging_error:
        get_notification_service(service_config)

    assert mock_exit.call_count == 1
    assert mock_logging_error.call_count == 1


def test_get_notification_service_missing_fields():
    service_config = {
        "renderer": "text",
        "parameters": {},
    }

    with patch("sys.exit") as mock_exit, patch("logging.error") as mock_logging_error:
        get_notification_service(service_config)

    assert mock_exit.call_count == 2
    assert mock_logging_error.call_count == 2
