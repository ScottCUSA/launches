"""Space Launch Notifications - Notifications Services Module

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import sys

from loguru import logger

from launches.config import NotificationHandlerConfig
from launches.notifications.services.gmail import GmailNotificationService
from launches.notifications.services.protocol import NotificationService
from launches.notifications.services.smtp_email import SMTPEmaiLNotificationService
from launches.notifications.services.stdout import StdOutNotificationService


def get_notification_service(
    service_config: NotificationHandlerConfig,
) -> NotificationService:
    """This function returns a notification service built from
    the service configuration

    Expected Format:
    {
        "service": "stdout",
        "renderer":"text",   // ignored
        "parameters": {}
    }

    This function will exit the tool if an error is encountered loading
    the service, or required configuration parameters are missing.
    """
    try:
        logger.info(
            "Attempting to load notification service: {}",
            service_config.service,
        )
        match service_config.service:
            case "email":
                return SMTPEmaiLNotificationService(**service_config.parameters)
            case "gmail":
                return GmailNotificationService(**service_config.parameters)
            case "stdout":
                return StdOutNotificationService()
            # case "gmail":
            #     return GmailNotificationService(**service_config.parameters)
            case _:
                logger.error(
                    "Unknown notification service {}",
                    service_config.service,
                )
                sys.exit(1)
    except (ValueError, TypeError, KeyError) as ex:
        logger.error("Unable to load notification service: {}", ex)
        sys.exit(1)
