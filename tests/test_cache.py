"""unittests for launches.cache

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from launches.cache import LaunchCache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_logger():
    """Mock the logger to prevent actual logging during tests"""
    with patch("launches.cache.logger") as mock_log:
        yield mock_log


@pytest.fixture
def sample_launch():
    """Sample launch data"""
    return {
        "id": "test-launch-1",
        "name": "Test Launch 1",
        "status": {"id": 1, "name": "Go for Launch"},
        "window_start": "2024-06-01T12:00:00Z",
        "net": "2024-06-01T12:00:00Z",
        "infoURLs": [{"url": "https://example.com/launch1"}],
        "vidURLs": [{"url": "https://youtube.com/watch?v=123"}],
    }


@pytest.fixture
def sample_launches(sample_launch):
    """Sample launches response data"""
    return {"count": 1, "next": None, "previous": None, "results": [sample_launch]}


@pytest.fixture
def updated_launch(sample_launch):
    """Sample launch with updated status"""
    updated = sample_launch.copy()
    updated["status"] = {"id": 2, "name": "Launch Successful"}
    return updated


@pytest.fixture
def new_launch():
    """A completely new launch"""
    return {
        "id": "test-launch-2",
        "name": "Test Launch 2",
        "status": {"id": 1, "name": "Go for Launch"},
        "window_start": "2024-06-02T12:00:00Z",
        "net": "2024-06-02T12:00:00Z",
        "infoURLs": [{"url": "https://example.com/launch2"}],
        "vidURLs": [{"url": "https://youtube.com/watch?v=456"}],
    }


def test_init_disabled():
    """Test initialization with cache disabled"""
    cache = LaunchCache(enabled=False)
    assert cache.enabled is False
    assert not hasattr(cache, "cache_dir")
    assert not hasattr(cache, "cache_file")


def test_init_custom_dir(temp_cache_dir):
    """Test initialization with custom cache directory"""
    custom_dir = os.path.join(temp_cache_dir, "custom_cache")
    cache = LaunchCache(cache_dir=custom_dir)
    assert cache.enabled is True
    assert cache.cache_dir == Path(custom_dir)
    assert cache.cache_file == Path(custom_dir) / "launches_cache.json"
    assert os.path.exists(custom_dir)


def test_load_cache_no_file(temp_cache_dir):
    """Test loading cache when no file exists"""
    cache = LaunchCache(cache_dir=temp_cache_dir)
    result = cache._load_cache()
    assert result == {}


def test_load_cache_invalid_json(temp_cache_dir, mock_logger):
    """Test loading cache with invalid JSON content"""
    cache_file = Path(temp_cache_dir) / "launches_cache.json"
    with open(cache_file, "w") as f:
        f.write("invalid json")

    cache = LaunchCache(cache_dir=temp_cache_dir)

    assert cache._previous_launches == {}
    mock_logger.warning.assert_called_once()


def test_load_cache_valid_json(temp_cache_dir, sample_launches):
    """Test loading cache with valid JSON content"""
    cache_file = Path(temp_cache_dir) / "launches_cache.json"
    with open(cache_file, "w") as f:
        json.dump(sample_launches, f)

    cache = LaunchCache(cache_dir=temp_cache_dir)

    assert cache._previous_launches == sample_launches


def test_save_cache(temp_cache_dir, sample_launches):
    """Test saving cache"""
    cache = LaunchCache(cache_dir=temp_cache_dir)
    cache._save_cache(sample_launches)

    # Verify file was created with correct content
    cache_file = Path(temp_cache_dir) / "launches_cache.json"
    assert os.path.exists(cache_file)

    with open(cache_file, "r") as f:
        saved_data = json.load(f)

    assert saved_data == sample_launches


def test_save_cache_io_error(temp_cache_dir, sample_launches, mock_logger):
    """Test saving cache with IO error"""
    cache = LaunchCache(cache_dir=temp_cache_dir)

    # Mock open to raise an IOError
    with patch("builtins.open", side_effect=IOError("Test IO error")):
        cache._save_cache(sample_launches)

    mock_logger.warning.assert_called_once()


def test_get_changed_launches_disabled(sample_launches):
    """Test get_changed_launches with cache disabled"""
    cache = LaunchCache(enabled=False)
    result = cache.get_changed_launches(sample_launches)
    assert result == sample_launches


def test_get_changed_launches_no_previous(temp_cache_dir, sample_launches, mock_logger):
    """Test get_changed_launches with no previous cache"""
    cache = LaunchCache(cache_dir=temp_cache_dir)

    result = cache.get_changed_launches(sample_launches)

    assert result == sample_launches
    # Verify cache was saved
    with open(cache.cache_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data == sample_launches


def test_get_changed_launches_no_changes(temp_cache_dir, sample_launches, mock_logger):
    """Test get_changed_launches with no changes"""
    cache = LaunchCache(cache_dir=temp_cache_dir)

    # First call to set initial cache
    cache.get_changed_launches(sample_launches)

    # Second call with same data
    result = cache.get_changed_launches(sample_launches)

    # Should return empty results
    assert result["count"] == 0
    assert len(result["results"]) == 0


def test_get_changed_launches_new_launch(temp_cache_dir, sample_launches, new_launch, mock_logger):
    """Test get_changed_launches with a new launch"""
    cache = LaunchCache(cache_dir=temp_cache_dir)

    # First call to set initial cache
    cache.get_changed_launches(sample_launches)

    # Create new launches dict with original and new launch
    new_launches = {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [sample_launches["results"][0], new_launch],
    }

    # Second call with new data
    result = cache.get_changed_launches(new_launches)

    # Should return only the new launch
    assert result["count"] == 1
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == new_launch["id"]


def test_get_changed_launches_modified_launch(
    temp_cache_dir, sample_launches, updated_launch, mock_logger
):
    """Test get_changed_launches with a modified launch"""
    cache = LaunchCache(cache_dir=temp_cache_dir)

    # First call to set initial cache
    cache.get_changed_launches(sample_launches)

    # Create updated launches dict
    updated_launches = {"count": 1, "next": None, "previous": None, "results": [updated_launch]}

    # Second call with updated data
    result = cache.get_changed_launches(updated_launches)

    # Should return the updated launch
    assert result["count"] == 1
    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == updated_launch["id"]
    assert result["results"][0]["status"]["name"] == "Launch Successful"


def test_is_launch_significantly_changed_status(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with status change"""
    # Create a modified launch with changed status
    modified_launch = sample_launch.copy()
    modified_launch["status"] = {"id": 2, "name": "Launch Successful"}

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is True
    mock_logger.info.assert_called_once()


