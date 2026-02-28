# 自动开发循环（dev-loop）

## 概述

项目使用 OpenClaw 定时任务 + Claude Code 实现自动化开发循环，无需人工干预即可持续推进功能迭代。

## 触发机制

每 **5 分钟**，定时任务自动检查 `status.json`，根据状态决定是否启动新一轮开发。

## status.json 状态文件

> **注意：** `status.json` 为本地文件，不上传 git 仓库（已加入 .gitignore）

```json
{
  "version": "v0.2.0",
  "in_progress": false,
  "pending_work": false,
  "last_run": "2026-02-28T17:30:00+08:00",
  "last_result": "success",
  "note": "本次执行摘要"
}
```

| 字段 | 说明 |
|------|------|
| `version` | 当前版本号 |
| `in_progress` | 是否正在执行开发循环（防并发） |
| `pending_work` | 是否有待开发内容 |
| `last_run` | 上次执行时间（ISO格式） |
| `last_result` | `success` / `failed` |
| `note` | 本次执行摘要 |

## 执行流程

```
定时任务触发
    │
    ├── 读取 status.json
    │
    ├── pending_work == false → 输出「项目稳定」，退出
    │
    └── pending_work == true 或 in_progress == true
            │
            ├── Step 1：读设计文档，找未完成 Todo
            ├── Step 2：启动 Claude Code（--print 非交互模式）开发
            ├── Step 3：子 agent 运行 pytest 测试
            │
            ├── 测试通过 ✅
            │       ├── 更新版本号（patch +1）
            │       ├── 更新 README.md
            │       ├── 更新 Todo [ ] → [x]
            │       ├── 创建 docs/features/v<新版本>/improvements.md
            │       ├── 更新 status.json（pending_work 视优化文档而定）
            │       ├── 合并 dev → main，打 tag，push
            │       └── 通知用户（版本号、更新内容、下次计划）
            │
            └── 测试失败 ❌
                    ├── 不更新版本号
                    ├── 创建 docs/features/v<版本>_issues/problems.md
                    ├── 更新 status.json（pending_work=true, result=failed）
                    ├── 只提交到 feature 分支，不合并
                    └── 通知用户失败原因
```

## 版本管理规则

- **测试通过** → patch 版本 +1，合并 dev → main，打 tag
- **测试失败** → 版本号不变，只提交到 feature 分支
- **稳定版本**（连续2次 success）→ 合并到 main

## 相关文件

| 文件 | 说明 |
|------|------|
| `~/.openclaw/skills/imaotai-dev-loop/SKILL.md` | 完整开发循环 skill |
| `~/.openclaw/skills/claude-code-usage/SKILL.md` | Claude Code 使用规范 |
| `docs/features/` | 各版本设计文档和 Todo |
| `status.json` | 本地状态文件（不入库） |

## 历史版本

| 版本 | 状态 | 主要内容 |
|------|------|---------|
| v0.1.0 | ✅ | 项目骨架、API客户端、申购逻辑、定时调度、结果通知 |
| v0.1.1 | ✅ | 登录工具（手机号+验证码获取token）、文档整理 |
| v0.2.0 | ✅ | 多商品支持、申购重试、结果持久化、Token过期检测、健康检查 |
