---
title: 无测试框架项目的真实行为冒烟手法（esbuild bundle + node require）
version: 1
owner: 家俊（番茄钟·桌面便签实战）→ 调度器（蒸馏）
last_verified: 2026-09-02
review_cycle: 90d
status: active
tags: [验证, 冒烟, esbuild, 无测试框架, 真实模块, rule73]
source: 番茄钟桌面便签（Sticky Note）实战 2026-09-01，Wave2 8/8 + Wave3 26/26 实测
supersedes: null
superseded_by: null
---

# ts-smoke-harness · 无测试框架项目的真实行为冒烟

## 适用判定

**当** 项目没有测试框架（无 jest / vitest / mocha），却要满足 rule 73④「必须导入真实模块的单测，禁止复刻逻辑」时。

**易犯** 两种偷懒：
1. 用 `npm run typecheck` 冒充验证 —— 类型绿只证明"结构对"，不证明"行为对"；
2. 手写一份**复刻被测逻辑**的假脚本 —— 测了个寂寞，源码改了它照样绿。

**护栏**：用 esbuild 把**真实源码**打成 CJS，再由 node 脚本 require 该产物，断言**行为**。

## 三步手法

```bash
# 1) 把真实 TS 源码 bundle 成 CJS（原生模块必须 external，否则加载失败）
npx esbuild src/main/<module>.ts --bundle --platform=node --format=cjs \
  --external:better-sqlite3 --outfile=zz-<module>-bundle.cjs

# 2) node 脚本 require 真实产物，注入临时依赖后断言行为
#    （临时目录 + 用完即删，绝不落进仓库）

# 3) 跑完删除临时脚本与产物
```

关键参数：
- `--bundle`：把依赖链一起打进来，避免 node 直接 import `.ts` 失败
- `--external:<原生模块>`：`better-sqlite3` / `sharp` 这类带 `.node` 的必须外部化，否则 bundle 阶段报错
- 被测类若依赖宿主对象（如 `Database`），可只传一个满足契约的最小对象，或把宿主也 bundle 一份

## 断言写什么（这是价值所在）

按 rule 43「不跑不会发现」原则，优先断言这些 typecheck 永远抓不到的东西：
- **语义正确性**：不是"函数存在"，而是"取消勾选只回滚 auto 日志、manual 日志保留"这类业务语义
- **幂等性**：反复操作后最终状态是否唯一（如"勾→取消→再勾只留 1 条记录"）
- **边界与脏数据**：绕过正常校验直接写脏数据，验证防御分支真的工作
- **不可达分支**：跑完若发现某分支始终走不到，要显式标注（见 R-008 第二条），别假装覆盖到了

## 实测战果

番茄钟桌面便签项目（2026-09-01）：
- Wave2 迁移冒烟 8/8：建表幂等、`ON DELETE SET NULL` 生效、`CHECK` 约束拒绝非法值、位置值可 JSON 解析
- Wave3 仓储冒烟 26/26：层级非法被拒、跨天隔离、软删后子项解绑且日志不丢、顺延不删原项、排序生效
- **并抓到两个 typecheck 永远发现不了的问题**：① 环校验分支在层级约束下不可达；② 自动日志的幂等回滚语义

## 纪律

- 临时脚本命名统一 `zz-*`，**跑完必删**，避免污染工作区（与 G-005「临时脚本清理」同源）
- 冒烟结果以 `N PASS / M FAIL` 计数进 cost_log，作为 rule 42「验证证据」的可审计材料
- 环境限制导致的不可测项，诚实标 `[不可测·已降级]` 进未验证项清单（rule 42 / rule 50）

## 关联

- rule 42 验证证据纪律 · rule 43 验证两层制 · rule 50 契约验收前置核实 · rule 73④ 真实模块单测
- G-005 web 自动化环境坑（临时脚本清理同源）
- R-008 类型门禁假绿（typecheck 不能充当验证的另一面）
