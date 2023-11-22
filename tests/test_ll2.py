"""unittests for launches.ll2

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""
import pytest

from launches.ll2 import check_response, LL2RequestError

VALID_LAUNCHES_DICT = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "name": "Falcon 9 Block 5 | Starlink Group 7-7",
            "status": {"name": "Go for Launch"},
            "window_end": "2023-11-19T10:52:20Z",
            "window_start": "2023-11-19T06:55:00Z",
            "launch_service_provider": {
                "name": "SpaceX",
                "type": "Commercial",
            },
            "rocket": {
                "configuration": {
                    "full_name": "Falcon 9 Block 5",
                },
            },
            "mission": {
                "name": "Starlink Group 7-7",
                "description": "A batch of satellites for the Starlink mega-constellation - SpaceX's project for space-based Internet communication system.",
                "type": "Communications",
                "orbit": {"name": "Low Earth Orbit"},
                "agencies": [
                    {
                        "name": "SpaceX",
                        "type": "Commercial",
                        "country_code": "USA",
                    }
                ],
            },
            "pad": {
                "name": "Space Launch Complex 4E",
                "location": {
                    "name": "Vandenberg SFB, CA, USA",
                },
            },
        }
    ],
}
INVALID_LAUNCHES_DICT = {"error_message": "something unexpected happened"}


def test_check_error_response():
    with pytest.raises(LL2RequestError):
        check_response(INVALID_LAUNCHES_DICT)


def test_check_valid_response():
    assert check_response(VALID_LAUNCHES_DICT) is None
