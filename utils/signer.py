import hashlib
import time


def generate_sign(path: str, timestamp: str, device_id: str, user_id: str = "") -> str:
    raw = f"{path}{timestamp}{device_id}{user_id}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_timestamp() -> str:
    return str(int(time.time() * 1000))
