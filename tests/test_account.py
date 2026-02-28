import pytest
from unittest.mock import patch, mock_open

import yaml


VALID_CONFIG = {
    "accounts": [
        {
            "mobile": "13800000001",
            "token": "tok_1",
            "device_id": "dev_1",
            "user_id": "uid_1",
        },
        {
            "mobile": "13800000002",
            "token": "tok_2",
            "device_id": "dev_2",
            "user_id": "uid_2",
        },
    ]
}

MISSING_FIELD_CONFIG = {
    "accounts": [
        {
            "mobile": "13800000001",
            "token": "tok_1",
            # missing device_id, user_id
        },
        {
            "mobile": "13800000002",
            "token": "tok_2",
            "device_id": "dev_2",
            "user_id": "uid_2",
        },
    ]
}


class TestLoadAccounts:
    @patch("core.account.Path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="",
    )
    @patch("core.account.yaml.safe_load")
    def test_loads_valid_accounts(self, mock_yaml, mock_file, mock_exists):
        mock_yaml.return_value = VALID_CONFIG

        from core.account import load_accounts

        accounts = load_accounts("config/config.yaml")
        assert len(accounts) == 2
        assert accounts[0]["mobile"] == "13800000001"

    @patch("core.account.Path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="",
    )
    @patch("core.account.yaml.safe_load")
    def test_skips_accounts_missing_fields(self, mock_yaml, mock_file, mock_exists):
        mock_yaml.return_value = MISSING_FIELD_CONFIG

        from core.account import load_accounts

        accounts = load_accounts("config/config.yaml")
        assert len(accounts) == 1
        assert accounts[0]["mobile"] == "13800000002"

    @patch("core.account.Path.exists", return_value=False)
    def test_returns_empty_when_file_not_found(self, mock_exists):
        from core.account import load_accounts

        accounts = load_accounts("nonexistent.yaml")
        assert accounts == []
