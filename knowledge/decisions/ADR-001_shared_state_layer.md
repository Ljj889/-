---
title: ADR-001 显式共享状态层 + 类型化交接 schema
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [共享状态, 黑板, 交接schema, 架构决策]
source: 调研全档案索引 §五-6（方向 C/D 深度轮询共识，Harvey/GrowBrain/Cloudflare v2）
supersedes: null
superseded_by: null
---
# ADR-001 显式共享状态层 + 类型化交接 schema

## 背景
多 Agent 协作时，Agent 间**不靠自然语言重建上下文**（口头交接 = 信息损耗 + 上下文膨胀）。GrowBrain/Cloudflare v2/Harvey 均证实：共享状态层是生产级多 Agent 系统的架构前提。

## 决策
1. 引入**显式共享状态层（SharedBlackboard）**：状态变更走统一通道（写入/订阅），不通过对话传递
2. **类型化交接 schema**：Agent 间交接用结构化 schema（字段/类型/必填），校验后传递，不做自由文本
3. 消息总线/黑板 = **有序不可变事件流**；compaction 只整段摘要替换，不局部改写（防状态漂移）

## 与现有框架衔接
方法论层 = rule 18 接口契约层（interfaces.md 统一对接格式）+ rule 16 调度器中转（子 Agent 不直接对话）——本 ADR 是这两条的**引擎层扩展**（把"文档契约"变成"运行时共享状态"）。
## 落地
编排 B 阶段 2（树形编排 + SharedBlackboard），预留设计不阻塞阶段 1。
## 来源
深度轮询_架构演进复盘（Harvey 树形编排 / GrowBrain / Cloudflare v2）+ 深度轮询_多Agent协作（GitHub Engineering）。
