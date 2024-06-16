"""unittests for launches.ll2

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import pytest

from launches.ll2 import LL2RequestError, check_response


def test_check_valid_response(valid_launches):
    """check_response should return None if response is valid"""
    assert check_response(valid_launches) is None


def test_check_error_response(invalid_launches):
    """check_response should raise LL2RequestError if response is an error"""
    with pytest.raises(LL2RequestError):
        check_response(invalid_launches)
