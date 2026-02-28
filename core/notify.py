from datetime import datetime

from utils.logger import get_logger
from utils.notifier import send_notification

logger = get_logger("core.notify")


def format_results(results: list[dict]) -> tuple[str, str]:
    """将申购结果列表格式化为推送消息。

    Args:
        results: 申购结果列表，每项包含 mobile, item_code, success, message

    Returns:
        (title, content) 元组
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"i茅台申购结果 - {now}"

    lines: list[str] = []
    expired_mobiles: list[str] = []

    for r in results:
        mobile = r.get("mobile", "unknown")
        suffix = mobile[-4:] if len(mobile) >= 4 else mobile
        item_code = r.get("item_code", "")
        status = "成功" if r.get("success") else "失败"
        message = r.get("message", "")
        item_label = f"[{item_code}]" if item_code else ""
        lines.append(f"- {suffix}{item_label}: {status} | {message}")
        if r.get("token_expired"):
            expired_mobiles.append(suffix)

    if expired_mobiles:
        lines.append("")
        lines.append("⚠️ Token 已过期，请重新登录: " + ", ".join(expired_mobiles))

    content = "\n".join(lines)
    return title, content


def notify_results(results: list[dict], config: dict) -> None:
    """汇总申购结果并推送通知。

    Args:
        results: 申购结果列表
        config: 配置字典，从 config['settings']['sendkey'] 读取推送 key
    """
    sendkey = config.get("settings", {}).get("sendkey")
    if not sendkey:
        logger.info("未配置 sendkey，跳过推送通知")
        return

    title, content = format_results(results)
    ok = send_notification(title, content, sendkey)
    if ok:
        logger.info("申购结果推送完成")
    else:
        logger.warning("申购结果推送失败")
