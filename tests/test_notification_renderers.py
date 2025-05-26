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

SINGLE_LAUNCH_TXT_BODY = """Summary:
    Launch 1:
      - SpaceX Falcon 9 Block 5 | Starlink Group 17-1 | Go for Launch
      - Tue May 27 2025 11:14 CDT | Tue May 27 2025 16:14 UTC

Upcoming Space Launches:

    Launch 1:
        Name: Falcon 9 Block 5 | Starlink Group 17-1
        Status: Go for Launch

        Launch Window:
            Start:
                Tue May 27 2025 11:14 CDT
                Tue May 27 2025 16:14 UTC
            End:
                Tue May 27 2025 15:14 CDT
                Tue May 27 2025 20:14 UTC

        Launch Service Provider:
            Name: SpaceX
            Type: Commercial

        Rocket:
            Name: Falcon 9 Block 5

        Mission:
            Name: Starlink Group 17-1
            Description: A batch of 24 satellites for the Starlink mega-constellation - SpaceX's project for space-based Internet communication system.
            Orbit: Low Earth Orbit
            Agencies:
                Name: SpaceX
                Type: Commercial
                Country: USA
        Launch Pad:
            Name: Space Launch Complex 4E
            Location: Vandenberg SFB, CA, USA
"""

TWO_LAUNCHES_TXT_BODY = """Summary:
    Launch 1:
      - SpaceX Falcon 9 Block 5 | Starlink Group 17-1 | Go for Launch
      - Tue May 27 2025 11:14 CDT | Tue May 27 2025 16:14 UTC

    Launch 2:
      - SpaceX Starship | Flight 9 | Go for Launch
      - Tue May 27 2025 18:30 CDT | Tue May 27 2025 23:30 UTC

Upcoming Space Launches:

    Launch 1:
        Name: Falcon 9 Block 5 | Starlink Group 17-1
        Status: Go for Launch

        Launch Window:
            Start:
                Tue May 27 2025 11:14 CDT
                Tue May 27 2025 16:14 UTC
            End:
                Tue May 27 2025 15:14 CDT
                Tue May 27 2025 20:14 UTC

        Launch Service Provider:
            Name: SpaceX
            Type: Commercial

        Rocket:
            Name: Falcon 9 Block 5

        Mission:
            Name: Starlink Group 17-1
            Description: A batch of 24 satellites for the Starlink mega-constellation - SpaceX's project for space-based Internet communication system.
            Orbit: Low Earth Orbit
            Agencies:
                Name: SpaceX
                Type: Commercial
                Country: USA
        Launch Pad:
            Name: Space Launch Complex 4E
            Location: Vandenberg SFB, CA, USA

    Launch 2:
        Name: Starship | Flight 9
        Status: Go for Launch

        Launch Window:
            Start:
                Tue May 27 2025 18:30 CDT
                Tue May 27 2025 23:30 UTC
            End:
                Tue May 27 2025 20:34 CDT
                Wed May 28 2025 01:34 UTC

        Launch Service Provider:
            Name: SpaceX
            Type: Commercial

        Rocket:
            Name: Starship

        Mission:
            Name: Flight 9
            Description: 9th test flight of the two-stage Starship launch vehicle.
            Orbit: Suborbital
            Agencies:
        Launch Pad:
            Name: Orbital Launch Mount A
            Location: SpaceX Starbase, TX, USA
"""

