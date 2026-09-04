# knowledge/ 经验资产库 · 索引（canonical entry）

> **read_knowledge 唯一入口**（rule 59）：先读本文件，禁止盲搜。检索 = 按问题类型/tags 匹配下表，不按项目名（NASA LLIS 覆辙）。
> 版本：v3.9.3 首建 · 复核点：每个新项目启动（Phase 0.5 顺带 review 召回列表）
> 维护纪律：资产落盘后 30 秒内追一行；被吸收进 SKILL.md rule 的资产可从库移除（空库=吸收彻底）。

| 路径 | 类型 | 状态 | tags | 摘要 | last_verified |
|---|---|---|---|---|---|
| rules/R-001_execution_boundary.md | rule | active | 执行边界,安全,沙箱,runtime | 默认拒绝：无网出口/文件限临时目录/硬超时 | 2026-08-11 |
| rules/R-002_cost_circuit_breaker.md | rule | active | 成本控制,熔断,token预算,runtime | 成本熔断一等公民：调用前 budget gate，告警异步无效（rule 57 的来源） | 2026-08-11 |
| rules/R-003_loop_guardrails.md | rule | active | 循环护栏,死循环,runtime | 循环护栏默认开：max_iterations/无进展检测/目标校验 | 2026-08-11 |
| rules/R-004_structured_envelope_fail_loud.md | rule | active | 结构化输出,fail-loud,runtime | 响应信封 {status,data,error,trace_id} + 绝不静默吞 | 2026-08-11 |
| rules/R-005_checkpointer_transactional.md | rule | active | checkpoint,持久化,事务,schema版本 | Checkpointer 事务化+复合键+schema 版本化（M_CKPT 已落地） | 2026-08-11 |
| rules/R-006_dangerous_op_policy_gate.md | rule | active | 危险操作,策略门,审计,安全 | 危险操作模型外硬策略门+不可变审计（rule 36 引擎化） | 2026-08-11 |
| decisions/ADR-001_shared_state_layer.md | decision | active | 共享状态,黑板,交接schema,架构决策 | 显式共享状态层+类型化交接 schema（阶段 2 落地） | 2026-08-11 |
| decisions/ADR-002_cache_friendly_prompt.md | decision | active | 提示词缓存,性能,prompt组装 | 静态前缀/动态尾部分离，cache hit 当核心指标（7%→84%） | 2026-08-11 |
| framework-skills/experience-distiller.md | framework-skill | active | 经验蒸馏,知识沉淀,Phase7 | 按名可调用的蒸馏能力（Phase 7 专用，模板见 task_templates） | 2026-08-12 |
| guides/G-001_environment_pitfalls.md | guide | active | 环境坑,Windows,沙箱,Electron,git,pathspec | 实战环境坑合集 v1.2（Electron GUI 沙箱/rm 拦截/Git Bash set/裸变量/PowerShell 路径/pip冲突 + **git 中文 pathspec 静默返回空**/**Set-Location 与 .NET 当前目录不同步**/**node -e 双引号被吞**） | 2026-09-02 |
| guides/G-002_effect_acceptance_guide.md | guide | active | 效果类,主观验收,MOS,语音 | 效果类验收指南（MOS/CMOS/MUSHRA + 维度拆解 + 盲测，rule 61 操作手册） | 2026-08-13 |
| guides/G-003_agent_channel_fallback.md | guide | active | 编排,子Agent,通道故障,出口,CDP,实例占用 | 子 Agent 通道失效→rule 46 直执行出口；**变体1 任务书空投递 / 变体2 返回工具轨迹无正文**的鉴别与处置；CDP 前探测实例占用与 DB 备份（2026-08-16 番茄钟 + 2026-09-02 便签实战） | 2026-09-02 |
| rules/R-007_zombie_capability.md | rule | active | 僵尸能力,调用点,验收,死代码,第二真相源 | 无调用点的能力=僵尸（galagame 关系系统 scanRelationshipState 零调用/备份双实现/idb 单例未 init）：新能力必须有宿主接线点；验收前 grep 调用方，无调用点禁止标已验证 | 2026-09-01 |
| guides/G-004_monorepo_build_order.md | guide | active | monorepo,workspace,构建顺序,dist,typecheck | 改 workspace 底层包先 build 再 typecheck 消费方——消费方解析 dist 而非 src，TS2353 假错识别法（galagame 统一设置面板实战） | 2026-09-01 |
| guides/G-005_web_automation_env.md | guide | active | 环境坑,web,CDP,vite,自动化验证,临时脚本 | web 前端自动化验证坑：vite preview 127.0.0.1/CDP page target/node 加载 TS 源码包须 tsx/BOM 扫描/临时脚本清理 fs.unlinkSync/PATH 每命令前置（galagame 实战） | 2026-09-01 |
| decisions/ADR-003_settings_entry_consolidation.md | decision | active | 设置面板,信息架构,功能与设置配套,UI | 设置集中单一入口分 tab（⚙️+模型/语音/数据）；新功能默认自带设置项 UI；共用配置 UI 注明（galagame 统一设置面板实战） | 2026-09-01 |
| guides/G-006_framework_compliance.md | guide | active | 框架合规,软约束失效,合规检查,six_layer_check,并发会话 | 软约束失效解毒剂：调用 skill 但骨架被跳过的根因 + 合规检查脚本用法（galagame 教训，配套 scripts/six_layer_check.py，rule 64 引擎化落地案例） | 2026-09-01 |
| rules/R-008_type_gate_false_green.md | rule | active | 类型检查,假绿,tsconfig,include,不可达分支,验证 | 新增目录必须进 tsconfig include，否则 typecheck 是假绿（实测既有 overlay 漏检多年）；不可达分支须标[不可测·已降级]+造脏数据定向验证，不假装已验证 | 2026-09-02 |
| rules/R-009_module_removability.md | rule | active | 解耦,可移除性,编译期依赖,回调注入,红线自洽 | 可移除性优先于整洁性：宿主相关代码内联宿主文件 + 回调注入替代反向 import；验收=grep 外部引用须收敛到单一装配文件 | 2026-09-02 |
| framework-skills/ts-smoke-harness.md | framework-skill | active | 验证,冒烟,esbuild,无测试框架,真实模块,rule73 | 无测试框架时满足 rule 73④"导入真实模块"的手法：esbuild bundle 真实源码→node require 断言行为（实测抓到 typecheck 发现不了的语义与幂等缺陷） | 2026-09-02 |
| rules/R-010_build_config_silent_failure.md | rule | active | 构建配置,静默失效,tailwind,vite,tsconfig,IPC,渲染端 | 构建配置漏扫=静默失效：三层全绿≠没坏——五处高危点（tsconfig include/vite input/tailwind content/preload d.ts/IPC 通道一致性）已引擎化为 six_layer_check render-silent-fail（rule 79，2026-09-05 便签实战硬伤2） | 2026-09-05 |

## 四桶说明
- `rules/`：红线，注入 constitution 常驻
- `decisions/`：ADR，注入 plan 作 rationale
- `framework-skills/`：可调用能力（当前：experience-distiller 经验蒸馏 · ts-smoke-harness 无测试框架冒烟）
- `guides/`：可选操作手册（当前：G-001 环境坑 v1.2 · G-002 效果类验收 · G-003 子Agent通道 v1.1 · G-004 monorepo构建 · G-005 web自动化 · G-006 框架合规检查）
- `rules/`：红线，注入 constitution 常驻（当前 R-001~R-010；R-007 僵尸能力 / R-008 类型门禁假绿 / R-009 可移除性 / R-010 构建配置静默失效，后三者属"看起来已验证其实没有"家族且都可 grep 硬校验）
