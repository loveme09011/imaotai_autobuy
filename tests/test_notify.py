from unittest.mock import patch

import pytest


class TestFormatResults:
    def test_format_single_success(self):
        from core.notify import format_results

        results = [{"mobile": "13800000001", "success": True, "message": "申购成功"}]
        title, content = format_results(results)

        assert "i茅台申购结果" in title
        assert "0001" in content
        assert "成功" in content

    def test_format_multiple_results(self):
        from core.notify import format_results

        results = [
            {"mobile": "13800000001", "success": True, "message": "申购成功"},
            {"mobile": "13800000002", "success": False, "message": "已申购过"},
        ]
        title, content = format_results(results)

        lines = content.strip().split("\n")
        assert len(lines) == 2
        assert "0001" in lines[0]
        assert "成功" in lines[0]
        assert "0002" in lines[1]
        assert "失败" in lines[1]
        assert "已申购过" in lines[1]

    def test_format_empty_results(self):
        from core.notify import format_results

        title, content = format_results([])

        assert "i茅台申购结果" in title
        assert content == ""

    def test_format_short_mobile(self):
        from core.notify import format_results

        results = [{"mobile": "123", "success": True, "message": "ok"}]
        title, content = format_results(results)

        assert "123" in content


class TestNotifyResults:
    @patch("core.notify.send_notification", return_value=True)
    def test_sends_when_sendkey_configured(self, mock_send):
        from core.notify import notify_results

        results = [{"mobile": "13800000001", "success": True, "message": "申购成功"}]
        config = {"settings": {"sendkey": "my_key"}}

        notify_results(results, config)

        mock_send.assert_called_once()
        args = mock_send.call_args
        assert "i茅台申购结果" in args[0][0]
        assert args[0][2] == "my_key"

    @patch("core.notify.send_notification")
    def test_skips_when_no_sendkey(self, mock_send):
        from core.notify import notify_results

        results = [{"mobile": "13800000001", "success": True, "message": "ok"}]
        config = {"settings": {}}

        notify_results(results, config)

        mock_send.assert_not_called()

    @patch("core.notify.send_notification")
    def test_skips_when_no_settings(self, mock_send):
        from core.notify import notify_results

        results = [{"mobile": "13800000001", "success": True, "message": "ok"}]
        config = {}

        notify_results(results, config)

        mock_send.assert_not_called()

    @patch("core.notify.send_notification")
    def test_skips_when_sendkey_empty(self, mock_send):
        from core.notify import notify_results

        results = []
        config = {"settings": {"sendkey": ""}}

        notify_results(results, config)

        mock_send.assert_not_called()
