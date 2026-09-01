---
title: Checkpointer 事务化 + schema 版本化
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [checkpoint, 持久化, 事务, schema版本, runtime]
source: 调研全档案索引 §五-5（方向 B/D 深度轮询共识，LangGraph #8590/#8478）
supersedes: null
superseded_by: null
---
# R-005 Checkpointer 事务化 + schema 版本化

**当** Checkpointer 需要落盘状态时 → **易犯** 写一半被杀留半截状态（#8590）、跨会话串读（#8478）、旧 schema 读新数据崩溃 → **护栏**：

1. **事务化**：状态写入包原子事务（BEGIN/COMMIT/ROLLBACK），失败回滚不留半截
2. **复合键隔离**：thread_id + run_id（+ns）分区，WHERE 校验 owner，防跨会话串读
3. **schema 版本化**：checkpoint 表带 schema 版本号 + 迁移函数，**resume 前校验版本并迁移**，版本不符拒绝恢复（fail-loud 而非崩溃乱读）

**与框架衔接**：方法论层 = rule 39（Checkpoint 三态）+ 断点恢复 SOP；引擎层 = 编排 B M_CKPT 已落地事务化 + 复合键 + fail-loud（commit 21efdb3），schema 版本化待 Wave 2+。
**来源**：LangGraph #8590（写一半被杀）/ #8478（跨会话串读）/ CrewAI #6262。
