from unittest.mock import MagicMock, patch

import pytest


MOCK_ACCOUNT = {
    "mobile": "13800000001",
    "token": "tok_1",
    "device_id": "dev_1",
    "user_id": "uid_1",
}


class TestGetBestShop:
    @patch("core.reservation.ApiClient")
    def test_returns_first_shop_id(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.get_shops.return_value = [
            {"shopId": "shop_001"},
            {"shopId": "shop_002"},
        ]

        from core.reservation import get_best_shop

        shop_id = get_best_shop(mock_client, "520100")
        assert shop_id == "shop_001"

    @patch("core.reservation.ApiClient")
    def test_raises_when_no_shops(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.get_shops.return_value = []

        from core.reservation import get_best_shop

        with pytest.raises(ValueError, match="无可用门店"):
            get_best_shop(mock_client, "520100")


class TestRunReservation:
    @patch("core.reservation.ApiClient")
    def test_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.get_shops.return_value = [{"shopId": "shop_001"}]
        mock_client.reservation.return_value = {"code": 2000, "message": "成功"}
        mock_client_cls.return_value = mock_client

        from core.reservation import run_reservation

        result = run_reservation(MOCK_ACCOUNT, "10056", "520100")
        assert result["success"] is True
        assert result["mobile"] == "13800000001"

    @patch("core.reservation.ApiClient")
    def test_failure_with_error_code(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.get_shops.return_value = [{"shopId": "shop_001"}]
        mock_client.reservation.return_value = {"code": 4001, "message": "已申购过"}
        mock_client_cls.return_value = mock_client

        from core.reservation import run_reservation

        result = run_reservation(MOCK_ACCOUNT, "10056", "520100")
        assert result["success"] is False
        assert "已申购过" in result["message"]

    @patch("core.reservation.ApiClient")
    def test_failure_on_exception(self, mock_client_cls):
        mock_client_cls.side_effect = Exception("网络错误")

        from core.reservation import run_reservation

        result = run_reservation(MOCK_ACCOUNT, "10056", "520100")
        assert result["success"] is False
        assert "网络错误" in result["message"]


class TestRunAll:
    @patch("core.reservation.load_accounts")
    @patch("core.reservation.ApiClient")
    def test_runs_all_accounts(self, mock_client_cls, mock_load):
        mock_load.return_value = [
            MOCK_ACCOUNT,
            {**MOCK_ACCOUNT, "mobile": "13800000002"},
        ]
        mock_client = MagicMock()
        mock_client.get_shops.return_value = [{"shopId": "shop_001"}]
        mock_client.reservation.return_value = {"code": 2000, "message": "成功"}
        mock_client_cls.return_value = mock_client

        from core.reservation import run_all

        results = run_all("config/config.yaml", "10056", "520100")
        assert len(results) == 2
        assert all(r["success"] for r in results)

    @patch("core.reservation.load_accounts")
    def test_returns_empty_when_no_accounts(self, mock_load):
        mock_load.return_value = []

        from core.reservation import run_all

        results = run_all("config/config.yaml", "10056", "520100")
        assert results == []
