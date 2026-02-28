import time

import requests

from utils.logger import get_logger
from utils.signer import generate_sign, get_timestamp

logger = get_logger("api.client")

BASE_URL = "https://app.moutai519.com.cn"
APP_VERSION = "1.7.6"
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]


class ApiClient:
    def __init__(self, config: dict) -> None:
        self.token: str = config.get("token", "")
        self.device_id: str = config.get("device_id", "")
        self.user_id: str = config.get("user_id", "")
        self.session = requests.Session()

    def _get_headers(self, path: str, timestamp: str) -> dict:
        return {
            "MT-Device-ID": self.device_id,
            "MT-APP-Version": APP_VERSION,
            "Authorization": self.token,
            "mt-k": generate_sign(path, timestamp, self.device_id, self.user_id),
            "mt-r": generate_sign(path, timestamp, self.device_id),
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        url = f"{BASE_URL}{path}"
        timestamp = get_timestamp()
        headers = self._get_headers(path, timestamp)

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                logger.info("请求 {} {}, 第{}次尝试", method.upper(), path, attempt + 1)
                resp = self.session.request(method, url, json=data, headers=headers, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF[attempt]
                    logger.warning("请求失败: {}, {}s后重试", exc, wait)
                    time.sleep(wait)

        logger.error("请求 {} {} 最终失败: {}", method.upper(), path, last_exc)
        raise last_exc  # type: ignore[misc]

    def send_code(self, mobile: str) -> dict:
        return self._request("POST", "/sendCode", data={"mobile": mobile})

    def login(self, mobile: str, code: str, device_id: str) -> dict:
        resp = self._request(
            "POST",
            "/login",
            data={"mobile": mobile, "code": code, "deviceId": device_id},
        )
        return {"token": resp.get("token", ""), "user_id": resp.get("userId", "")}

    def get_items(self) -> list:
        resp = self._request("GET", "/items")
        return resp.get("data", [])

    def get_shops(self, city_code: str) -> list:
        resp = self._request("GET", f"/shops?cityCode={city_code}")
        return resp.get("data", [])

    def reservation(self, item_id: str, shop_id: str) -> dict:
        return self._request(
            "POST",
            "/reservation",
            data={"itemId": item_id, "shopId": shop_id},
        )

    def travel(self) -> dict:
        return self._request("POST", "/travel")
