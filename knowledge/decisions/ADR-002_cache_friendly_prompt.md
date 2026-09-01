---
title: ADR-002 缓存友好提示组装
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [提示词缓存, 性能, prompt组装, 架构决策]
source: 调研全档案索引 §五-8（方向 E 深度轮询共识，ProjectDiscovery 7%→84%）
supersedes: null
superseded_by: null
---
# ADR-002 缓存友好提示组装

## 背景
提示词缓存（prompt cache）命中率是长对话成本的第一杠杆：ProjectDiscovery 通过静态/动态分离把 cache hit 从 7% 提升到 84%（dev.to 复盘，方向 E）。

## 决策
1. **静态前缀 / 动态尾部分离**：稳定内容（系统提示、框架规则、角色定义、知识资产全文）放**前缀**（缓存友好，命中即免 token）；每次变化的内容（任务上下文、用户输入、状态）放**尾部**（不进缓存区）
2. **cache breakpoint 意识**：缓存按前缀命中计费，组装时把"必变内容"推迟到 prompt 最末尾
3. **cache hit rate 当核心指标**：成本监控不只看 token 总量，跟踪缓存命中率

## 与现有框架衔接
方法论层 = rule 40 上下文管理（<2,000 行裁剪）+ rule 56 引擎/智能分离（引擎层组装 prompt）——本 ADR 是引擎层 prompt 组装的**成本优化决策**。
## 落地
编排 B 阶段 2（平台提示组装模块），阶段 1 不阻塞。
## 来源
深度轮询_成本与模型（ProjectDiscovery / dev.to -62%/-60%/-73% 复盘，数字依赖流量结构，引用须以自家计量为准）。
