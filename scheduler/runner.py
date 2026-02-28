import random
import time

import schedule

from scheduler.jobs import reservation_job, travel_job
from utils.logger import get_logger

logger = get_logger("scheduler.runner")


def _random_travel_time() -> str:
    """生成 10:00-20:00 之间的随机时间字符串（HH:MM:SS）。"""
    hour = random.randint(10, 19)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def _schedule_travel(config_path: str) -> None:
    """执行旅行任务，然后为明天重新调度一个随机时间。"""
    travel_job(config_path)
    # 清除旧的旅行任务，重新调度明天的随机时间
    schedule.clear("travel")
    travel_time = _random_travel_time()
    schedule.every().day.at(travel_time).do(
        _schedule_travel, config_path=config_path
    ).tag("travel")
    logger.info("明日旅行任务已调度: {}", travel_time)


def setup(config_path: str, item_code: str, city_code: str) -> None:
    """注册所有定时任务。"""
    # 每天 09:00:00 执行申购
    schedule.every().day.at("09:00:00").do(
        reservation_job,
        config_path=config_path,
        item_code=item_code,
        city_code=city_code,
    ).tag("reservation")
    logger.info("申购任务已注册: 每天 09:00:00")

    # 每天随机时间执行旅行
    travel_time = _random_travel_time()
    schedule.every().day.at(travel_time).do(
        _schedule_travel, config_path=config_path
    ).tag("travel")
    logger.info("旅行任务已注册: 今日 {}", travel_time)


def start(config_path: str, item_code: str, city_code: str) -> None:
    """启动调度主循环。"""
    setup(config_path, item_code, city_code)
    logger.info("调度器已启动，等待任务触发...")
    while True:
        schedule.run_pending()
        time.sleep(1)
