import sys
from pathlib import Path

import yaml

from utils.logger import setup_logger, get_logger

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    if not path.exists():
        print(f"配置文件不存在: {path}")
        print("请复制 config/config.example.yaml 为 config/config.yaml 并填写账号信息")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    setup_logger()
    log = get_logger("main")

    log.info("i茅台自动抢购程序启动")

    config = load_config()
    accounts = config.get("accounts", [])
    log.info(f"已加载 {len(accounts)} 个账号")


if __name__ == "__main__":
    main()