def test_is_launch_significantly_changed_window_start(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with window_start change"""
    # Create a modified launch with changed window_start
    modified_launch = sample_launch.copy()
    modified_launch["window_start"] = "2024-06-01T13:00:00Z"

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is True
    mock_logger.info.assert_called_once()


def test_is_launch_significantly_changed_info_urls(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with infoURLs change"""
    # Create a modified launch with changed infoURLs
    modified_launch = sample_launch.copy()
    modified_launch["infoURLs"] = [
        {"url": "https://example.com/launch1"},
        {"url": "https://example.com/launch1/update"},
    ]

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is True
    mock_logger.info.assert_called_once()


def test_is_launch_significantly_changed_vid_urls(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with vidURLs change"""
    # Create a modified launch with changed vidURLs
    modified_launch = sample_launch.copy()
    modified_launch["vidURLs"] = [
        {"url": "https://youtube.com/watch?v=123"},
        {"url": "https://youtube.com/watch?v=456"},
    ]

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is True
    mock_logger.info.assert_called_once()


def test_is_launch_significantly_changed_net(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with net change"""
    # Create a modified launch with changed net
    modified_launch = sample_launch.copy()
    modified_launch["net"] = "2024-06-01T14:00:00Z"

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is True
    mock_logger.info.assert_called_once()


def test_is_launch_significantly_changed_no_change(sample_launch, mock_logger):
    """Test _is_launch_significantly_changed with no significant changes"""
    # Create a copy with no significant changes
    modified_launch = sample_launch.copy()
    modified_launch["id"] = sample_launch["id"]  # Same ID

    result = LaunchCache._is_launch_significantly_changed(sample_launch, modified_launch)
    assert result is False
    mock_logger.info.assert_not_called()
