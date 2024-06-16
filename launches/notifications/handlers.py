"""Space Launch Notifications - Notification Handler Module

This module composes NotificationRenderers and NotificationServices and
handles construction of both from the projects configuration

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from dataclasses import dataclass
from loguru import logger
import sys
from typing import Any
from launches.notifications.templates import (
    get_notification_renderer,
    NotificationRenderer,
)
from launches.notifications.services import (
    NotificationService,
    get_notification_service,
)


@dataclass
class NotificationHandler:
    """Composition of a NotificationRender and a NotificationService.
    Renders and sends a notification from a launches dict"""

    renderer: NotificationRenderer
    service: NotificationService

    def send(self, launches: dict[str, Any]) -> None:
        """render and send a notification from the launches dict"""
        subject = self.renderer.render_subject(launches)
        body = self.renderer.render_body(launches)
        self.service.send(subject, body)


def get_notification_handlers(
    handler_configs: list[dict[str, Any]],
) -> list[NotificationHandler]:
    """This function returns a list notification handlers built from
    the project configuration

    Expected Format:
    service_configs = [
        {
            "service": "stdout",
            "renderer":"text",   // optional
            "parameters": {}
        }
    ]

    """
    logger.debug("loading notification handlers")
    notification_handlers: list[NotificationHandler] = []
    for handler_config in handler_configs:
        if "service" not in handler_config or "parameters" not in handler_config:
            logger.error("Handler config missing required fields")
            sys.exit(1)
        try:
            renderer_name = handler_config["renderer"] if "renderer" in handler_config else ""
            renderer = get_notification_renderer(renderer_name)
            service = get_notification_service(handler_config)
            notification_handlers.append(NotificationHandler(renderer, service))
        except (ValueError, KeyError) as ex:
            logger.error("Unable to load notification handlers: {}", ex)
            sys.exit(1)

    if len(notification_handlers) == 0:
        logger.error("Unable to load any notification handlers")
        sys.exit(1)

    return notification_handlers
