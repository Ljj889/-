---
title: experience-distiller 经验蒸馏能力
version: 1
owner: 调度器（蒸馏自 v3.9.3 Phase 7 设计）
last_verified: 2026-08-12
review_cycle: 90d
status: active
tags: [经验蒸馏, 知识沉淀, Phase7, framework-skill]
source: 六层框架_经验蒸馏与文档读取回路_设计_2026-08-12.md §7
supersedes: null
superseded_by: null
---
# framework-skill: experience-distiller

**按名可调用的蒸馏能力**（框架 Phase 7 专用，不独立成 skill 文件——核心最小化，per-call tax 教训）。

## 何时按名调用
调度器进入 Phase 7 项目级 full 蒸馏时，派"经验蒸馏员"子 Agent（模板见 references/task_templates.md「蒸馏 sub-Agent 模板」）。

## 调用契约
```
触发: 项目收尾（Phase 5 合并后）或用户说"蒸馏经验/沉淀资产"
输入: lessons.md / cost_log.md / feedback_accumulated.md / 审查 FAIL 记录
流程: ① read_knowledge 查重（rule 59）→ ② 六步蒸馏（Gather→Rewrite→Classify→Gate→Land→Feed，rule 58）
输出: candidates 清单 → 人工 Gate（采纳/修改/驳回）→ 落盘四桶 + 追 _index.md（rule 54 Gate）
```

## 与独立 skill 的关系
- 独立 meta-skill 会分裂判断权（"要不要蒸馏"的判断必须唯一，归属 Phase 7）；
- 本资产 = 能力登记，被 read_knowledge("蒸馏") 可检索、可按名调用，符合"核心保持最小、能力按需装配"（OpenClaw per-call tax / Harvey Tool Bundle 教训）。
