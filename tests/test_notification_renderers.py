"""unittests for launches.notifications.templates

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from launches.notifications.renderers import (
    HTML_TEMPLATE,
    JinjaRenderer,
    format_time,
    local_format_time,
)


def test_subject_renderer(single_launch):
    renderer = JinjaRenderer()
    subject = renderer.render_subject(single_launch)
    assert "1" in subject


def test_subject_renderer_two_launches(two_launches):
    renderer = JinjaRenderer()
    subject = renderer.render_subject(two_launches)
    assert "2" in subject


def test_jinja_renderer(single_launch):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    text_body = text_renderer.render_text_body(single_launch)
    subject = text_renderer.render_subject(single_launch)
    formatted_body = text_renderer.render_formatted_body(single_launch)

    assert "1" in subject
    assert formatted_body is None
    # Check key content for first launch
    assert "Falcon 9 Block 5 | Starlink Group 17-1" in text_body
    assert "Tue May 27 2025 11:14 CDT" in text_body
    assert "Tue May 27 2025 16:14 UTC" in text_body


def test_jinja_renderer_html(single_launch):
    """TextRenderer should render a notification in the expected format"""
    html_renderer = JinjaRenderer(formatted_template=HTML_TEMPLATE)
    formatted_body = html_renderer.render_formatted_body(single_launch)

    # Check that output is valid HTML rather than exact match
    assert formatted_body is not None
    assert formatted_body.startswith("<!DOCTYPE html>")
    assert "<html" in formatted_body
    assert "<head>" in formatted_body
    assert "<body>" in formatted_body

    # Check key content is present
    assert "Falcon 9 Block 5 | Starlink Group 17-1" in formatted_body
    assert "Tue May 27 2025 11:14 CDT" in formatted_body
    assert "Tue May 27 2025 16:14 UTC" in formatted_body
    assert "Go for Launch" in formatted_body


def test_jinja_renderer_two_launches(two_launches):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    text_body = text_renderer.render_text_body(two_launches)

    # Check key content for first launch
    assert "Falcon 9 Block 5 | Starlink Group 17-1" in text_body
    assert "Tue May 27 2025 11:14 CDT" in text_body
    assert "Tue May 27 2025 16:14 UTC" in text_body
    assert "Go for Launch" in text_body

    # Check key content for second launch
    assert "Falcon 9 Block 5 | Starlink Group 10-32" in text_body
    assert "Wed May 28 2025 13:30 UTC" in text_body
    assert "To Be Confirmed" in text_body


def test_jinja_renderer_two_launches_html(two_launches):
    """TextRenderer should render a notification in the expected format"""
    html_renderer = JinjaRenderer(formatted_template=HTML_TEMPLATE)
    formatted_body = html_renderer.render_formatted_body(two_launches)

    # Check that output is valid HTML rather than exact match
    assert formatted_body is not None
    assert formatted_body.startswith("<!DOCTYPE html>")
    assert "<html" in formatted_body
    assert "<head>" in formatted_body
    assert "<body>" in formatted_body

    # Check key content for first launch
    assert "Falcon 9 Block 5 | Starlink Group 17-1" in formatted_body
    assert "Tue May 27 2025 11:14 CDT" in formatted_body
    assert "Tue May 27 2025 16:14 UTC" in formatted_body
    assert "Go for Launch" in formatted_body

    # Check key content for second launch
    assert "Falcon 9 Block 5 | Starlink Group 10-32" in formatted_body
    assert "Wed May 28 2025 13:30 UTC" in formatted_body
    assert "To Be Confirmed" in formatted_body


def test_local_format_time():
    """local_format_time should return a string in the expected format"""
    assert local_format_time("2023-11-19T10:52:20Z") == "Sun Nov 19 2023 04:52 CST"


def test_local_unexpected_time_format():
    """local_format_time should return an empty string if the input is not in the expected format"""
    assert local_format_time("2023-11-19") == ""
    assert local_format_time("2023-11-19T10:52") == ""
    assert local_format_time("2023-11-19 10:52") == ""


def test_format_time():
    """format_time should return a string in the expected format"""
    assert format_time("2023-11-19T10:52:20Z") == "Sun Nov 19 2023 10:52 UTC"


def test_format_unexpected_time_format():
    """format_time should return an empty string if the input is not in the expected format"""
    assert format_time("2023-11-19 10:52 GMT") == ""
    assert format_time("2023-11-19 10:52") == ""
