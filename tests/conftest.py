from typing import Any
from unittest.mock import patch

import pytest

VALID_LAUNCHES_DICT: dict[str, Any] = {
  "count": 1,
  "next": None,
  "previous": None,
  "results": [
    {
      "id": "67c0e594-72df-4cb4-8db3-3f94e96a7ecc",
      "url": "https://lldev.thespacedevs.com/2.2.0/launch/67c0e594-72df-4cb4-8db3-3f94e96a7ecc/",
      "slug": "firefly-alpha-flta005-noise-of-summer",
      "flightclub_url": "https://flightclub.io/result?llId=67c0e594-72df-4cb4-8db3-3f94e96a7ecc",
      "r_spacex_api_id": None,
      "name": "Firefly Alpha | FLTA005 (Noise of Summer)",
      "status": {
        "id": 1,
        "name": "Go for Launch",
        "abbrev": "Go",
        "description": "Current T-0 confirmed by official or reliable sources."
      },
      "last_updated": "2024-06-30T19:00:35Z",
      "updates": [
        {
          "id": 1441,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/arnaud2520muller_profile_20230607144351.jpg",
          "comment": "Adding launch",
          "info_url": "https://www.cnbc.com/2022/03/22/rocket-builder-firefly-resuming-launch-operations-raises-75-million.html",
          "created_by": "Nosu",
          "created_on": "2022-03-22T17:44:40Z"
        },
        {
          "id": 2101,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET November 2022",
          "info_url": "https://spacenews.com/firefly-gears-up-for-second-alpha-launch/",
          "created_by": "Cosmic_Penguin",
          "created_on": "2022-07-18T09:18:15Z"
        },
        {
          "id": 2858,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET January 2023",
          "info_url": "https://apps.fcc.gov/oetcf/els/reports/STA_Print.cfm?mode=current&application_seq=119834&RequestTimeout=1000",
          "created_by": "Cosmic_Penguin",
          "created_on": "2022-11-20T03:28:55Z"
        },
        {
          "id": 3172,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET February 2023",
          "info_url": "https://apps.fcc.gov/oetcf/els/reports/STA_Print.cfm?mode=current&application_seq=119834&RequestTimeout=1000",
          "created_by": "Cosmic_Penguin",
          "created_on": "2023-01-15T13:19:59Z"
        },
        {
          "id": 3991,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET July 2023.",
          "info_url": "https://www.cnbc.com/2023/05/06/firefly-launching-space-force-high-speed-victus-nox-mission.html",
          "created_by": "Cosmic_Penguin",
          "created_on": "2023-05-06T15:14:36Z"
        },
        {
          "id": 4247,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET August 2023.",
          "info_url": "https://apps.fcc.gov/oetcf/els/reports/STA_Print.cfm?mode=current&application_seq=124895&RequestTimeout=1000",
          "created_by": "Cosmic_Penguin",
          "created_on": "2023-05-31T17:34:35Z"
        },
        {
          "id": 5403,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET March 2024.",
          "info_url": "https://forum.nasaspaceflight.com/index.php?topic=58177.msg2531109#msg2531109",
          "created_by": "Cosmic_Penguin",
          "created_on": "2023-10-13T02:34:13Z"
        },
        {
          "id": 7548,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET June.",
          "info_url": "https://astro.arizona.edu/news/congratulations-catsat-team-successful-satellite-integration-vandenberg-space-force-base-next",
          "created_by": "Cosmic_Penguin",
          "created_on": "2024-05-16T23:44:32Z"
        },
        {
          "id": 7905,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "Targeting June 27 UTC.",
          "info_url": "https://www.nasa.gov/missions/small-satellite-missions/nasas-elana-43-prepares-for-firefly-aerospace-launch/",
          "created_by": "Cosmic_Penguin",
          "created_on": "2024-06-21T19:14:43Z"
        },
        {
          "id": 7933,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "Tweaked T-0.",
          "info_url": "https://fireflyspace.com/missions/noise-of-summer/",
          "created_by": "Cosmic_Penguin",
          "created_on": "2024-06-24T19:25:35Z"
        },
        {
          "id": 7945,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "Delayed to July 2 UTC.",
          "info_url": "https://forum.nasaspaceflight.com/index.php?topic=58177.msg2603811#msg2603811",
          "created_by": "Cosmic_Penguin",
          "created_on": "2024-06-26T02:04:31Z"
        },
        {
          "id": 7958,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/cosmic2520penguin_profile_20210817212020.png",
          "comment": "NET June 30 local time.",
          "info_url": "https://fireflyspace.com/missions/noise-of-summer/",
          "created_by": "Cosmic_Penguin",
          "created_on": "2024-06-27T01:47:28Z"
        },
        {
          "id": 7979,
          "profile_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/profile_images/arnaud2520muller_profile_20230607144351.jpg",
          "comment": "Delayed by a day",
          "info_url": "https://fireflyspace.com/missions/noise-of-summer/",
          "created_by": "Nosu",
          "created_on": "2024-06-29T21:02:09Z"
        }
      ],
      "net": "2024-07-02T04:03:00Z",
      "net_precision": {
        "id": 1,
        "name": "Minute",
        "abbrev": "MIN",
        "description": "The T-0 is accurate to the minute."
      },
      "window_end": "2024-07-02T04:33:00Z",
      "window_start": "2024-07-02T04:03:00Z",
      "probability": None,
      "weather_concerns": None,
      "holdreason": "",
      "failreason": "",
      "hashtag": None,
      "launch_service_provider": {
        "id": 265,
        "url": "https://lldev.thespacedevs.com/2.2.0/agencies/265/",
        "name": "Firefly Aerospace",
        "featured": True,
        "type": "Commercial",
        "country_code": "USA",
        "abbrev": "FA",
        "description": "Firefly Aerospace is an American private aerospace firm based in Austin, Texas, that develops small and medium-sized launch vehicles for commercial launches to orbit.",
        "administrator": "Bill Weber",
        "founding_year": "2014",
        "launchers": "",
        "spacecraft": "",
        "launch_library_url": None,
        "total_launch_count": 4,
        "consecutive_successful_launches": 0,
        "successful_launches": 2,
        "failed_launches": 2,
        "pending_launches": 2,
        "consecutive_successful_landings": 0,
        "successful_landings": 0,
        "failed_landings": 0,
        "attempted_landings": 0,
        "info_url": "https://firefly.com/",
        "wiki_url": "https://en.wikipedia.org/wiki/Firefly_Aerospace",
        "logo_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly2520aerospace_logo_20220826094423.jpg",
        "image_url": None,
        "nation_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly2520aerospace_nation_20230531050520.jpg"
      },
      "rocket": {
        "id": 7542,
        "configuration": {
          "id": 179,
          "url": "https://lldev.thespacedevs.com/2.2.0/config/launcher/179/",
          "name": "Firefly Alpha",
          "active": True,
          "reusable": False,
          "description": "Firefly Alpha (Firefly α) is a two-stage orbital expendable launch vehicle developed by the American aerospace company Firefly Aerospace to cover the commercial small satellite launch market. Alpha is intended to provide launch options for both full vehicle and ride share customers.",
          "family": "",
          "full_name": "Firefly Alpha",
          "manufacturer": {
            "id": 265,
            "url": "https://lldev.thespacedevs.com/2.2.0/agencies/265/",
            "name": "Firefly Aerospace",
            "featured": True,
            "type": "Commercial",
            "country_code": "USA",
            "abbrev": "FA",
            "description": "Firefly Aerospace is an American private aerospace firm based in Austin, Texas, that develops small and medium-sized launch vehicles for commercial launches to orbit.",
            "administrator": "Bill Weber",
            "founding_year": "2014",
            "launchers": "",
            "spacecraft": "",
            "launch_library_url": None,
            "total_launch_count": 4,
            "consecutive_successful_launches": 0,
            "successful_launches": 2,
            "failed_launches": 2,
            "pending_launches": 2,
            "consecutive_successful_landings": 0,
            "successful_landings": 0,
            "failed_landings": 0,
            "attempted_landings": 0,
            "info_url": "https://firefly.com/",
            "wiki_url": "https://en.wikipedia.org/wiki/Firefly_Aerospace",
            "logo_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly2520aerospace_logo_20220826094423.jpg",
            "image_url": None,
            "nation_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly2520aerospace_nation_20230531050520.jpg"
          },
          "program": [],
          "variant": "",
          "alias": "",
          "min_stage": 2,
          "max_stage": 2,
          "length": 29.0,
          "diameter": 1.82,
          "maiden_flight": "2021-09-03",
          "launch_cost": "15000000",
          "launch_mass": 54,
          "leo_capacity": 1000,
          "gto_capacity": None,
          "to_thrust": 736,
          "apogee": None,
          "vehicle_range": None,
          "image_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly_alpha_l_image_20240605174156.jpeg",
          "info_url": "https://fireflyspace.com/alpha/",
          "wiki_url": "https://en.wikipedia.org/wiki/Firefly_Alpha",
          "total_launch_count": 4,
          "consecutive_successful_launches": 0,
          "successful_launches": 2,
          "failed_launches": 2,
          "pending_launches": 2,
          "attempted_landings": 0,
          "successful_landings": 0,
          "failed_landings": 0,
          "consecutive_successful_landings": 0
        },
        "launcher_stage": [],
        "spacecraft_stage": None
      },
      "mission": {
        "id": 5969,
        "name": "FLTA005 (Noise of Summer)",
        "description": "Fourth flight of the Firefly Alpha small sat launcher, carrying eight cubesats for NASA's ELaNa 43 (Educational Launch of a Nanosatellite) mission.",
        "launch_designator": None,
        "type": "Technology",
        "orbit": {
          "id": 8,
          "name": "Low Earth Orbit",
          "abbrev": "LEO"
        },
        "agencies": [
          {
            "id": 44,
            "url": "https://lldev.thespacedevs.com/2.2.0/agencies/44/",
            "name": "National Aeronautics and Space Administration",
            "featured": True,
            "type": "Government",
            "country_code": "USA",
            "abbrev": "NASA",
            "description": "The National Aeronautics and Space Administration is an independent agency of the executive branch of the United States federal government responsible for the civilian space program, as well as aeronautics and aerospace research. NASA have many launch facilities but most are inactive. The most commonly used pad will be LC-39B at Kennedy Space Center in Florida.",
            "administrator": "Administrator: Bill Nelson",
            "founding_year": "1958",
            "launchers": "Space Shuttle | SLS",
            "spacecraft": "Orion",
            "launch_library_url": None,
            "total_launch_count": 135,
            "consecutive_successful_launches": 11,
            "successful_launches": 115,
            "failed_launches": 20,
            "pending_launches": 6,
            "consecutive_successful_landings": 0,
            "successful_landings": 0,
            "failed_landings": 0,
            "attempted_landings": 0,
            "info_url": "http://www.nasa.gov",
            "wiki_url": "http://en.wikipedia.org/wiki/National_Aeronautics_and_Space_Administration",
            "logo_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/national2520aeronautics2520and2520space2520administration_logo_20190207032448.png",
            "image_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/national2520aeronautics2520and2520space2520administration_image_20190207032448.jpeg",
            "nation_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/national2520aeronautics2520and2520space2520administration_nation_20230803040809.jpg"
          }
        ],
        "info_urls": [],
        "vid_urls": []
      },
      "pad": {
        "id": 39,
        "url": "https://lldev.thespacedevs.com/2.2.0/pad/39/",
        "agency_id": None,
        "name": "Space Launch Complex 2W",
        "description": "SLC-2W was originally used for Delta, Thor-Agena and Delta II launches. After the last Delta II flight in 2018, SLC-2W was repurposed to launch Firefly Alpha rockets.",
        "info_url": None,
        "wiki_url": "https://en.wikipedia.org/wiki/Vandenberg_Space_Launch_Complex_2",
        "map_url": "https://www.google.com/maps?q=34.7556,-120.6224",
        "latitude": "34.7556",
        "longitude": "-120.6224",
        "location": {
          "id": 11,
          "url": "https://lldev.thespacedevs.com/2.2.0/location/11/",
          "name": "Vandenberg SFB, CA, USA",
          "country_code": "USA",
          "description": "",
          "map_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/location_11_20200803142416.jpg",
          "timezone_name": "America/Los_Angeles",
          "total_launch_count": 761,
          "total_landing_count": 19
        },
        "country_code": "USA",
        "map_image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/pad_39_20200803143542.jpg",
        "total_launch_count": 96,
        "orbital_launch_attempt_count": 96
      },
      "infoURLs": [
        {
          "priority": 10,
          "source": "fireflyspace.com",
          "title": "Noise of Summer",
          "description": "Alpha FLTA005 will launch eight CubeSats in support of Firefly’s Venture-Class Launch Services Demo 2 contract with NASA.",
          "feature_image": None,
          "url": "https://fireflyspace.com/missions/noise-of-summer/",
          "type": {
            "id": 1,
            "name": "Official Page"
          },
          "language": {
            "id": 1,
            "name": "English",
            "code": "en"
          }
        }
      ],
      "vidURLs": [
        {
          "priority": 10,
          "source": "youtube.com",
          "publisher": "Firefly Aerospace",
          "title": "Alpha FLTA005 \"Noise of Summer\"",
          "description": "Alpha FLTA005, a mission called Noise of Summer, supports Firefly’s Venture-Class Launch Services Demo 2 contract with NASA that serves to validate the capab...",
          "feature_image": "https://i.ytimg.com/vi/F6nYZEVsMc0/maxresdefault_live.jpg",
          "url": "https://www.youtube.com/watch?v=F6nYZEVsMc0",
          "type": {
            "id": 1,
            "name": "Official Webcast"
          },
          "language": {
            "id": 1,
            "name": "English",
            "code": "en"
          },
          "start_time": "2024-07-02T03:33:00Z",
          "end_time": None
        }
      ],
      "webcast_live": False,
      "timeline": [
        {
          "type": {
            "id": 118,
            "abbrev": "Payload Processing End",
            "description": "End of payload processing operations"
          },
          "relative_time": "-PT18H"
        },
        {
          "type": {
            "id": 119,
            "abbrev": "Payload Segment Preparation",
            "description": "Preparation of the payload segment ahead of its mating with the rocket"
          },
          "relative_time": "-PT17H30M"
        },
        {
          "type": {
            "id": 120,
            "abbrev": "Payload Segment Transport",
            "description": "Transport of the payload segment to the rocket"
          },
          "relative_time": "-PT17H"
        },
        {
          "type": {
            "id": 121,
            "abbrev": "Payload Segment Mating",
            "description": "Mating of the payload segment to the rocket"
          },
          "relative_time": "-PT15H"
        },
        {
          "type": {
            "id": 122,
            "abbrev": "Pad Configuration",
            "description": "Configuration of the pad for flight"
          },
          "relative_time": "-PT9H"
        },
        {
          "type": {
            "id": 123,
            "abbrev": "Launcher Vertical",
            "description": "Erection of the launch vehicle into a vertical position"
          },
          "relative_time": "-PT7H30M"
        },
        {
          "type": {
            "id": 124,
            "abbrev": "Propulsion Checkouts",
            "description": "Final checkouts of the propulsion system ahead of launch"
          },
          "relative_time": "-PT5H"
        },
        {
          "type": {
            "id": 2,
            "abbrev": "Prop Load",
            "description": "Start of propelland loading"
          },
          "relative_time": "-PT4H"
        },
        {
          "type": {
            "id": 125,
            "abbrev": "LOX Topping",
            "description": "Liquid oxygen topping off"
          },
          "relative_time": "-PT1H5M"
        },
        {
          "type": {
            "id": 126,
            "abbrev": "Ready Poll",
            "description": "Polling ready ahead of terminal count"
          },
          "relative_time": "-PT20M"
        },
        {
          "type": {
            "id": 127,
            "abbrev": "Terminal Count",
            "description": "Start of the terminal countdown towards launch"
          },
          "relative_time": "-PT15M"
        },
        {
          "type": {
            "id": 128,
            "abbrev": "Strongback Retract",
            "description": "Retraction of the strongback arm ahead of liftoff"
          },
          "relative_time": "-PT5M"
        },
        {
          "type": {
            "id": 8,
            "abbrev": "GO for Launch",
            "description": "Launch director verifies go for launch"
          },
          "relative_time": "-PT2M"
        },
        {
          "type": {
            "id": 9,
            "abbrev": "Ignition",
            "description": "Start of the engine ignition sequence"
          },
          "relative_time": "-PT2S"
        },
        {
          "type": {
            "id": 10,
            "abbrev": "Liftoff",
            "description": "First upwards movement of the rocket"
          },
          "relative_time": "P0D"
        },
        {
          "type": {
            "id": 25,
            "abbrev": "Supersonic",
            "description": "Vehicle is supersonic"
          },
          "relative_time": "PT54S"
        },
        {
          "type": {
            "id": 11,
            "abbrev": "Max-Q",
            "description": "Maximum dynamic pressure"
          },
          "relative_time": "PT1M5S"
        },
        {
          "type": {
            "id": 12,
            "abbrev": "MECO",
            "description": "Cut-off of the main engine"
          },
          "relative_time": "PT2M30S"
        },
        {
          "type": {
            "id": 13,
            "abbrev": "Stage 2 Separation",
            "description": "Separation of the second stage from the first"
          },
          "relative_time": "PT2M33S"
        },
        {
          "type": {
            "id": 31,
            "abbrev": "SES",
            "description": "Start of the second engine"
          },
          "relative_time": "PT2M35S"
        },
        {
          "type": {
            "id": 15,
            "abbrev": "Fairing Separation",
            "description": "Separation of the payload fairing"
          },
          "relative_time": "PT2M45S"
        },
        {
          "type": {
            "id": 24,
            "abbrev": "SECO",
            "description": "Cut-off of the second engine"
          },
          "relative_time": "PT8M10S"
        },
        {
          "type": {
            "id": 78,
            "abbrev": "Payload Deployment Sequence Start",
            "description": "Start of the payload deployment sequence"
          },
          "relative_time": "PT44M33S"
        },
        {
          "type": {
            "id": 79,
            "abbrev": "Payload Deployment Sequence End",
            "description": "End of the payload deployment sequence."
          },
          "relative_time": "PT55M13S"
        }
      ],
      "image": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/images/firefly_alpha_l_image_20240605174156.jpeg",
      "infographic": None,
      "program": [],
      "orbital_launch_attempt_count": 6706,
      "location_launch_attempt_count": 762,
      "pad_launch_attempt_count": 97,
      "agency_launch_attempt_count": 5,
      "orbital_launch_attempt_count_year": 127,
      "location_launch_attempt_count_year": 23,
      "pad_launch_attempt_count_year": 1,
      "agency_launch_attempt_count_year": 1,
      "pad_turnaround": "P192DT10H30M30S",
      "mission_patches": [
        {
          "id": 1024,
          "name": "Noise of Summer",
          "priority": 10,
          "image_url": "https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/mission_patch_images/noise2520of25_mission_patch_20240612193711.png", 
          "agency": {
            "id": 265,
            "url": "https://lldev.thespacedevs.com/2.2.0/agencies/265/",
            "name": "Firefly Aerospace",
            "type": "Commercial"
          }
        }
      ],
      "type": "detailed"
    }
  ]
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
