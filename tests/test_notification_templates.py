"""unittests for launches.notifications.templates

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from test_ll2 import VALID_LAUNCHES_DICT
from launches.notifications.templates import format_time, localize_time, TextRenderer


RENDERED_BODY = """Upcoming Space Launches:

Launch 1:
    Name: Falcon 9 Block 5 | Starlink Group 7-7
    Status: Go for Launch

    Launch Window:
        Start:
            2023-11-19 00:55:00 CST
            2023-11-19 06:55:00 UTC
        End:
            2023-11-19 04:52:20 CST
            2023-11-19 10:52:20 UTC

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


def test_text_renderer():
    """TextRenderer should render a notification in the expected format"""
    text_renderer = TextRenderer()
    assert (
        text_renderer.render_subject(VALID_LAUNCHES_DICT)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    assert text_renderer.render_body(VALID_LAUNCHES_DICT) == RENDERED_BODY


def test_localize_time():
    """localize_time should return a string in the expected format"""
    assert localize_time("2023-11-19T10:52:20Z") == "2023-11-19 04:52:20 CST"


def test_localize_unexpected_time_format():
    """localize_time should return an empty string if the input is not in the expected format"""
    assert localize_time("2023-11-19") == ""
    assert localize_time("2023-11-19T10:52:20") == ""
    assert localize_time("2023-11-19 10:52:20") == ""


def test_format_time():
    """format_time should return a string in the expected format"""
    assert format_time("2023-11-19T10:52:20Z") == "2023-11-19 10:52:20 UTC"


def test_format_unexpected_time_format():
    """format_time should return an empty string if the input is not in the expected format"""
    assert format_time("2023-11-19 10:52:20 GMT") == ""
    assert format_time("2023-11-19 10:52:20") == ""
