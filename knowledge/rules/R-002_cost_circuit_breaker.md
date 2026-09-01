---
title: 成本熔断做成一等公民
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [成本控制, 熔断, token预算, runtime]
source: 调研全档案索引 §五-2（方向 A/E/F 深度轮询共识，$5,847/58min 事故）
supersedes: null
superseded_by: null
---
# R-002 成本熔断做成一等公民

**当** 编排循环需要持续调用 LLM 时 → **易犯** 只做事后记账（跑完才看账单）、把成本控制寄托在"告警"上 → **护栏**：

1. **调用前 budget gate**：每次调用前检查累计消耗，超预算即熔断（circuit breaker）——**告警是异步的，拦不住调用**
2. **递归深度上限**：嵌套/递归任务设最大深度，超限即停
3. **wall-clock 预算**：整体任务设时间预算，超时即停

**与框架衔接**：方法论层已嵌入 SKILL.md rule 57（成本硬刹车：maxIterations/tokenBudget/repetitionThreshold）——本资产是 rule 57 的完整 rationale 与来源；引擎层 = 编排 B 实现为**调用前 enforcement**（拦截函数），非仅 cost_log 事后记账。
**来源**：dev.to 成本复盘（-60%/-73%）、OpenClaw 循环事故（$5,847/58min 未独立核实，教训方向可信）。
