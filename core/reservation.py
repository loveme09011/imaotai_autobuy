import time
from concurrent.futures import ThreadPoolExecutor

from api.client import ApiClient
from core.account import load_accounts
from utils.logger import get_logger

logger = get_logger("core.reservation")

RESERVATION_MAX_RETRIES = 3
RESERVATION_RETRY_INTERVAL = 1


def get_best_shop(client: ApiClient, city_code: str) -> str:
    """获取该城市出货量最大的门店 ID（取第一个）。"""
    shops = client.get_shops(city_code)
    if not shops:
        raise ValueError(f"城市 {city_code} 无可用门店")
    shop_id = shops[0].get("shopId", "")
    logger.info("选中门店: {}", shop_id)
    return shop_id


def run_reservation(account: dict, item_code: str, city_code: str) -> dict:
    """对单个账号、单个商品执行申购流程（含重试）。"""
    mobile = account.get("mobile", "unknown")
    try:
        client = ApiClient(account)
        shop_id = get_best_shop(client, city_code)

        last_msg = "未知错误"
        for attempt in range(RESERVATION_MAX_RETRIES):
            result = client.reservation(item_id=item_code, shop_id=shop_id)
            code = result.get("code", -1)
            if code == 2000:
                logger.info("[{}] 商品{} 申购成功", mobile, item_code)
                return {"mobile": mobile, "item_code": item_code, "success": True, "message": "申购成功"}
            last_msg = result.get("message", "未知错误")
            # Token 过期不重试，直接返回并标记
            if code in (401, 4001, 4003):
                logger.error("[{}] Token 已过期或无效，请重新登录", mobile)
                return {"mobile": mobile, "item_code": item_code, "success": False,
                        "message": last_msg, "token_expired": True}
            if attempt < RESERVATION_MAX_RETRIES - 1:
                logger.warning("[{}] 商品{} 申购失败(第{}次): {}, 重试中", mobile, item_code, attempt + 1, last_msg)
                time.sleep(RESERVATION_RETRY_INTERVAL)

        logger.warning("[{}] 商品{} 申购最终失败: {}", mobile, item_code, last_msg)
        return {"mobile": mobile, "item_code": item_code, "success": False, "message": last_msg}
    except Exception as e:
        logger.error("[{}] 商品{} 申购异常: {}", mobile, item_code, e)
        return {"mobile": mobile, "item_code": item_code, "success": False, "message": str(e)}


def run_all(
    config_path: str, item_codes: list[str], city_code: str
) -> list[dict]:
    """加载所有账号，为每个账号申购所有商品，并发执行，返回结果列表。"""
    accounts = load_accounts(config_path)
    if not accounts:
        logger.warning("无有效账号，跳过申购")
        return []

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for acc in accounts:
            acc_items = acc.get("items", item_codes)
            for item_code in acc_items:
                futures.append(executor.submit(run_reservation, acc, item_code, city_code))
        for future in futures:
            results.append(future.result())

    success_count = sum(1 for r in results if r["success"])
    logger.info("申购完成: {}/{} 成功", success_count, len(results))
    return results
