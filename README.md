# imaotai_autobuy

> 🍾 i茅台自动申购工具 — v0.1.1

## 功能概览

- **API 客户端**：完整封装 i茅台 API，含签名、重试、日志
- **申购核心**：多账号并发申购，自动选择最优门店
- **定时调度**：精确到秒的申购任务（09:00），随机时间旅行任务
- **结果通知**：通过 Server酱推送申购结果
- **登录工具**：手机号+验证码获取 Token，写入账号配置

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 登录获取 Token（交互式）
python tools/login.py

# 启动申购调度
python main.py
```

## 配置文件

`config/accounts.yaml` — 账号列表（phone、token、userId）  
`config/settings.yaml` — 全局设置（商品ID、Server酱 SendKey）

## 项目结构

```
api/          # API 客户端封装
core/         # 申购核心逻辑、账号管理、通知
scheduler/    # 定时任务（APScheduler）
tools/        # 登录工具
utils/        # 签名、时间同步、日志、通知器
tests/        # 78 个单元测试（pytest）
docs/         # 设计文档
```

## 版本历史

- **v0.1.1** (2026-02-28)：完成所有基础模块，文档整理，78 项测试全部通过
- **v0.1.0** (2026-02-28)：基础功能完成：API客户端、申购核心逻辑、定时调度、结果通知
