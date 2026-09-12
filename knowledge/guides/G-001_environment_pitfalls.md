---
title: 实战环境坑合集（Windows 沙箱 + Electron 桌宠）
version: 4
owner: 家俊（番茄钟实战）→ 调度器（蒸馏）
last_verified: 2026-09-12
review_cycle: 90d
status: active
tags: [环境坑, Windows, 沙箱, Electron, 排障, Python, 控制台编码]
source: 六层开发框架实战经验_2026-08-12.md §E（番茄钟 06 复盘 P1-4 实测）
supersedes: null
superseded_by: null
---
# G-001 实战环境坑合集

**当** 在 Windows 沙箱 / Electron 桌面环境做自动化验证时 → **易犯** 用常规环境假设（GUI 能启动、rm 能删、set 生效、路径能转义）→ **护栏**（都是实测过的坑，遇到即查）：

| 坑 | 现象 | 对策 |
|---|---|---|
| Electron GUI 无法沙箱启动 | `require('electron')` 返回字符串（非模块） | **验收必须用户桌面跑**，沙箱内只验逻辑层 |
| `rm -rf` 被 safe-delete 拦截 | 清空 out/ 失败 | 用全新输出目录验证构建（`POMODORO_OUT_DIR=out-xxx`） |
| Git Bash `set` 不生效 | 设 CDP 端口失败 | 必须 `export` |
| 注入页面表达式裸变量 | ReferenceError | `${JSON.stringify()}` 插值，不拼裸变量 |
| PowerShell 中文+空格路径 | 转义失败 | 用 Bash 绝对路径；**更省事：命令默认在工作区根目录执行，不 `cd` 中文路径**（galagame L3） |
| **pip/uv 安装与沙箱 safe-delete 冲突（v1.1 · 多宠语音实战 P1）** | 沙箱内装依赖失败 | **依赖安装用非沙箱模式执行**（安装类操作用户确认后放行） |
| **git 中文 pathspec 静默返回空（v1.2 · 便签实战）** | `git status/diff -- "中文目录/src"` 返回 **0 行**，被误读为"该目录干净"——注意这不是转义失败，是**静默成功** | 先 `Set-Location` 进目标目录再用**相对** pathspec；**任何 0 结果的 git 查询都要换路径复跑一次**再下结论 |
| **PowerShell `Set-Location` 与 .NET 当前目录不同步（v1.2）** | `[System.IO.File]::ReadAllBytes('相对路径')` 报"未能找到路径的一部分"，路径缺了子目录层 | .NET API 与 `node -e` 一律用 **FullName 拼绝对路径**；npm / git 等子进程不受影响（它们跟随 PowerShell PWD） |
| **`node -e '...'` 内部双引号被吞（v1.2）** | node 收到 `require(fs)` → `ReferenceError: Cannot access 'fs' before initialization` | 改用 PowerShell 原生 API 实现，或写成临时 `.cjs` 文件再执行 |
| **Python 缺失 / py 启动器指向失效安装（v1.3 · 便答回合2）** | `python` 不在 PATH；`py` 启动器注册的 `Python312\python.exe` 实际不存在（卸载残留）→ "Unable to create process" | 先 `Test-Path <注册路径>` 探测；缺失用平台 `install_binary(python)` 装受管运行时，用其返回的**绝对路径**执行框架脚本 |
| **GBK 控制台 UnicodeEncodeError（v1.3）** | Python 脚本 print `✓/✗` 等非 GBK 字符崩（`'gbk' codec can't encode`）——**检查逻辑已跑完，只是输出崩**，别误判为脚本故障 | 执行前设 `$env:PYTHONUTF8='1'`（或 `PYTHONIOENCODING=utf-8`） |
| **删除类命令审批超时（v1.3）** | `Remove-Item` 触发用户审批，用户不在场 → 超时取消（连试两次都超时） | 不阻塞交付：临时文件留在 tmp/（未跟踪、无害），交付说明里记"待清理清单"，下轮顺手清；避免把可延后的清理卡成流程阻塞 |

| **`node`/`npm` 不在 PATH（PATH 指向已删除的版本目录）（v1.4 · 2026-09-12 番茄宠物V2）** | `where.exe node` 为空、`npm` 全不可用 → 依赖脚本的 Gate（引擎三件套 / `six_layer_check`）**必然失败**，容易被误判为"框架坏了" | 先跑**运行时探针**：`Get-ChildItem ~\.workbuddy\binaries\node\versions`（或 `Test-Path`）找**实际存在**的目录，再用**绝对路径**执行（`& "$nd\node.exe"` / `& "$nd\npm.cmd"`），并在命令内 `$env:PATH="$nd;$env:PATH"`；探针失败 → 标未验证，**禁止静默跳过** |
| **本机只有 WSL bash、无 Git Bash（v1.4）** | 仓库 `sync_to_platforms.sh` 用 `C:/Users/...` 形态路径：Git Bash 可解析，**WSL 不能**（需 `/mnt/c/...`）→ 脚本"能启动但路径全错" | 平台同步改用等价的 **`sync_to_platforms.ps1`**（已入库）；跨平台脚本一律**运行时探测路径**，不硬编码盘符形态 |
| **读+写/删混在一条命令 → 审批超时被取消（v1.4）** | 一条命令里同时有 `Get-Content` 与 `Set-Content`/`Remove-Item` → 审批弹窗超时、命令白跑（实测两次） | 把"只读取证"与"写/删"拆成**独立命令**；清理类操作可延后（见 v1.3「删除类命令审批超时」行） |

**配套原则**：环境限制导致的"不可验证"必须诚实标 `[不可测·真机]` 进未验证项清单（rule 42），不粉饰。
**关联**：R-001 执行边界（沙箱默认拒绝是环境坑的根源）、rule 43 验证两层制（环境限制下 dry-run 更不可信）。
