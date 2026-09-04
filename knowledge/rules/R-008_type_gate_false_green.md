---
title: 类型门禁假绿 + 不可达分支诚实标注
version: 1
owner: 家俊（番茄钟·桌面便签实战）→ 调度器（蒸馏）
last_verified: 2026-09-02
review_cycle: 90d
status: active
tags: [类型检查, 假绿, tsconfig, include, 验证, 不可达分支]
source: 番茄钟桌面便签实战 2026-09-01（tsconfig.web.json 漏 include；环校验分支不可达）
supersedes: null
superseded_by: null
---
# R-008 类型门禁假绿 + 不可达分支诚实标注

**当** 新增源码目录（尤其渲染端新窗口 / 新子应用 / 新子包）→ **易犯** 只顾写业务代码，忘了把它加进 `tsconfig*.json` 的 `include`，于是 `npm run typecheck` 全绿，但**该目录一行代码都没被检查过** → **护栏**：

1. **新增目录当天先改 `include`**，并把它列为该 Wave 的验收项——不能等 typecheck 报错，它永远不会报错（本次实测：新建的 `renderer/sticky-window`、`renderer/goal-window` 若不补 include，`typecheck:web` 照样全绿）。
2. **审计法（可脚本化）**：`grep <新目录名> tsconfig*.json` 必须非空；收尾时对每个新建目录跑一次。
3. **存量补查**：接手老项目时先核对 `include` 是否漏了既有目录。本次实测发现 `src/renderer/overlay/` **已漏在外面多年无人察觉**——这类历史窟窿往往不止一处。

**同源第二条 · 不可达分支必须诚实标注**：验收时若发现某分支在正常路径下根本走不到（本次：环校验在层级严格单向约束 `step→today→short→long` 下结构上不可能触发，构造的"成环"请求会先被层级校验拦截），**不要沉默放行，也不要假装已验证**——做法是：

1. 代码注释标 `【已知不可达 · 防御性冗余】`，写明保留理由（抵御脏数据 / 为未来放宽约束留口）；
2. 补一个"绕过正常校验直接造脏数据"的定向验证，证明该防御逻辑**本身**正确；
3. 验收口径按 `[不可测·已降级]` 标注（rule 50），**不声称"已验证"**。

**为什么单独立红线**：这两类问题都属于"看起来验证过了、其实没有"，是 AI 生成代码最擅长伪造的 False Green 家族，且**都可以 grep/执行硬校验**——符合 rule 64「能硬约束的绝不靠自觉」。

**关联**：rule 43（验证两层制 / False Green 认知）、rule 42（验证证据纪律）、rule 50（契约验收前置核实）、R-007（僵尸能力，同为"看起来落地了其实没有"家族）、framework-skills/ts-smoke-harness（用真实行为验证补位）。
