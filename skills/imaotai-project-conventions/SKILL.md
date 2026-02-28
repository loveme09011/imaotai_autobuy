---
name: imaotai-project-conventions
description: i茅台抢购项目开发规范。开发 imaotai_autobuy 项目中任何模块时必须激活此 skill，包含：项目结构、Python 规范、配置管理、日志、错误处理、测试要求、Git 管理规范。
---

# imaotai-project-conventions

## 语言 & 环境

- Python 3.10+
- 虚拟环境：`venv`（目录名 `.venv`，加入 `.gitignore`）
- 依赖管理：`requirements.txt`（固定版本号）

## 项目结构

```
imaotai_autobuy/
├── config/
│   ├── config.yaml          # 实际配置（gitignore）
│   └── config.example.yaml  # 配置模板（提交到 git）
├── core/                    # 核心业务逻辑
├── api/                     # i茅台 API 封装层
├── scheduler/               # 定时任务
├── utils/                   # 工具函数
├── tests/                   # 测试文件（与模块一一对应）
├── logs/                    # 运行日志（gitignore）
├── main.py
├── requirements.txt
└── .gitignore
```

## 配置管理

- 账号、Token、device_id 等敏感信息只存 `config/config.yaml`，绝不硬编码
- `config/config.yaml` 加入 `.gitignore`，只提交 `config.example.yaml`
- 使用 `PyYAML` 读取配置

## 日志规范

- 统一使用 `loguru`
- 格式：`{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}`
- 日志文件：`logs/app_{time:YYYY-MM-DD}.log`，按天轮转，保留 7 天
- 控制台同步输出，级别 INFO 及以上

## 错误处理

- 网络请求失败：最多重试 3 次，指数退避（1s → 2s → 4s）
- 关键操作失败（申购、登录）必须记录 ERROR 日志
- 不允许裸 except:，必须捕获具体异常类型

## 测试规范

- 使用 `pytest`
- 每个独立模块完成后必须编写对应测试，测试文件放 `tests/` 下，命名 `test_<module>.py`
- 测试通过后方可提交 git，禁止带测试失败的代码提交
- 网络请求测试使用 mock，不发真实请求

## Git 管理规范

### Commit 格式（Conventional Commits）

```
<type>(<scope>): <subject>
```

type：
- `feat` — 新功能
- `fix` — Bug 修复
- `test` — 测试
- `refactor` — 重构
- `docs` — 文档
- `chore` — 构建/依赖/配置

示例：
```
feat(api): 添加申购接口封装
fix(scheduler): 修复9点定时偏差问题
test(api): 添加登录接口单元测试
chore: 初始化项目结构和 .gitignore
```

### 提交时机（强制）

1. 每个独立模块功能完成 → 运行测试 → 全部通过 → 立即 commit
2. 一个 commit 只做一件事，禁止多模块混合提交
3. 提交前检查：不含调试代码（print、hardcode token）、不含敏感信息

### 分支策略

- `main` — 稳定可运行，只接受 merge，禁止 force push
- `dev` — 日常开发
- `feature/xxx` — 独立功能分支，完成后合并 dev

### 版本 Tag

- 里程碑节点打 tag，格式：`v0.1.0`（语义化版本）
- 示例里程碑：基础申购跑通 v0.1.0、多账号支持 v0.2.0、耐力值自动维护 v0.3.0

### .gitignore 必须包含

```
.venv/
config/config.yaml
logs/
__pycache__/
*.pyc
.env
```
