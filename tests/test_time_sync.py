import time

from unittest.mock import MagicMock, patch

import pytest


class TestGetNtpOffset:
    @patch("utils.time_sync.ntplib.NTPClient")
    def test_returns_offset_on_success(self, mock_ntp_cls):
        mock_response = MagicMock()
        mock_response.offset = 0.123
        mock_ntp_cls.return_value.request.return_value = mock_response

        from utils.time_sync import get_ntp_offset

        offset = get_ntp_offset()
        assert offset == pytest.approx(0.123)

    @patch("utils.time_sync.ntplib.NTPClient")
    def test_returns_zero_on_failure(self, mock_ntp_cls):
        mock_ntp_cls.return_value.request.side_effect = Exception("timeout")

        from utils.time_sync import get_ntp_offset

        offset = get_ntp_offset()
        assert offset == 0.0


class TestGetAccurateTime:
    @patch("utils.time_sync._ntp_offset", 1.5)
    @patch("utils.time_sync.time.time", return_value=1000.0)
    def test_returns_calibrated_timestamp(self, mock_time):
        from utils.time_sync import get_accurate_time

        result = get_accurate_time()
        assert isinstance(result, float)
        assert result == pytest.approx(1001.5)


class TestWaitUntil:
    @patch("utils.time_sync._ntp_offset", 0.0)
    def test_returns_immediately_for_past_target(self):
        from utils.time_sync import wait_until

        target = time.time() - 1.0
        start = time.time()
        wait_until(target)
        elapsed = time.time() - start
        assert elapsed < 0.1

    @patch("utils.time_sync._ntp_offset", 0.0)
    def test_waits_until_target(self):
        from utils.time_sync import wait_until

        target = time.time() + 0.05
        wait_until(target)
        assert time.time() >= target - 0.01
