"""unittests for launches.notifications.templates

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from launches.notifications.renderers import JinjaRenderer, format_time, localize_time

RENDERED_BODY = """Upcoming Space Launches:

Launch 1:
    Name: Falcon 9 Block 5 | Starlink Group 7-7
    Status: Go for Launch

    Launch Window:
        Start:
            Sun Nov 19 00:55:00 2023 CST
            Sun Nov 19 06:55:00 2023 UTC
        End:
            Sun Nov 19 04:52:20 2023 CST
            Sun Nov 19 10:52:20 2023 UTC

    Launch Service Provider:
        Name: SpaceX
        Type: Commercial

    Rocket:
        Name: Falcon 9 Block 5

    Mission:
        Name: Starlink Group 7-7
        Description: A batch of satellites for the Starlink mega-constellation - SpaceX's project for space-based Internet communication system.
        Orbit: Low Earth Orbit
        Agencies:
            Name: SpaceX
            Type: Commercial
            Country: USA
    Launch Pad:
        Name: Space Launch Complex 4E
        Location: Vandenberg SFB, CA, USA

"""


def test_jinja_renderer(valid_launches):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    assert (
        text_renderer.render_subject(valid_launches)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    assert text_renderer.render_text_body(valid_launches) == RENDERED_BODY
    assert text_renderer.render_formatted_body(valid_launches) is None


def test_localize_time():
    """localize_time should return a string in the expected format"""
    assert localize_time("2023-11-19T10:52:20Z") == "Sun Nov 19 04:52:20 2023 CST"


def test_localize_unexpected_time_format():
    """localize_time should return an empty string if the input is not in the expected format"""
    assert localize_time("2023-11-19") == ""
    assert localize_time("2023-11-19T10:52:20") == ""
    assert localize_time("2023-11-19 10:52:20") == ""


def test_format_time():
    """format_time should return a string in the expected format"""
    assert format_time("2023-11-19T10:52:20Z") == "Sun Nov 19 10:52:20 2023 UTC"


def test_format_unexpected_time_format():
    """format_time should return an empty string if the input is not in the expected format"""
    assert format_time("2023-11-19 10:52:20 GMT") == ""
    assert format_time("2023-11-19 10:52:20") == ""
