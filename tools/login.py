"""i茅台登录工具 — 通过手机号+验证码获取 token 并写入配置文件."""

import shutil
import sys
import uuid
from pathlib import Path

import requests
import yaml

BASE_URL = "https://app.moutai519.com.cn"
SEND_CODE_PATH = "/xhr/front/user/register/vcode"
LOGIN_PATH = "/xhr/front/user/register/login"
APP_VERSION = "1.7.6"

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
CONFIG_PATH = CONFIG_DIR / "config.yaml"
EXAMPLE_PATH = CONFIG_DIR / "config.example.yaml"


def generate_device_id() -> str:
    """生成设备ID：UUID4 去掉横线并大写."""
    return uuid.uuid4().hex.upper()


def _get_headers(device_id: str = "") -> dict:
    return {
        "MT-Device-ID": device_id,
        "MT-APP-Version": APP_VERSION,
        "Authorization": "",
        "Content-Type": "application/json",
    }


def _get_timestamp() -> str:
    import time
    return str(int(time.time() * 1000))


def send_code(mobile: str) -> dict:
    """发送验证码."""
    url = f"{BASE_URL}{SEND_CODE_PATH}"
    payload = {"mobile": mobile, "timestamp": _get_timestamp()}
    resp = requests.post(url, json=payload, headers=_get_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def login(mobile: str, code: str, device_id: str) -> dict:
    """登录并返回 token 和 user_id."""
    url = f"{BASE_URL}{LOGIN_PATH}"
    payload = {
        "mobile": mobile,
        "vCode": code,
        "deviceId": device_id,
        "timestamp": _get_timestamp(),
    }
    resp = requests.post(url, json=payload, headers=_get_headers(device_id), timeout=10)
    resp.raise_for_status()
    result = resp.json()
    data = result.get("data", result)
    return {"token": data.get("token", ""), "user_id": str(data.get("userId", ""))}


def mask_phone(phone: str) -> str:
    """手机号脱敏：保留后4位，其余用*替代."""
    if len(phone) <= 4:
        return phone
    return "*" * (len(phone) - 4) + phone[-4:]


def load_config() -> dict:
    """加载配置文件，不存在则从 example 复制."""
    if not CONFIG_PATH.exists():
        if EXAMPLE_PATH.exists():
            shutil.copy(EXAMPLE_PATH, CONFIG_PATH)
        else:
            return {"accounts": [], "settings": {"sendkey": ""}, "schedule": {}}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict) -> None:
    """保存配置到 config.yaml."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def write_account(config: dict, account: dict, mode: str = "append") -> dict:
    """将账号信息写入配置.

    mode:
        - "append": 追加到 accounts 列表
        - "replace": 清空 accounts 列表后写入
    """
    if "accounts" not in config:
        config["accounts"] = []

    if mode == "replace":
        config["accounts"] = [account]
    else:
        config["accounts"].append(account)

    save_config(config)
    return config


def main() -> None:
    print("=" * 40)
    print("  i茅台登录工具")
    print("=" * 40)

    # 1. 输入手机号
    mobile = input("\n请输入手机号: ").strip()
    if not mobile:
        print("手机号不能为空")
        sys.exit(1)

    # 2. 发送验证码
    print(f"\n正在向 {mask_phone(mobile)} 发送验证码...")
    try:
        send_code(mobile)
        print("验证码发送成功！")
    except requests.RequestException as e:
        print(f"发送验证码失败: {e}")
        sys.exit(1)

    # 3. 输入验证码
    code = input("请输入验证码: ").strip()
    if not code:
        print("验证码不能为空")
        sys.exit(1)

    # 4. 生成 device_id
    device_id = generate_device_id()

    # 5. 登录
    print("\n正在登录...")
    try:
        result = login(mobile, code, device_id)
    except requests.RequestException as e:
        print(f"登录失败: {e}")
        sys.exit(1)

    token = result["token"]
    user_id = result["user_id"]

    if not token:
        print("登录失败：未获取到 token")
        sys.exit(1)

    # 6. 写入配置
    config = load_config()
    account = {
        "phone": mobile,
        "token": token,
        "device_id": device_id,
        "user_id": user_id,
        "province": "",
        "city": "",
        "items": ["10056"],
    }

    existing_accounts = config.get("accounts", [])
    # 过滤掉 example 占位账号
    real_accounts = [a for a in existing_accounts if a.get("token") != "your_token_here"]

    mode = "append"
    if real_accounts:
        print(f"\n当前已有 {len(real_accounts)} 个有效账号")
        choice = input("请选择操作 [1] 新增账号 [2] 替换所有账号: ").strip()
        if choice == "2":
            mode = "replace"

    if mode == "replace":
        write_account(config, account, mode="replace")
    else:
        # 替换掉占位账号，保留真实账号
        config["accounts"] = real_accounts
        write_account(config, account, mode="append")

    # 7. 打印结果
    print("\n" + "=" * 40)
    print("  登录成功！")
    print("=" * 40)
    print(f"  手机号:    {mask_phone(mobile)}")
    print(f"  user_id:   {user_id}")
    print(f"  device_id: {device_id}")
    print(f"  token:     {token[:8]}...")
    print("=" * 40)
    print(f"\n配置已写入: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
