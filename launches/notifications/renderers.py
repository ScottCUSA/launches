"""Space Launch Notifications - Notification Templates Module

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from datetime import datetime, timezone
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from jinja2 import Environment, PackageLoader, Template, select_autoescape
from loguru import logger

from launches.ll2 import LAUNCH_DT_FORMAT

JINJA_ENV = Environment(
    loader=PackageLoader("launches", "templates"), autoescape=select_autoescape()
)
TXT_TEMPLATE = "launches.j2.txt"
HTML_TEMPLATE = "launches.j2.html"
BODY_TZ = "US/Central"
BODY_DT_FORMAT = "%a %b %d %Y %X %Z"


class NotificationRenderer(Protocol):
    """Launch Notification Renderer Protocol"""

    def render_subject(self, launches: dict[str, Any]) -> str:
        """render subject"""
        raise NotImplementedError()

    def render_text_body(self, launches: dict[str, Any]) -> str:
        """render plaintext body"""
        raise NotImplementedError()

    def render_formatted_body(self, launches: dict[str, Any]) -> str | None:
        """render formatted body"""
        raise NotImplementedError()


class JinjaRenderer:
    """Render a Launch Notification Using Text"""

    def __init__(self, text_template=TXT_TEMPLATE, formatted_template: str | None = None):
        self.text_renderer = JINJA_ENV.get_template(text_template)
        if formatted_template is not None:
            self.formatted_renderer: Template | None = JINJA_ENV.get_template(formatted_template)
        else:
            self.formatted_renderer = None
        logger.info(
            "Initialized JinjaRender with text_template: {}, formatted_template: {}",
            text_template,
            formatted_template,
        )

    def render_subject(self, launches: dict[str, Any]) -> str:
        """render text subject"""
        return f"Notification for {launches['count']} Upcoming Space Launch(es)"

    def render_text_body(self, launches: dict[str, Any]) -> str:
        """render text body"""
        return self.text_renderer.render(launches)

    def render_formatted_body(self, launches: dict[str, Any]) -> str | None:
        """render formatted body"""
        if self.formatted_renderer is not None:
            return self.formatted_renderer.render(launches)
        return None

    def __repr__(self) -> str:
        return "JinjaRenderer()"


def get_notification_renderer(renderer: str) -> NotificationRenderer:
    """Get a NotificationRender based on the renderer string."""
    logger.debug(
        "loading notification render: {}",
        renderer,
    )
    match renderer:
        case "plaintext":
            return JinjaRenderer()
        case "html":
            return JinjaRenderer(formatted_template=HTML_TEMPLATE)
        case _:
            # default to TextRender
            logger.warning("Unknown renderer: '{}', defaulting to `plaintext`", renderer)
            return JinjaRenderer(formatted_template=TXT_TEMPLATE)


def local_format_time(iso_time: str) -> str:
    """Localize iso_time to
    TEMPLATE_TZ and BODY_DT_FORMAT"""
    try:
        # convert str time to naive datetime
        dt = datetime.strptime(iso_time, LAUNCH_DT_FORMAT)
    except ValueError:
        return ""
    # set timezone to UTC
    dt = dt.replace(tzinfo=timezone.utc)
    # change timezone
    dt_offset = dt.astimezone(ZoneInfo(BODY_TZ))
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
    dt = dt.replace(tzinfo=timezone.utc)
    # output datetime in template format
    return dt.strftime(BODY_DT_FORMAT)


# add custom time formatting functions to jinja2 env
JINJA_ENV.globals["local_format_time"] = local_format_time
JINJA_ENV.globals["format_time"] = format_time
