"""unittests for launches.notifications.handlers

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from unittest.mock import Mock, patch
import pytest
from launches.notifications.handlers import (
    NotificationHandler,
    get_notification_handlers,
)


@pytest.fixture
def handler():
    """return a NotificationHandler with mocks for renderer and service"""
    renderer = Mock()
    service = Mock()
    return NotificationHandler(renderer, service)


def test_send(handler, valid_launches):  # pylint: disable=redefined-outer-name
    """send should call the renderer and service"""
    handler.send(valid_launches)
    handler.renderer.render_subject.assert_called_once_with(valid_launches)
    handler.renderer.render_text_body.assert_called_once_with(valid_launches)
    handler.renderer.render_formatted_body.assert_called_once_with(valid_launches)
    handler.service.send.assert_called_once()


@patch("launches.notifications.handlers.get_notification_renderer")
@patch("launches.notifications.handlers.get_notification_service")
def test_get_notification_handlers(get_notification_service_mock, get_notification_renderer_mock):
    """get_notification_handlers should return a list of NotificationHandlers"""
    handler_configs = [{"service": "stdout", "renderer": "text", "parameters": {}}]
    get_notification_handlers(handler_configs)
    get_notification_renderer_mock.assert_called_once()
    get_notification_service_mock.assert_called_once()
