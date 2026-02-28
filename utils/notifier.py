import requests

from utils.logger import get_logger

logger = get_logger("utils.notifier")

SERVER_CHAN_URL = "https://sctapi.ftqq.com/{}.send"


def send_notification(title: str, content: str, sendkey: str) -> bool:
    """通过 Server酱 推送消息到微信。

    Args:
        title: 消息标题
        content: 消息内容（支持 Markdown）
        sendkey: Server酱 SendKey

    Returns:
        True 表示推送成功，False 表示推送失败
    """
    url = SERVER_CHAN_URL.format(sendkey)
    try:
        resp = requests.post(url, data={"title": title, "desp": content}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            logger.info("Server酱推送成功")
            return True
        logger.warning("Server酱推送失败: {}", data.get("message", "未知错误"))
        return False
    except Exception as e:
        logger.warning("Server酱推送异常: {}", e)
        return False
