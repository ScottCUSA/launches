"""unittests for launches.notifications.handlers

Copyright ©️ 2023 Scott Cummings
License: GNU General Public License V3
         https://www.gnu.org/licenses/gpl-3.0.en.html
"""
import pytest
from unittest.mock import Mock, patch
from launches.notifications.handlers import (
    NotificationHandler,
    get_notification_handlers,
)
from test_ll2 import VALID_LAUNCHES_DICT

@pytest.fixture
def handler():
    renderer = Mock()
    service = Mock()
    return NotificationHandler(renderer, service)


def test_send(handler):
    handler.send(VALID_LAUNCHES_DICT)
    handler.renderer.render_subject.assert_called_once_with(VALID_LAUNCHES_DICT)
    handler.renderer.render_body.assert_called_once_with(VALID_LAUNCHES_DICT)
    handler.service.send.assert_called_once()


@patch("launches.notifications.handlers.get_notification_renderer")
@patch("launches.notifications.handlers.get_notification_service")
def test_get_notification_handlers(
    get_notification_service_mock, get_notification_renderer_mock
):
    handler_configs = [{"service": "stdout", "renderer": "text", "parameters": {}}]
    get_notification_handlers(handler_configs)
    get_notification_renderer_mock.assert_called_once()
    get_notification_service_mock.assert_called_once()
