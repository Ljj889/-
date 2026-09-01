---
type: guide
date: 2026-09-01
tags: 框架合规,软约束失效,合规检查,six_layer_check,并发会话,galagame
confidence: high
version: 1
owner: six-layer-orchestrator
last_verified: 2026-09-01
review_cycle: 90d
status: active
source: galagame 项目实战（2026-08/09）
---

# G-006 框架使用合规检查（软约束失效的解毒剂）

## 症状（galagame 实战，2026-09-01 复盘）

用户在开发 galagame 时**明确调用了 six-layer-orchestrator skill**，但项目落地后检查发现：

- 无 `lessons.md` / `cost_log.md` / `progress.json` / `interfaces.md`
- 无 `knowledge/` 或 `知识经验/` 目录（Phase 0.5 未初始化）
- 无 `PHASE_*_DONE` 标记
- 无 SDD 四件套（spec/plan/tasks/constitution）
- **结果**：框架级 `knowledge/_index.md` 无任何该项目的资产产出，read_knowledge 读侧自然也无从召回

**注意区分**：项目里其实有 `.workbuddy/memory/` 日志、交接文档、战略图、Wave 编号——说明"部分纪律生效了"（rule 73 过程文档、收尾文档），但**骨架流程被整体跳过**。这不是"完全没用框架"，是"降级使用"。

## 根因（机制层面，不是态度问题）

1. **SKILL.md 本质是提示词纪律（软约束）**：只是一篇加载进上下文的文档，没有任何程序在"开工时检查 Phase 0.5 做了没"、"收尾时检查蒸馏了没"。
2. **声称的引擎化大部分是纸面的**（2026-09-01 实测）：`validate_output.py` / `read_knowledge.py` 存在，但 SKILL.md 中描述的 `cli.py design --finalize`（设计锁定 Gate）、`route_error()`、lifecycle 状态机硬拦截、调用前 enforcement **均未落地**——能强制的只有 2 个工具脚本。
3. **并发会话放大漂移**：galagame 项目 MEMORY.md 自述"本仓易有并发会话写入"。多窗口并发时，后来的会话上下文未必加载了 skill，或加载了但被长任务稀释。深度模式授权"全量自主执行"后，AI 优先保效率，仪式性步骤最容易被砍。

## 护栏（可执行）

1. **合规检查脚本（本指南的配套工具）**：`scripts/six_layer_check.py <项目目录>` — 一键检查框架痕迹（git 基线 / Phase 0.5 知识资产 / SDD 四件套 / lessons / cost_log / progress / PHASE 标记 / 收尾文档），缺失项列清单并提示该补哪个 Phase。
   - 开工前跑：`--mode init`（应具备 Phase 0/0.5 痕迹）
   - 收尾跑：`--mode deliver`（应具备 Phase 5-7 痕迹）
   - 程序化使用：`--strict`（有缺失 exit 1）+ `--json`
2. **调度器纪律**：加载 skill 后第一步 = 跑合规检查；缺失项按清单补 Phase，**禁止跳过初始化直接开写**。
3. **并发会话场景**：多窗口并发前先 `git status` + git bundle 打保险；新会话启动先跑合规检查确认当前处于哪个阶段（复用断点恢复 SOP）。
4. **收尾强制蒸馏**：Phase 5 合并交付后必须走 Phase 7 六步（含人工 Gate），蒸馏产物进 `knowledge/` 四桶并追 `_index.md`（rule 54 索引 Gate）。
5. **red flag 联动**：交付报告中若项目无任何框架痕迹（lessons/cost_log/progress 全缺）却声称"按六层框架开发"→ 视为未验证，FAIL。

## 与既有规则的关系

- 本指南是 rule 64（硬约束优先——能硬约束的绝不靠自觉）的落地案例：把"靠自觉记得走框架"引擎化为可检查脚本。
- 与 G-001（环境坑）并列：G-001 治"环境问题"，本指南治"流程合规问题"。
- 引擎化优先级参照 rule 64 第 269 行：数据类校验（本检查清单）→ 脚本/CLI；状态流转 → 状态机硬拦截；纯判断类 → 保留提示词+多 Agent 制衡。
