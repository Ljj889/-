---
title: 循环护栏默认开
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [循环护栏, 死循环, 无进展检测, runtime]
source: 调研全档案索引 §五-3（方向 A/B/D/E 深度轮询共识）
supersedes: null
superseded_by: null
---
# R-003 循环护栏默认开

**当** 编排流程存在 LOOP / 反思 / 重试 / 递归循环时 → **易犯** `while True` 无界循环（Agent 概率系统转圈空转，状态只增不减）→ **护栏**（默认开启，不靠自觉）：

1. **max_iterations / max_hops**：所有循环任务设迭代上限（默认 3，复杂可调），超限硬停并抛异常/报告
2. **无进展检测**：连续 N 轮输出与上轮高度重复（repetitionThreshold）→ 判定空转，停止升级给人
3. **目标校验**：每轮循环前校验"本轮是否仍朝目标前进"，偏离即停

**与框架衔接**：方法论层已嵌入 SKILL.md rule 57（重复熔断 repetitionThreshold）；引擎层 = 编排 B 循环执行器默认带护栏。
**来源**：LangGraph/CrewAI 循环事故、MAST 论文、OpenClaw 空转案例。
