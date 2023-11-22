"""Space Launch Notifications - Notification Templates Module

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""
from datetime import datetime
import logging
from typing import Any, Protocol

import pytz
from jinja2 import Environment, PackageLoader, select_autoescape

from launches.ll2 import LAUNCH_DT_FORMAT

JINJA_ENV = Environment(
    loader=PackageLoader("launches", "templates"), autoescape=select_autoescape()
)
TXT_TEMPLATE = "launches.j2.txt"
BODY_TZ = "US/Central"
BODY_DT_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class NotificationRenderer(Protocol):
    """Launch Notification Renderer Protocol"""

    def render_subject(self, launches: dict[str, Any]) -> str:
        """render subject"""
        raise NotImplementedError()

    def render_body(self, launches: dict[str, Any]) -> str:
        """render body"""
        raise NotImplementedError()


class TextRenderer:
    """Render a Launch Notification Using Text"""

    def __init__(self):
        self.renderer = JINJA_ENV.get_template(TXT_TEMPLATE)
        logging.info("Initialized %s with template: %s", self, TXT_TEMPLATE)

    def render_subject(self, launches: dict[str, Any]) -> str:
        """render text subject"""
        return f"Notification for {launches['count']} Upcoming Space Launch(es)"

    def render_body(self, launches: dict[str, Any]) -> str:
        """render text body"""
        return self.renderer.render(launches)

    def __repr__(self) -> str:
        return "TextRenderer()"


def get_notification_renderer(renderer: str) -> NotificationRenderer:
    """Get a NotificationRender based on the renderer string."""
    logging.debug(
        "loading notification render: %s",
        renderer,
    )
    match renderer:
        case "plaintext":
            return TextRenderer()
        case _:
            # default to TextRender
            logging.warning("Unknown renderer: %s", renderer)
            return TextRenderer()


def localize_time(iso_time: str) -> str:
    """Localize iso_time to
    TEMPLATE_TZ and TEMPLATE_DT_FORMAT"""
    try:
        # convert str time to naive datetime
        dt = datetime.strptime(iso_time, LAUNCH_DT_FORMAT)
    except ValueError:
        return ""
    # set timezone to UTC
    dt = dt.replace(tzinfo=pytz.utc)
    # change timezone
    dt_offset = dt.astimezone(pytz.timezone(BODY_TZ))
    # output datetime in template format
    return dt_offset.strftime(BODY_DT_FORMAT)


def format_time(iso_time: str) -> str:
    """convert an iso formatted time to the
    TEMPLATE_DT_FORMAT"""
    try:
        # convert str time to naive datetime
        dt = datetime.strptime(iso_time, LAUNCH_DT_FORMAT)
    except ValueError:
        return ""
    # set timezone to UTC
    dt = dt.replace(tzinfo=pytz.utc)
    # output datetime in template format
    return dt.strftime(BODY_DT_FORMAT)


# add custom time formatting functions to jinja2 env
JINJA_ENV.globals["localize_time"] = localize_time
JINJA_ENV.globals["format_time"] = format_time
