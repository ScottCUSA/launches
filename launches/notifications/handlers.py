"""Space Launch Notifications - Notification Handler Module

This module composes NotificationRenderers and NotificationServices and
handles construction of both from the projects configuration

Copyright ©️ 2023 Scott Cummings
License: GNU General Public License V3
         https://www.gnu.org/licenses/gpl-3.0.en.html
"""

from dataclasses import dataclass
import logging
import sys
from typing import Any
from .templates import get_notification_renderer, NotificationRenderer
from .services import (
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
    logging.debug("loading notification handlers")
    notification_handlers: list[NotificationHandler] = []
    for handler_config in handler_configs:
        if "service" not in handler_config or "parameters" not in handler_config:
            logging.error("Handler config missing required fields")
            sys.exit(1)
        try:
            renderer_name = (
                handler_config["render"] if "render" in handler_config else ""
            )
            renderer = get_notification_renderer(renderer_name)
            service = get_notification_service(handler_config)
            notification_handlers.append(NotificationHandler(renderer, service))
        except (ValueError, KeyError) as ex:
            logging.error("Unable to load notification handlers: %s", ex)
            sys.exit(1)

    if len(notification_handlers) == 0:
        logging.error("Unable to load any notification handlers")
        sys.exit(1)

    return notification_handlers
