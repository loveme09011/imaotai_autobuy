from concurrent.futures import ThreadPoolExecutor

from api.client import ApiClient
from core.account import load_accounts
from utils.logger import get_logger

logger = get_logger("core.reservation")


def get_best_shop(client: ApiClient, city_code: str) -> str:
    """获取该城市出货量最大的门店 ID（取第一个）。"""
    shops = client.get_shops(city_code)
    if not shops:
        raise ValueError(f"城市 {city_code} 无可用门店")
    shop_id = shops[0].get("shopId", "")
    logger.info("选中门店: {}", shop_id)
    return shop_id


def run_reservation(account: dict, item_code: str, city_code: str) -> dict:
    """对单个账号执行申购流程。"""
    mobile = account.get("mobile", "unknown")
    try:
        client = ApiClient(account)
        shop_id = get_best_shop(client, city_code)
        result = client.reservation(item_id=item_code, shop_id=shop_id)
        code = result.get("code", -1)
        if code == 2000:
            logger.info("[{}] 申购成功", mobile)
            return {"mobile": mobile, "success": True, "message": "申购成功"}
        msg = result.get("message", "未知错误")
        logger.warning("[{}] 申购失败: {}", mobile, msg)
        return {"mobile": mobile, "success": False, "message": msg}
    except Exception as e:
        logger.error("[{}] 申购异常: {}", mobile, e)
        return {"mobile": mobile, "success": False, "message": str(e)}


def run_all(
    config_path: str, item_code: str, city_code: str
) -> list[dict]:
    """加载所有账号，并发执行申购，返回结果列表。"""
    accounts = load_accounts(config_path)
    if not accounts:
        logger.warning("无有效账号，跳过申购")
        return []

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(run_reservation, acc, item_code, city_code)
            for acc in accounts
        ]
        for future in futures:
            results.append(future.result())

    success_count = sum(1 for r in results if r["success"])
    logger.info("申购完成: {}/{} 成功", success_count, len(results))
    return results
