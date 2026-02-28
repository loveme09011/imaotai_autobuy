import sys
from pathlib import Path

import yaml

from core.health import check_config
from utils.logger import setup_logger, get_logger
from scheduler.runner import start

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

    errors = check_config(config)
    if errors:
        for err in errors:
            log.error("配置检查失败: {}", err)
        sys.exit(1)
    log.info("配置检查通过")

    accounts = config.get("accounts", [])
    item_code = config.get("item_code", "10056")
    if isinstance(item_code, list):
        item_codes = item_code
    else:
        item_codes = [item_code]
    city_code = config.get("city_code", "520100")

    # 打印配置摘要
    log.info("===== 配置摘要 =====")
    log.info("账号数量: {}", len(accounts))
    log.info("目标商品: {}", item_codes)
    log.info("城市代码: {}", city_code)
    log.info("===================")

    start(
        config_path=str(CONFIG_PATH),
        item_codes=item_codes,
        city_code=city_code,
    )


if __name__ == "__main__":
    main()
