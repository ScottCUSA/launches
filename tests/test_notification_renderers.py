"""unittests for launches.notifications.templates

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

from launches.notifications.renderers import (
    HTML_TEMPLATE,
    JinjaRenderer,
    format_time,
    local_format_time,
)

TXT_RENDERED_BODY = """Upcoming Space Launches:

Launch 1:
    Name: Firefly Alpha | FLTA005 (Noise of Summer)
    Status: Go for Launch

    Launch Window:
        Start:
            Mon Jul 01 2024 23:03:00 CDT
            Tue Jul 02 2024 04:03:00 UTC
        End:
            Mon Jul 01 2024 23:33:00 CDT
            Tue Jul 02 2024 04:33:00 UTC

    Launch Service Provider:
        Name: Firefly Aerospace
        Type: Commercial

    Rocket:
        Name: Firefly Alpha

    Mission:
        Name: FLTA005 (Noise of Summer)
        Description: Fourth flight of the Firefly Alpha small sat launcher, carrying eight cubesats for NASA's ELaNa 43 (Educational Launch of a Nanosatellite) mission.
        Orbit: Low Earth Orbit
        Agencies:
            Name: National Aeronautics and Space Administration
            Type: Government
            Country: USA
    Launch Pad:
        Name: Space Launch Complex 2W
        Location: Vandenberg SFB, CA, USA

"""  # noqa: E501

HTML_RENDERED_BODY = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upcoming Space Launches</title>
</head>
<body>
    <h1>Upcoming Space Launches</h1>

    <div>
        <h2>Launch 1:</h2>
        <p>
            <strong>Name:</strong> Firefly Alpha | FLTA005 (Noise of Summer)<br>
            <strong>Status:</strong> Go for Launch
        </p>
        <strong>Launch Window</strong><br>
        <ul>
            <li>
                <strong>Start:</strong><br>
                Mon Jul 01 2024 23:03:00 CDT<br>
                Tue Jul 02 2024 04:03:00 UTC
            </li>
            <li>
                <strong>End:</strong><br>
                Mon Jul 01 2024 23:33:00 CDT<br>
                Tue Jul 02 2024 04:33:00 UTC
            </li>
        </ul>
        <p>
            <strong>Launch Service Provider:</strong><br>
            Name: Firefly Aerospace<br>
            Type: Commercial
        </p>
        <p>
            <strong>Rocket:</strong> Firefly Alpha
        </p>
        <p>
            <strong>Mission:</strong><br>
            Name: FLTA005 (Noise of Summer)<br>
            Description: Fourth flight of the Firefly Alpha small sat launcher, carrying eight cubesats for NASA&#39;s ELaNa 43 (Educational Launch of a Nanosatellite) mission.<br>
            Orbit: Low Earth Orbit
        </p>
        <p>
            <strong>Agencies:</strong><br>
            Name: National Aeronautics and Space Administration<br>
            Type: Government<br>
            Country: USA<br>
        </p>
        <p>
            <strong>Launch Pad:</strong><br>
            Name: Space Launch Complex 2W<br>
            Location: Vandenberg SFB, CA, USA
        </p>
        <p>
            <strong>Info Urls:</strong><br>
            <a href="https://fireflyspace.com/missions/noise-of-summer/" target="_blank">Noise of Summer</a><br>
        </p>
        <p>
            <strong>Video Urls:</strong><br>
            <a href="https://www.youtube.com/watch?v=F6nYZEVsMc0" target="_blank">Alpha FLTA005 &#34;Noise of Summer&#34;</a><br>
        </p>
    </div>
</body>
</html>"""  # noqa: E501


def test_jinja_renderer(valid_launches):
    """TextRenderer should render a notification in the expected format"""
    text_renderer = JinjaRenderer()
    assert (
        text_renderer.render_subject(valid_launches)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    assert text_renderer.render_text_body(valid_launches) == TXT_RENDERED_BODY
    assert text_renderer.render_formatted_body(valid_launches) is None


def test_jinja_renderer_html(valid_launches):
    """TextRenderer should render a notification in the expected format"""
    html_renderer = JinjaRenderer(formatted_template=HTML_TEMPLATE)
    assert (
        html_renderer.render_subject(valid_launches)
        == "Notification for 1 Upcoming Space Launch(es)"
    )
    assert html_renderer.render_text_body(valid_launches) == TXT_RENDERED_BODY
    assert html_renderer.render_formatted_body(valid_launches) == HTML_RENDERED_BODY


def test_local_format_time():
    """local_format_time should return a string in the expected format"""
    assert local_format_time("2023-11-19T10:52:20Z") == "Sun Nov 19 2023 04:52:20 CST"


def test_local_unexpected_time_format():
    """local_format_time should return an empty string if the input is not in the expected format"""
    assert local_format_time("2023-11-19") == ""
    assert local_format_time("2023-11-19T10:52:20") == ""
    assert local_format_time("2023-11-19 10:52:20") == ""


def test_format_time():
    """format_time should return a string in the expected format"""
    assert format_time("2023-11-19T10:52:20Z") == "Sun Nov 19 2023 10:52:20 UTC"


def test_format_unexpected_time_format():
    """format_time should return an empty string if the input is not in the expected format"""
    assert format_time("2023-11-19 10:52:20 GMT") == ""
    assert format_time("2023-11-19 10:52:20") == ""
