"""Space Launch Notifications - Launch Library 2 Requests Module

Copyright ©️ 2023 Scott Cummings
License: GNU General Public License V3
         https://www.gnu.org/licenses/gpl-3.0.en.html
"""
import json
import logging
from datetime import datetime
from typing import Any

import requests

LL2_API_URL = "https://ll.thespacedevs.com/2.2.0/"
LL2_UPCOMING_ENDPOINT = "launch/upcoming/"
REQUEST_TIMEOUT = 30
LAUNCH_DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class LL2RequestError(Exception):
    """launch library request error"""


def ll2_get(endpoint: str, parameters: dict) -> requests.Response:
    """make a get request to the launch library at the
    provided endpoint using the provided parameters"""
    logging.info(
        "Making request to space launch library endpoint %s with parameters: %s",
        endpoint,
        parameters,
    )
    # call launch API for tomorrow's launches
    try:
        resp = requests.get(
            LL2_API_URL + endpoint,
            params=parameters,
            timeout=REQUEST_TIMEOUT,
        )
        logging.info("Space launch library response status code: %s", resp.status_code)
        # raise an exception if the status code >=400
        resp.raise_for_status()
    except requests.exceptions.RequestException as ex:
        raise LL2RequestError(f"Error getting space launches {ex}") from ex

    return resp


def get_upcoming_launches_within_window(
    window_start_lt: datetime,
) -> dict[str, Any] | None:
    """Make a request to the space launch libary for upcoming launches where the
    window is less than the provided datetime raises a RequestError
    if there are issues with the request or response"""
    parameters = {
        "window_start__lt": window_start_lt.strftime(LAUNCH_DT_FORMAT),
        "hide_recent_previous": True,
    }

    resp = ll2_get(LL2_UPCOMING_ENDPOINT, parameters)

    # attempt to decode response as JSON
    try:
        launches = resp.json()
    except json.JSONDecodeError as ex:
        raise LL2RequestError(f"Unable to decode response JSON {ex}") from ex

    try:
        check_response(launches)
        logging.info("upcoming launches: %s", launches["count"])
    except LL2RequestError as ex:
        logging.error("Error encounted attempting to get upcoming launches: %s", ex)
        return None

    return launches


def check_response(launches: Any):
    """checks to make sure the decoded response is a dict
    contains the expected fields Raises a request error if not"""
    if (
        launches is None
        or not isinstance(launches, dict)
        or "count" not in launches
        or "results" not in launches
    ):
        raise LL2RequestError("unexpected response")
