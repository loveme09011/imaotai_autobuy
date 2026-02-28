from core.health import check_config, check_token_valid


class TestCheckConfig:
    def test_valid_config(self):
        config = {
            "accounts": [
                {"mobile": "13800000001", "token": "real_token_abc", "device_id": "dev1", "user_id": "uid1"},
            ]
        }
        assert check_config(config) == []

    def test_missing_accounts_key(self):
        errors = check_config({"item_code": "10056"})
        assert any("accounts" in e for e in errors)

    def test_accounts_not_list(self):
        errors = check_config({"accounts": "not_a_list"})
        assert any("列表" in e for e in errors)

    def test_empty_accounts(self):
        errors = check_config({"accounts": []})
        assert any("为空" in e for e in errors)

    def test_account_missing_fields(self):
        config = {
            "accounts": [
                {"mobile": "13800000001"},
            ]
        }
        errors = check_config(config)
        assert any("token" in e for e in errors)
        assert any("device_id" in e for e in errors)
        assert any("user_id" in e for e in errors)

    def test_placeholder_values_detected(self):
        config = {
            "accounts": [
                {"mobile": "13800000001", "token": "your_token_here", "device_id": "dev1", "user_id": "uid1"},
            ]
        }
        errors = check_config(config)
        assert any("token" in e for e in errors)

    def test_non_dict_config(self):
        errors = check_config("not_a_dict")
        assert any("格式错误" in e for e in errors)

    def test_non_dict_account(self):
        config = {"accounts": ["not_a_dict"]}
        errors = check_config(config)
        assert any("格式错误" in e for e in errors)

    def test_multiple_accounts_partial_valid(self):
        config = {
            "accounts": [
                {"mobile": "13800000001", "token": "real_token", "device_id": "dev1", "user_id": "uid1"},
                {"mobile": "13800000002"},
            ]
        }
        errors = check_config(config)
        assert any("账号#2" in e for e in errors)
        assert not any("账号#1" in e for e in errors)


class TestCheckTokenValid:
    def test_valid_token(self):
        assert check_token_valid({"token": "Bearer abc123xyz"}) is True

    def test_placeholder_token(self):
        assert check_token_valid({"token": "your_token_here"}) is False

    def test_empty_token(self):
        assert check_token_valid({"token": ""}) is False

    def test_missing_token(self):
        assert check_token_valid({}) is False

    def test_short_token(self):
        assert check_token_valid({"token": "abc"}) is False
