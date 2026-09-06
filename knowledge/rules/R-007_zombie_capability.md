---
title: 无调用点的能力 = 僵尸（定义 ≠ 落地）
version: 2
owner: 调度器（蒸馏自 galagame 关系系统双重僵尸实战 + 2026-09-06 便签反馈回合2）
last_verified: 2026-09-06
review_cycle: 90d
status: active
tags: [僵尸能力, 调用点, 验收, 死代码, 第二真相源, preload参数焊死]
source: galagame 关系系统 WS4.2（scanRelationshipState 全仓零调用）+ 备份双实现 + idb 未托管单例
supersedes: null
superseded_by: null
---
# R-007 无调用点的能力 = 僵尸

**当** 模块/能力交付或验收时 → **易犯** 把"接口完整、类型检查全绿、单测通过"当成"已落地"，但该能力**没有任何宿主调用它**（galagame 实测三个案例：① 关系系统 `scanRelationshipState` 全仓从未被调用，公式错了半年没人发现；② 备份存在 `backup.ts`/`idb.ts` 两套实现，被改的是无调用方的死代码；③ 模块级 `idb` 单例从未 `init()`，写入被重试逻辑静默吞掉，UI 却提示成功）→ **护栏**：

1. **新能力必须有显式宿主接线点**（启动即扫 / 定时器 / UI 入口 / 明确的消费方），并把"调用点存在"写进该模块的验收标准（衔接 rule 50 契约验收前置核实）。
2. **验收前 `grep 能力名` 查调用方**：无调用点 = 僵尸，**禁止标「已验证」**（rule 39 三态），回退补接线后再验。
3. **修复/审查疑似缺陷时先 grep 调用方定位真实链路**（rule 64 纠错先检索）：无调用方的"缺陷"是死代码而非缺陷——galagame 曾仅凭死代码判"备份漏 store（P1）"，实际 UI 走的是另一条早已正确的链路（误判复盘）。
4. **preload/胶水层参数焊死变体（v2 · 2026-09-06 便签反馈回合2）**：main handler 支持某参数但 preload 签名不传 → 该参数是死参数，渲染端能力**事实上不存在**（实测：`STICKY_DRAG_START` handler 带 `key` 默认 'sticky'，preload `dragStart()` 焊死不传 → 目标管理窗"拖不动"；用户报的"拖不动"根因有二，此其一，另一是渲染层事件链根本没写——两者都属僵尸家族）。护栏：契约核对时**逐参数对齐三处**——preload 签名 ↔ main handler 签名 ↔ index.d.ts 声明；"handler 支持、preload 不传"按僵尸处理，与 ①② 同一验收 grep。

**关联**：rule 50（契约验收前置核实）、rule 64（纠错先检索）、rule 42（验证证据纪律）、L2（同能力双实现=重复真相源）、rule 73②共享交互信号（同一交互能力 ≥2 宿主必须抽共享 hook，防两份实现漂移）。
