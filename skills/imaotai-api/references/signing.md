# i茅台请求签名算法

> 警告：签名算法随 APP 版本更新可能变化，需持续跟进社区逆向结果

## 签名 Header

- `mt-k`：主签名字段
- `mt-r`：辅助验证字段

## 已知签名逻辑（参考 oddfar/campus-imaotai）

签名基于以下字段生成：
- 请求路径（path）
- 时间戳（timestamp，13位）
- device_id
- user_id（登录后）

算法伪代码：
```python
import hashlib

def generate_sign(path: str, timestamp: str, device_id: str, user_id: str = "") -> str:
    raw = f"{path}{timestamp}{device_id}{user_id}"
    return hashlib.md5(raw.encode()).hexdigest()
```

## 注意事项

1. 时间戳必须与服务器时间一致（误差 < 30s），建议同步 NTP
2. 算法可能已更新，以实际抓包验证为准
3. 参考最新社区逆向：https://github.com/oddfar/campus-imaotai/issues