SINGLE_LAUNCH_HTML_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upcoming Space Launches</title>
</head>
<body>
    <h3>Summary</h3>
    <div>
        <ul>
            <li>
                <strong>Launch 1:</strong><br>
                SpaceX Falcon 9 Block 5 | Starlink Group 17-1 | Go for Launch<br>
                Tue May 27 2025 11:14 CDT | Tue May 27 2025 16:14 UTC
            </li>
        </ul>
    </div>
    <h3>Upcoming Space Launches</h3>
    <div style="padding-left: 20px;">
        <h4>Launch 1:</h4>
        <div style="padding-left: 30px;">
            <p>
                <strong>Name:</strong> Falcon 9 Block 5 | Starlink Group 17-1<br>
                <strong>Status:</strong> Go for Launch
            </p>
            <strong>Launch Window</strong><br>
            <ul>
                <li>
                    <strong>Start:</strong><br>
                    Tue May 27 2025 11:14 CDT<br>
                    Tue May 27 2025 16:14 UTC
                </li>
                <li>
                    <strong>End:</strong><br>
                    Tue May 27 2025 15:14 CDT<br>
                    Tue May 27 2025 20:14 UTC
                </li>
            </ul>
            <p>
                <strong>Launch Service Provider:</strong><br>
                Name: SpaceX<br>
                Type: Commercial
            </p>
            <p>
                <strong>Rocket:</strong> Falcon 9 Block 5
            </p>
            <p>
                <strong>Mission:</strong><br>
                Name: Starlink Group 17-1<br>
                Description: A batch of 24 satellites for the Starlink mega-constellation - SpaceX&#39;s project for space-based Internet communication system.<br>
                Orbit: Low Earth Orbit
            </p><p>
                <strong>Agencies:</strong><br>
                Name: SpaceX<br>
                Type: Commercial<br>
                Country: USA<br>
            </p>
            <p>
                <strong>Launch Pad:</strong><br>
                Name: Space Launch Complex 4E<br>
                Location: Vandenberg SFB, CA, USA
            </p><p>
                <strong>Info Urls:</strong><br>
                <a href="https://www.spacex.com/launches/mission/?missionId=sl-17-1" target="_blank">SpaceX</a><br>
            </p>
            <p>
                <strong>Video Urls:</strong><br>
                <a href="https://www.youtube.com/watch?v=NsJfeLlENLU" target="_blank">GO! - SpaceX - Falcon 9 - Starlink  17-1 - SLC-4E - Vandenberg SFB - Space Affairs Live</a><br>
            <a href="https://x.com/i/broadcasts/1BdxYqMBNoExX" target="_blank">Starlink Mission</a><br>
            </p>
        </div>
    </div>
</body>
</html>"""

TWO_LAUNCHES_HTML_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upcoming Space Launches</title>
</head>
<body>
    <h3>Summary</h3>
    <div>
        <ul>
            <li>
                <strong>Launch 1:</strong><br>
                SpaceX Falcon 9 Block 5 | Starlink Group 17-1 | Go for Launch<br>
                Tue May 27 2025 11:14 CDT | Tue May 27 2025 16:14 UTC
            </li>
        <li>
                <strong>Launch 2:</strong><br>
                SpaceX Starship | Flight 9 | Go for Launch<br>
                Tue May 27 2025 18:30 CDT | Tue May 27 2025 23:30 UTC
            </li>
        </ul>
    </div>
    <h3>Upcoming Space Launches</h3>
    <div style="padding-left: 20px;">
        <h4>Launch 1:</h4>
        <div style="padding-left: 30px;">
            <p>
                <strong>Name:</strong> Falcon 9 Block 5 | Starlink Group 17-1<br>
                <strong>Status:</strong> Go for Launch
            </p>
            <strong>Launch Window</strong><br>
            <ul>
                <li>
                    <strong>Start:</strong><br>
                    Tue May 27 2025 11:14 CDT<br>
                    Tue May 27 2025 16:14 UTC
                </li>
                <li>
                    <strong>End:</strong><br>
                    Tue May 27 2025 15:14 CDT<br>
                    Tue May 27 2025 20:14 UTC
                </li>
            </ul>
            <p>
                <strong>Launch Service Provider:</strong><br>
                Name: SpaceX<br>
                Type: Commercial
            </p>
            <p>
                <strong>Rocket:</strong> Falcon 9 Block 5
            </p>
            <p>
                <strong>Mission:</strong><br>
                Name: Starlink Group 17-1<br>
                Description: A batch of 24 satellites for the Starlink mega-constellation - SpaceX&#39;s project for space-based Internet communication system.<br>
                Orbit: Low Earth Orbit
            </p><p>
                <strong>Agencies:</strong><br>
                Name: SpaceX<br>
                Type: Commercial<br>
                Country: USA<br>
            </p>
            <p>
                <strong>Launch Pad:</strong><br>
                Name: Space Launch Complex 4E<br>
                Location: Vandenberg SFB, CA, USA
            </p><p>
                <strong>Info Urls:</strong><br>
                <a href="https://www.spacex.com/launches/mission/?missionId=sl-17-1" target="_blank">SpaceX</a><br>
            </p>
            <p>
                <strong>Video Urls:</strong><br>
                <a href="https://www.youtube.com/watch?v=NsJfeLlENLU" target="_blank">GO! - SpaceX - Falcon 9 - Starlink  17-1 - SLC-4E - Vandenberg SFB - Space Affairs Live</a><br>
            <a href="https://x.com/i/broadcasts/1BdxYqMBNoExX" target="_blank">Starlink Mission</a><br>
            </p>
        </div>
    </div>
<div style="padding-left: 20px;">
        <h4>Launch 2:</h4>
        <div style="padding-left: 30px;">
            <p>
                <strong>Name:</strong> Starship | Flight 9<br>
                <strong>Status:</strong> Go for Launch
            </p>
            <strong>Launch Window</strong><br>
            <ul>
                <li>
                    <strong>Start:</strong><br>
                    Tue May 27 2025 18:30 CDT<br>
                    Tue May 27 2025 23:30 UTC
                </li>
                <li>
                    <strong>End:</strong><br>
                    Tue May 27 2025 20:34 CDT<br>
                    Wed May 28 2025 01:34 UTC
                </li>
            </ul>
            <p>
                <strong>Launch Service Provider:</strong><br>
                Name: SpaceX<br>
                Type: Commercial
            </p>
            <p>
                <strong>Rocket:</strong> Starship
            </p>
            <p>
                <strong>Mission:</strong><br>
                Name: Flight 9<br>
                Description: 9th test flight of the two-stage Starship launch vehicle.<br>
                Orbit: Suborbital
            </p><p>
                <strong>Launch Pad:</strong><br>
                Name: Orbital Launch Mount A<br>
                Location: SpaceX Starbase, TX, USA
            </p><p>
                <strong>Info Urls:</strong><br>
                <a href="https://www.spacex.com/launches/mission/?missionId=starship-flight-9" target="_blank">SpaceX</a><br>
            </p>
            <p>
                <strong>Video Urls:</strong><br>
                <a href="https://www.youtube.com/watch?v=YOJKZYSOsGs" target="_blank">GO! - SpaceX - Starship - Suborbital Test Flight 9  - OLP-A - Starbase Texas - Space Affairs Live</a><br>
            <a href="https://www.youtube.com/watch?v=hAdLlG9Rfd4" target="_blank">SpaceX Starship Flight 9</a><br>
            <a href="https://x.com/i/broadcasts/1OwxWXMRAXmKQ" target="_blank">Starship&#39;s Ninth Flight Test</a><br>
            </p>
        </div>
    </div>
</body>
</html>"""


