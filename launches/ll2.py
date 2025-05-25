"""Space Launch Notifications - Launch Library 2 Requests Module

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
from datetime import datetime
from typing import Any

import requests
from loguru import logger

from launches.errors import LL2RequestError

LAUNCH_DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LL2_API_URL = {
    "prod": "https://ll.thespacedevs.com/2.2.0/",
    "dev": "https://lldev.thespacedevs.com/2.2.0/",
}


class LaunchLibrary2Client:
    LL2_UPCOMING_ENDPOINT = "launch/upcoming/"
    REQUEST_TIMEOUT = 30

    def __init__(self, env: str = "prod") -> None:
        if env not in LL2_API_URL:
            raise ValueError(f"Unknown LL2 environment: {env}")
        self.env = env
        self.base_url = LL2_API_URL[env]

    def ll2_get(self, endpoint: str, parameters: dict) -> requests.Response:
        """make a get request to the launch library at the
        provided endpoint using the provided parameters"""
        logger.info(
            "Making request to space launch library endpoint {} with parameters: {}",
            endpoint,
            parameters,
        )
        try:
            resp = requests.get(
                self.base_url + endpoint,
                params=parameters,
                timeout=self.REQUEST_TIMEOUT,
            )
            logger.info("Space launch library response status code: {}", resp.status_code)
            resp.raise_for_status()
        except requests.exceptions.RequestException as ex:
            raise LL2RequestError(f"Error getting space launches {ex}") from ex

        return resp

    def get_upcoming_launches_within_window(
        self,
        window_start_lt: datetime,
    ) -> dict[str, Any]:
        """Make a request to the space launch libary for upcoming launches where the
        window is less than the provided datetime raises a RequestError
        if there are issues with the request or response.

        Args:
            window_start_lt (datetime): The cutoff time for the launch window.

        Returns:
            dict[str, Any]: Dictionary containing launch data.
        """
        parameters = {
            "window_start__lt": window_start_lt.strftime(LAUNCH_DT_FORMAT),
            "hide_recent_previous": True,
            "mode": "detailed",
        }

        resp = self.ll2_get(self.LL2_UPCOMING_ENDPOINT, parameters)

        # attempt to decode response as JSON
        try:
            launches = resp.json()
            logger.debug(f"ll2 response: {resp.text}")
        except json.JSONDecodeError as ex:
            raise LL2RequestError(f"Unable to decode response JSON {ex}") from ex

        self.check_response(launches)
        logger.info("upcoming launches: {}", launches["count"])

        return launches

    @staticmethod
    def check_response(launches: Any) -> None:
        """checks to make sure the decoded response is a dict
        contains the expected fields Raises a request error if not"""
        if (
            launches is None
            or not isinstance(launches, dict)
            or "count" not in launches
            or "results" not in launches
        ):
            raise LL2RequestError("unexpected ll2 response")
