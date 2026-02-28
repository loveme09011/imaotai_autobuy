# v0.2.1 优化计划

## 背景

v0.2.0 完成了多商品支持、申购重试、结果持久化、Token 过期检测和健康检查。105 项测试全部通过。以下是下一步可优化的方向。

## Todo-List

- [ ] **多通知渠道**：除 Server酱外，支持飞书 Webhook、Bark、Telegram Bot 等推送渠道
- [ ] **Token 自动续期**：检测到 Token 过期后，自动调用登录流程刷新（需缓存验证码或使用免验证码方式）
- [ ] **申购结果统计面板**：基于 `data/results/` 日志生成每日/每周中签统计报表
- [ ] **Docker 部署支持**：提供 Dockerfile 和 docker-compose.yaml，方便一键部署到服务器
- [ ] **配置热更新**：运行中检测 config.yaml 变更自动重载，无需重启程序
- [ ] **异步化改造**：将 ThreadPoolExecutor 改为 asyncio + aiohttp，降低资源消耗
