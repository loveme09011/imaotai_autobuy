import re
import shutil
from pathlib import Path

import pytest
import yaml

from tools.login import (
    generate_device_id,
    load_config,
    login,
    mask_phone,
    save_config,
    send_code,
    write_account,
    CONFIG_PATH,
    EXAMPLE_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """用临时目录替换配置路径，避免污染真实配置."""
    cfg_path = tmp_path / "config.yaml"
    example_path = tmp_path / "config.example.yaml"

    # 复制 example 模板到临时目录
    if EXAMPLE_PATH.exists():
        shutil.copy(EXAMPLE_PATH, example_path)
    else:
        example_path.write_text(
            yaml.dump(
                {
                    "accounts": [
                        {"phone": "13800000001", "token": "your_token_here", "device_id": "your_device_id"}
                    ],
                    "settings": {"sendkey": ""},
                    "schedule": {"reserve_time": "09:59:30"},
                },
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    monkeypatch.setattr("tools.login.CONFIG_PATH", cfg_path)
    monkeypatch.setattr("tools.login.EXAMPLE_PATH", example_path)
    return cfg_path, example_path


@pytest.fixture
def mock_response(mocker):
    resp = mocker.Mock()
    resp.status_code = 200
    resp.raise_for_status = mocker.Mock()
    return resp


# ---------------------------------------------------------------------------
# device_id 格式测试
# ---------------------------------------------------------------------------

class TestGenerateDeviceId:
    def test_length_is_32(self):
        did = generate_device_id()
        assert len(did) == 32

    def test_no_hyphens(self):
        did = generate_device_id()
        assert "-" not in did

    def test_uppercase(self):
        did = generate_device_id()
        assert did == did.upper()

    def test_valid_hex(self):
        did = generate_device_id()
        assert re.fullmatch(r"[0-9A-F]{32}", did)

    def test_unique(self):
        ids = {generate_device_id() for _ in range(100)}
        assert len(ids) == 100


# ---------------------------------------------------------------------------
# mask_phone 测试
# ---------------------------------------------------------------------------

class TestMaskPhone:
    def test_standard_11_digit(self):
        assert mask_phone("13812345678") == "*******5678"

    def test_short_phone(self):
        assert mask_phone("1234") == "1234"

    def test_empty(self):
        assert mask_phone("") == ""


# ---------------------------------------------------------------------------
# 配置文件读写测试
# ---------------------------------------------------------------------------

class TestConfigReadWrite:
    def test_load_creates_from_example(self, tmp_config):
        cfg_path, example_path = tmp_config
        assert not cfg_path.exists()
        config = load_config()
        assert cfg_path.exists()
        assert "accounts" in config

    def test_load_existing_config(self, tmp_config):
        cfg_path, _ = tmp_config
        data = {"accounts": [{"phone": "13900001111", "token": "t1"}], "settings": {}}
        cfg_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        config = load_config()
        assert config["accounts"][0]["phone"] == "13900001111"

    def test_save_and_reload(self, tmp_config):
        cfg_path, _ = tmp_config
        data = {"accounts": [], "settings": {"sendkey": "abc"}}
        save_config(data)
        reloaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        assert reloaded["settings"]["sendkey"] == "abc"


# ---------------------------------------------------------------------------
# 多账号追加/替换逻辑
# ---------------------------------------------------------------------------

class TestWriteAccount:
    def test_append_account(self, tmp_config):
        config = {"accounts": [{"phone": "111", "token": "t1"}]}
        new_account = {"phone": "222", "token": "t2"}
        result = write_account(config, new_account, mode="append")
        assert len(result["accounts"]) == 2
        assert result["accounts"][-1]["phone"] == "222"

    def test_replace_accounts(self, tmp_config):
        config = {"accounts": [{"phone": "111", "token": "t1"}, {"phone": "222", "token": "t2"}]}
        new_account = {"phone": "333", "token": "t3"}
        result = write_account(config, new_account, mode="replace")
        assert len(result["accounts"]) == 1
        assert result["accounts"][0]["phone"] == "333"

    def test_append_to_empty(self, tmp_config):
        config = {}
        new_account = {"phone": "444", "token": "t4"}
        result = write_account(config, new_account, mode="append")
        assert len(result["accounts"]) == 1

    def test_config_persisted_to_file(self, tmp_config):
        cfg_path, _ = tmp_config
        config = {"accounts": [], "settings": {}}
        new_account = {"phone": "555", "token": "t5", "device_id": "D5"}
        write_account(config, new_account, mode="append")

        saved = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        assert saved["accounts"][0]["phone"] == "555"
        assert saved["accounts"][0]["device_id"] == "D5"


# ---------------------------------------------------------------------------
# send_code / login 网络请求 mock 测试
# ---------------------------------------------------------------------------

class TestSendCode:
    def test_send_code_success(self, mocker, mock_response):
        mock_response.json.return_value = {"code": 200}
        mocker.patch("tools.login.requests.post", return_value=mock_response)
        result = send_code("13800138000")
        assert result == {"code": 200}

    def test_send_code_calls_correct_url(self, mocker, mock_response):
        mock_response.json.return_value = {"code": 200}
        mock_post = mocker.patch("tools.login.requests.post", return_value=mock_response)
        send_code("13800138000")
        call_url = mock_post.call_args[0][0]
        assert "/prod/ct/platformgw/moutai/appService/v2/user/send/code" in call_url


class TestLogin:
    def test_login_returns_token_and_user_id(self, mocker, mock_response):
        mock_response.json.return_value = {"data": {"token": "tok_abc", "userId": "99001"}}
        mocker.patch("tools.login.requests.post", return_value=mock_response)
        result = login("13800138000", "1234", "DEVICE123")
        assert result["token"] == "tok_abc"
        assert result["user_id"] == "99001"

    def test_login_sends_device_id_in_header(self, mocker, mock_response):
        mock_response.json.return_value = {"data": {"token": "t", "userId": "u"}}
        mock_post = mocker.patch("tools.login.requests.post", return_value=mock_response)
        login("13800138000", "1234", "MY_DEVICE")
        headers = mock_post.call_args[1]["headers"]
        assert headers["MT-Device-ID"] == "MY_DEVICE"
        assert headers["Authorization"] == ""
