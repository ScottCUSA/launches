"""Space Launch Notifications - Cache Module

This module provides caching functionality for launch responses to avoid
redundant notifications for unchanged launches.

Copyright ©️ 2024 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from loguru import logger


class LaunchCache:
    """Cache for Launch Library 2 API responses to avoid redundant notifications."""

    def __init__(self, cache_dir: str | None = None, enabled: bool = True):
        """Initialize the launch cache.

        Args:
            cache_dir (str, optional): Directory to store cache files. Defaults to ./.launches_cache
            enabled (bool, optional): Whether the cache is enabled. Defaults to True.
        """
        self.enabled = enabled
        if not enabled:
            return

        if cache_dir is None:
            cache_dir = "./.launches_cache"

        self.cache_dir = Path(cache_dir)
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = self.cache_dir / "launches_cache.json"
        self._previous_launches = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """Load the cache from disk.

        Returns:
            Dict[str, Any]: The cached launches data or an empty dict if no cache exists.
        """
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}

    def _save_cache(self, launches: Dict[str, Any]) -> None:
        """Save the launches data to cache.

        Args:
            launches (Dict[str, Any]): The launches data to cache.
        """
        try:
            with open(self.cache_file, "w") as f:
                json.dump(launches, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save cache: {e}")

    def get_changed_launches(self, new_launches: Dict[str, Any]) -> Dict[str, Any]:
        """Get launches that have changed from the previous cached response.

        Args:
            new_launches (Dict[str, Any]): The new launches data.

        Returns:
            Dict[str, Any]: A dict containing only changed launches.
        """
        if not self.enabled:
            return new_launches

        if not self._previous_launches:
            # No previous cache or cache disabled - return all launches
            self._previous_launches = new_launches
            self._save_cache(new_launches)
            return new_launches

        changed_launches = {
            "count": 0,
            "next": new_launches.get("next"),
            "previous": new_launches.get("previous"),
            "results": [],
        }

        previous_launches_by_id = {
            launch["id"]: launch for launch in self._previous_launches.get("results", [])
        }

        # Track which launches have changed
        for launch in new_launches.get("results", []):
            launch_id = launch["id"]

            if launch_id not in previous_launches_by_id:
                # This is a new launch
                logger.info(f"New launch detected: {launch['name']}")
                changed_launches["results"].append(launch)
                continue

            previous_launch = previous_launches_by_id[launch_id]

            # Check if key attributes have changed
            if self._is_launch_significantly_changed(previous_launch, launch):
                logger.info(f"Launch changed: {launch['name']}")
                changed_launches["results"].append(launch)

        # Update the count of changed launches
        changed_launches["count"] = len(changed_launches["results"])

        # Save the new launches as the previous launches
        self._previous_launches = new_launches
        self._save_cache(new_launches)

        return changed_launches

    @staticmethod
    def _is_launch_significantly_changed(
        prev_launch: Dict[str, Any], new_launch: Dict[str, Any]
    ) -> bool:
        """Check if a launch has significantly changed.

        Args:
            prev_launch (Dict[str, Any]): Previous launch data.
            new_launch (Dict[str, Any]): New launch data.

        Returns:
            bool: True if the launch has significantly changed, False otherwise.
        """
        # Check if status has changed
        if prev_launch.get("status", {}).get("name") != new_launch.get("status", {}).get("name"):
            logger.info(
                f"Launch status changed from {prev_launch.get('status', {}).get('name')} "
                f"to {new_launch.get('status', {}).get('name')}"
            )
            return True

        # Check if window_start has changed
        if prev_launch.get("window_start") != new_launch.get("window_start"):
            logger.info(
                f"Launch window_start changed from {prev_launch.get('window_start')} "
                f"to {new_launch.get('window_start')}"
            )
            return True

        # Check if new information URLs were added
        prev_urls = {info_url.get("url") for info_url in prev_launch.get("infoURLs", [])}
        new_urls = {info_url.get("url") for info_url in new_launch.get("infoURLs", [])}

        if prev_urls != new_urls:
            logger.info(f"Launch info URLs changed: {len(new_urls - prev_urls)} new URLs added")
            return True

        # Check if new video URLs were added
        prev_vid_urls = {vid_url.get("url") for vid_url in prev_launch.get("vidURLs", [])}
        new_vid_urls = {vid_url.get("url") for vid_url in new_launch.get("vidURLs", [])}

        if prev_vid_urls != new_vid_urls:
            logger.info(
                f"Launch video URLs changed: {len(new_vid_urls - prev_vid_urls)} new video URLs added"
            )
            return True

        # Check if net (No Earlier Than) date has changed
        if prev_launch.get("net") != new_launch.get("net"):
            logger.info(
                f"Launch NET date changed from {prev_launch.get('net')} to {new_launch.get('net')}"
            )
            return True

        return False
