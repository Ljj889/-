---
title: monorepo/workspace 构建顺序：改底层包先 build 再 typecheck 消费方
version: 1
owner: 调度器（蒸馏自 galagame 统一设置面板实战）
last_verified: 2026-09-01
review_cycle: 90d
status: active
tags: [monorepo, workspace, 构建顺序, dist, typecheck]
source: galagame apps/web typecheck 报 TS2353（OpenAiProviderConfig.extraHeaders 不存在）
supersedes: null
superseded_by: null
---
# G-004 monorepo/workspace 构建顺序

**当** 改动 workspace 底层包（如 `@companion/core`）时 → **易犯** 改完 src 直接对消费方（web/bff）跑 typecheck → 报 **TS2353 假错误**（`xxx 不存在于类型 X`），因为消费方经 `package.json` 的 `main`/`types` 解析到底层包的 **`dist/index.d.ts` 构建产物**，而不是 src → **护栏**：

1. **改底层包后先 `npm run build -w 底层包` 重建 dist，再 typecheck 消费方**——顺序固定：`build 底层 → typecheck:all`。
2. 把这条写进派发清单/门禁清单的前置项（防"类型红"误判为代码错，也防"类型绿"其实是消费方仍在读旧 dist 的假绿）。
3. 判断技巧：报错文件名指向 `dist/*.d.ts` 或错误信息是"新加的字段/方法不存在"，先怀疑**解析到旧产物**，不是代码错了（用 `read package.json` 确认 `types` 指向）。

**关联**：rule 41（验证失败先归因：脚本/构建顺序错 vs 代码错）、rule 43（验证两层制）。
