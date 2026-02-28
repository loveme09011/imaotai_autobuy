from unittest.mock import MagicMock, patch

import pytest


class TestSendNotification:
    @patch("utils.notifier.requests.post")
    def test_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 0, "message": "success"}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        from utils.notifier import send_notification

        result = send_notification("测试标题", "测试内容", "test_key")

        assert result is True
        mock_post.assert_called_once_with(
            "https://sctapi.ftqq.com/test_key.send",
            data={"title": "测试标题", "desp": "测试内容"},
            timeout=10,
        )

    @patch("utils.notifier.requests.post")
    def test_server_returns_error_code(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"code": 40001, "message": "invalid key"}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        from utils.notifier import send_notification

        result = send_notification("标题", "内容", "bad_key")

        assert result is False

    @patch("utils.notifier.requests.post")
    def test_network_error_returns_false(self, mock_post):
        mock_post.side_effect = Exception("Connection timeout")

        from utils.notifier import send_notification

        result = send_notification("标题", "内容", "test_key")

        assert result is False

    @patch("utils.notifier.requests.post")
    def test_http_error_returns_false(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("500 Server Error")
        mock_post.return_value = mock_resp

        from utils.notifier import send_notification

        result = send_notification("标题", "内容", "test_key")

        assert result is False
