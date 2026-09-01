---
title: 结构化响应信封 + fail-loud
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [结构化输出, fail-loud, 错误处理, runtime]
source: 调研全档案索引 §五-4（方向 B/D 深度轮询共识，CrewAI #6262）
supersedes: null
superseded_by: null
---
# R-004 结构化响应信封 + fail-loud

**当** 子 Agent / 工具调用需要返回结果时 → **易犯** 自由格式输出、静默吞错（`except: pass` = fail-silent，错误消失无痕）→ **护栏**：

1. **结构化响应信封**：所有输出统一 `{status, data, error, trace_id}` 四字段，编排层校验信封
2. **fail-loud**：异常必须上抛带 trace，**绝不静默吞**——`except Exception: pass` 是红线
3. **trace_id 贯穿**：错误可追溯（哪个调用/哪个模块/哪个 token 段）

**与框架衔接**：方法论层 = rule 37（子 Agent 输出异常协议：空结果≠没执行，先磁盘核验）；引擎层 = 编排 B M_CKPT 已实现 fail-loud（close/写失败上抛，删 except:pass，commit 21efdb3）。
**来源**：CrewAI #6262（错误被吞=fail-silent）、GitHub Engineering 生产 Agent 失败模式。
