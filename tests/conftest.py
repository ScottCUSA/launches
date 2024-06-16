from unittest.mock import patch

import pytest

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
                "description": "A batch of satellites for the Starlink mega-constellation - "
                "SpaceX's project for space-based Internet communication system.",
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


@pytest.fixture
def valid_launches():
    return VALID_LAUNCHES_DICT


@pytest.fixture
def invalid_launches():
    return INVALID_LAUNCHES_DICT


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as get:
        yield get


@pytest.fixture
def mock_ll2_get():
    with patch("launches.ll2.ll2_get") as get:
        yield get
