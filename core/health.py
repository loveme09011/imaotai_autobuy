from utils.logger import get_logger

logger = get_logger("core.health")

REQUIRED_CONFIG_KEYS = ("accounts",)
REQUIRED_ACCOUNT_FIELDS = ("mobile", "token", "device_id", "user_id")


def check_config(config: dict) -> list[str]:
    """检查配置文件完整性，返回错误信息列表。空列表表示通过。"""
    errors: list[str] = []

    if not isinstance(config, dict):
        return ["配置文件格式错误，期望字典类型"]

    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            errors.append(f"缺少必填配置项: {key}")

    accounts = config.get("accounts", [])
    if not isinstance(accounts, list):
        errors.append("accounts 配置项应为列表")
        return errors

    if not accounts:
        errors.append("accounts 列表为空，请至少配置一个账号")
        return errors

    for i, account in enumerate(accounts):
        if not isinstance(account, dict):
            errors.append(f"账号#{i + 1} 格式错误，期望字典类型")
            continue
        for field in REQUIRED_ACCOUNT_FIELDS:
            value = account.get(field)
            if not value or (isinstance(value, str) and value.startswith("your_")):
                errors.append(f"账号#{i + 1} 缺少或未填写字段: {field}")

    return errors


def check_token_valid(account: dict) -> bool:
    """检测 token 是否可能已过期（简单格式校验）。

    真正的有效性需要调用 API 验证，此处仅做基础检查。
    """
    token = account.get("token", "")
    if not token or token.startswith("your_"):
        return False
    if len(token) < 10:
        return False
    return True
