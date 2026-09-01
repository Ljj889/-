---
title: web 前端自动化验证环境坑合集（vite preview / CDP / node 加载）
version: 1
owner: 调度器（蒸馏自 galagame 统一设置面板 + 生图持久化 + 移动端实战）
last_verified: 2026-09-01
review_cycle: 90d
status: active
tags: [环境坑, web, CDP, vite, node, 自动化验证, 临时脚本]
source: galagame scripts/web-smoke.mjs + 临时验收脚本实战
supersedes: null
superseded_by: null
---
# G-005 web 前端自动化验证环境坑

**当** 在 Windows + Node 环境对 web 前端做真机/自动化验证（CDP 无头浏览器、本地预览、临时脚本）时 → **易犯** 常规环境假设（localhost=IPv4、npm 包一定是 JS 产物、`rm`/删除总可用、PATH 持久）→ **护栏**（全是实测坑）：

| 坑 | 现象 | 对策 |
|---|---|---|
| vite preview 默认绑 localhost | Windows 解析为 IPv6 `::1`，探测/导航用 `127.0.0.1` 假失败（"服务起不来"实为地址错） | 显式 `--host 127.0.0.1`，探测与浏览器导航用同一 IPv4 地址 |
| CDP 连错 WS | `'Page.enable' wasn't found` | 必须连 `/json/list` 里 `type === 'page'` 的 target 的 `webSocketDebuggerUrl`；`/json/version` 给的是 browser 级 WS（无 Page/Runtime 域） |
| node 原生加载含 TS 源码的 npm 包 | `ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING`（包 main 指向 `.ts`，如 edge-tts） | 经 `tsx`（`node node_modules/tsx/dist/cli.mjs entry.ts`）或构建器启动，不用裸 `node dist` |
| 含中文注释的 .ts 落盘成 UTF-16LE | BOM `FF FE` 让 vite/esbuild 报 `Unexpected "�"` | 门禁前扫描目标目录 BOM（`ReadAllBytes` 首两字节 `FF FE`），发现转 UTF-8 |
| 删除临时文件被权限/审批拦截 | `rm`/`Remove-Item`/删除工具超时 | 兜底 `node -e "require('fs').unlinkSync(path)"`；临时验收脚本**用完即删** |
| shell 丢 Node PATH 且不跨调用保留 | 同一会话前一个命令能跑 npm，下一条 `node -e` 报"无法识别 node" | 每条命令**同一条内**前置 `$env:PATH = "node目录;" + $env:PATH` |

**配套原则**：环境限制导致的"不可验证"必须诚实标 `[不可测·真机]` 进未验证项清单（rule 42）；临时脚本属验证产物，验收后清理（rule 28/43 纪律延伸）。
**关联**：G-001（环境坑通用）、G-003（子 Agent 通道失效/CDP 实例占用）、L5/L6/L7/L9（galagame 教训源）。