def test_jinja_renderer(single_launch):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    assert (
        text_renderer.render_subject(single_launch)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    text_body = text_renderer.render_text_body(single_launch)
    formatted_body = text_renderer.render_formatted_body(single_launch)
    assert text_body == SINGLE_LAUNCH_TXT_BODY
    assert formatted_body is None


def test_jinja_renderer_html(single_launch):
    """TextRenderer should render a notification in the expected format"""
    html_renderer = JinjaRenderer(formatted_template=HTML_TEMPLATE)
    assert (
        html_renderer.render_subject(single_launch)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    text_body = html_renderer.render_text_body(single_launch)
    formatted_body = html_renderer.render_formatted_body(single_launch)
    assert text_body == SINGLE_LAUNCH_TXT_BODY
    assert formatted_body == SINGLE_LAUNCH_HTML_BODY


def test_jinja_renderer_two_launches(two_launches):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    assert (
        text_renderer.render_subject(two_launches) == "Notification for 2 Upcoming Space Launch(es)"
    )

    text_body = text_renderer.render_text_body(two_launches)
    formatted_body = text_renderer.render_formatted_body(two_launches)
    assert text_body == TWO_LAUNCHES_TXT_BODY
    assert formatted_body is None


def test_jinja_renderer_two_launches_html(two_launches):
    """TextRenderer should render a notification in the expected format"""
    html_renderer = JinjaRenderer(formatted_template=HTML_TEMPLATE)
    assert (
        html_renderer.render_subject(two_launches) == "Notification for 2 Upcoming Space Launch(es)"
    )
    text_body = html_renderer.render_text_body(two_launches)
    formatted_body = html_renderer.render_formatted_body(two_launches)
    assert text_body == TWO_LAUNCHES_TXT_BODY
    assert formatted_body == TWO_LAUNCHES_HTML_BODY


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
