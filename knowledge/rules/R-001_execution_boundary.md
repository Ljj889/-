---
title: 默认拒绝的执行边界
version: 1
owner: 家俊（调研产出）→ 调度器（蒸馏）
last_verified: 2026-08-11
review_cycle: 90d
status: active
tags: [执行边界, 安全, 沙箱, runtime]
source: 调研全档案索引 §五-1（方向 A/F 深度轮询共识）
supersedes: null
superseded_by: null
---
# R-001 默认拒绝的执行边界

**当** 子 Agent / 平台执行器需要访问外部资源时 → **易犯** 默认放行（网络出口全开、文件读写无限制、无执行时限）→ **护栏**：

1. **无网出口**：执行器默认无网络访问；需要网络的任务显式声明并白名单放行
2. **文件仅限临时目录**：子进程只能读写分配的临时目录/工作区，越界路径直接拒绝
3. **每次执行硬超时**：所有子进程执行必须带 wall-clock 超时（超时即杀，不等待）

**落地状态**：方法论层 = 本资产（注入 constitution 常驻）；引擎层 = 编排 B M_EXEC 沙箱执行器（subprocess timeout + 白名单目录）。
**来源**：OpenClaw 默认拒绝边界 / 个人生产踩坑复盘。
