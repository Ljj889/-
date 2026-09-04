---
title: 构建配置漏扫 = 静默失效（三层全绿 ≠ 真的没坏）
version: 1
owner: 调度器（蒸馏自 2026-09-05 家俊 Electron 便签实战硬伤2）
last_verified: 2026-09-05
review_cycle: 90d
status: active
tags: [构建配置, 静默失效, tailwind, vite, tsconfig, IPC, 渲染端]
source: 家俊 Electron 便签实战——Tailwind content 漏扫致 typecheck 绿/build 绿/不崩但 UI 全没样式，三轮才定位；同类隐患藏在五处配置
supersedes: null
superseded_by: null
---
# R-010 构建配置漏扫 = 静默失效

**当** Electron/前端项目新增渲染端窗口、页面、overlay 类模块，或验收"看起来不对"的现象时 → **易犯** 把"**typecheck 绿 + build 绿 + 运行不崩**"当成"没坏"，但这三层绿的检查根本覆盖不到**配置层的漏扫**——五处高危静默失效点：① tsconfig include 漏新目录（typecheck 对该目录假绿，R-008）② vite rollupOptions.input 漏新 html 入口（窗口 404 白屏）③ tailwind content 漏源码目录（样式静默丢失，实测三轮才定位）④ preload 的 window.* 无 d.ts 声明（类型假绿，改 API 名不报错）⑤ preload 调用的 IPC 通道主进程未注册（invoke 静默无响应，Promise 永远 pending）→ **护栏**：

1. **新增渲染端窗口/页面模块的合并前置 Gate**：跑 `python scripts/six_layer_check.py render-silent-fail <项目根> --strict`（rule 79 引擎化）——五项配置覆盖/一致性检查，FAIL 即禁止合并；配置不存在自动 SKIP 防误报。
2. **typecheck/build 绿不作为"没坏"的证据**：验收渲染端模块时，验证证据必须含"产物真的生效"（样式表体积/窗口可见/通道返回值），green CI 只证明"编译通过"（rule 43 False Green 认知）。
3. **通道与目录名用常量单一来源**：IPC 通道名两侧 import 同一常量文件；目录清单写进 interfaces.md 契约，新模块落盘时契约同步——防拼写漂移静默断链。
4. **现象类问题先跑本检查再人工排查**：窗口不可见/样式全丢/IPC 无响应三张排查卡见 references/symptom_triage.md（rule 80 取证优先）。

**关联**：rule 79（渲染端静默失效检查 Gate）、rule 80（取证优先与现象排查卡）、R-008（类型门禁假绿，tsconfig include 专项）、rule 43（False Green 认知）、rule 81（长排错检查点——三轮定位的教训闭环）。
