---
name: imaotai-api
description: i茅台 APP HTTP API 集成规范。开发 imaotai_autobuy 项目的 api/ 模块时激活，包含：已知端点、请求签名、Header 规范、Token 管理、风控规避策略。详细 API 文档见 references/。
---

# imaotai-api

## 概述

i茅台 APP 使用 HTTPS REST API，请求需要携带签名 Header。所有 API 封装放在 `api/` 目录下。

## 基础信息

- Base URL：`https://app.moutai519.com.cn`
- 内容类型：`application/json`
- 字符集：UTF-8

## 必须携带的 Header

```
MT-Device-ID: <设备唯一ID，首次随机生成后固定>
MT-APP-Version: <当前app版本号>
Authorization: <登录后获取的token>
User-Agent: iOS/16.0 iMoutai/<version>
mt-k: <请求签名>
mt-r: <请求签名辅助字段>
```

详细签名算法见 [references/signing.md](references/signing.md)

## 核心 API 端点

详见 [references/endpoints.md](references/endpoints.md)，主要包括：
- 登录/验证码
- 申购（每日9点）
- 旅行（维护耐力值）
- 商品/门店查询

## Token 管理

- 登录态 Token 存储在 `config/config.yaml`，字段 `users[].token`
- Token 有效期较长，但需处理过期刷新
- 多账号支持：config 中 users 为列表

## 风控规避原则

- 请求间隔不得为 0，关键请求前随机 sleep 0.5~2s
- device_id 每个账号固定，不随机变化
- User-Agent 与真实 APP 保持一致
- 申购请求控制在 09:00:00 ± 1s 内发出，不提前大量重试

## 错误处理

- HTTP 非 200：记录日志，按重试规范处理
- 业务错误码（code != 2000）：解析 message，记录日志，不重试申购接口
- 签名错误（401/403）：检查签名算法版本

## 参考文档

- [references/endpoints.md](references/endpoints.md) — 完整端点列表与参数
- [references/signing.md](references/signing.md) — 签名算法详解
