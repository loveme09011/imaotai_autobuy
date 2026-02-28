from pathlib import Path

import yaml

from utils.logger import get_logger

logger = get_logger("core.account")

REQUIRED_FIELDS = ("mobile", "token", "device_id", "user_id")


def load_accounts(config_path: str = "config/config.yaml") -> list[dict]:
    """加载账号配置，校验必填字段。缺少字段的账号会被跳过。"""
    path = Path(config_path)
    if not path.exists():
        logger.error("配置文件不存在: {}", config_path)
        return []

    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw_accounts = config.get("accounts", [])
    valid_accounts = []

    for i, account in enumerate(raw_accounts):
        missing = [f for f in REQUIRED_FIELDS if not account.get(f)]
        if missing:
            logger.warning(
                "账号#{} 缺少必填字段: {}, 已跳过", i + 1, ", ".join(missing)
            )
            continue
        valid_accounts.append(account)

    logger.info("加载 {} 个有效账号（共 {} 个）", len(valid_accounts), len(raw_accounts))
    return valid_accounts
