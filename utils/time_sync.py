import time

import ntplib

from utils.logger import get_logger

logger = get_logger("utils.time_sync")

_ntp_offset: float = 0.0


def get_ntp_offset() -> float:
    """获取与 NTP 服务器的时间偏差（秒），失败返回 0.0。"""
    global _ntp_offset
    try:
        client = ntplib.NTPClient()
        response = client.request("ntp.aliyun.com", version=3, timeout=5)
        _ntp_offset = response.offset
        logger.info("NTP 时间偏差: {:.4f}s", _ntp_offset)
    except Exception as e:
        logger.warning("NTP 同步失败: {}, 使用本地时间", e)
        _ntp_offset = 0.0
    return _ntp_offset


def get_accurate_time() -> float:
    """返回校准后的当前时间戳。"""
    return time.time() + _ntp_offset


def wait_until(target_ts: float) -> None:
    """阻塞等待到目标时间戳，精确到毫秒级。"""
    while True:
        diff = target_ts - get_accurate_time()
        if diff <= 0:
            break
        if diff > 1:
            time.sleep(diff - 0.5)
        elif diff > 0.01:
            time.sleep(0.005)
