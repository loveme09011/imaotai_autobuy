import json
from datetime import datetime
from pathlib import Path

import yaml

from api.client import ApiClient
from core.account import load_accounts
from core.notify import notify_results
from core.reservation import run_all
from utils.logger import get_logger

logger = get_logger("scheduler.jobs")

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def _save_results(results: list[dict]) -> None:
    """将申购结果持久化到本地 JSON 文件（按日期归档）。"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = RESULTS_DIR / f"{today}.json"

    existing: list[dict] = []
    if filepath.exists():
        try:
            existing = json.loads(filepath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }
    existing.append(entry)
    filepath.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("申购结果已保存: {}", filepath)


def reservation_job(config_path: str, item_codes: list[str], city_code: str) -> list[dict]:
    """申购任务：调用 core/reservation.run_all()，记录结果并推送通知。"""
    logger.info("===== 开始执行申购任务 =====")
    results = run_all(config_path, item_codes, city_code)
    success = sum(1 for r in results if r["success"])
    logger.info("申购任务完成: {}/{} 成功", success, len(results))

    _save_results(results)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        notify_results(results, config)
    except Exception as e:
        logger.warning("推送通知时出错: {}", e)

    return results


def travel_job(config_path: str) -> list[dict]:
    """旅行任务：对所有账号调用 api/client.travel()，记录结果。"""
    logger.info("===== 开始执行旅行任务 =====")
    accounts = load_accounts(config_path)
    if not accounts:
        logger.warning("无有效账号，跳过旅行")
        return []

    results: list[dict] = []
    for account in accounts:
        mobile = account.get("mobile", "unknown")
        try:
            client = ApiClient(account)
            resp = client.travel()
            code = resp.get("code", -1)
            if code == 2000:
                logger.info("[{}] 旅行成功", mobile)
                results.append({"mobile": mobile, "success": True, "message": "旅行成功"})
            else:
                msg = resp.get("message", "未知错误")
                logger.warning("[{}] 旅行失败: {}", mobile, msg)
                results.append({"mobile": mobile, "success": False, "message": msg})
        except Exception as e:
            logger.error("[{}] 旅行异常: {}", mobile, e)
            results.append({"mobile": mobile, "success": False, "message": str(e)})

    success = sum(1 for r in results if r["success"])
    logger.info("旅行任务完成: {}/{} 成功", success, len(results))
    return results
