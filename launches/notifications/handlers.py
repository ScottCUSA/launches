"""Space Launch Notifications - Notification Handler Module

This module composes NotificationRenderers and NotificationServices and
handles construction of both from the projects configuration

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from launches.config import NotificationHandlerConfig
from launches.errors import ConfigError
from launches.notifications.renderers import (
    NotificationRenderer,
    get_notification_renderer,
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
        text_body = self.renderer.render_text_body(launches)
        formatted_body = self.renderer.render_formatted_body(launches)
        self.service.send(subject, text_body, formatted_body)


def get_notification_handlers(
    handler_configs: list[NotificationHandlerConfig],
) -> list[NotificationHandler]:
    """This function returns a list notification handlers built from
    the project configuration
    """
    logger.debug("loading notification handlers")
    notification_handlers: list[NotificationHandler] = []
    for handler_config in handler_configs:
        renderer_name = handler_config.renderer
        renderer = get_notification_renderer(renderer_name)
        service = get_notification_service(handler_config)
        notification_handlers.append(NotificationHandler(renderer, service))

    if len(notification_handlers) == 0:
        logger.error("Unable to load any notification handlers")
        raise ConfigError()

    return notification_handlers
