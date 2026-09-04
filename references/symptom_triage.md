# 现象排查卡（Symptom Triage Cards · rule 80）

> 版本：v1.0（v3.14.0 新增）| 用途：用户报**现象类问题**时的标准取证流程 | 定位：rule 80 的落地模板，与 `six_layer_check.py render-silent-fail`、rule 81 长排错检查点、rule 41 验证归因联动
> 来源：2026-09-05 家俊 Electron 实战复盘硬伤3——"看不到"问题三轮往返（第一轮靠猜、第二轮才加日志、第三轮才做对照实验）。本卡把每一轮"该要的数据"固化下来，第一轮就要全。

---

## 使用规则（先读这段）

1. **取证优先（硬规则）**：现象类问题禁止未取证就改代码。第一动作三件——① 加最小诊断日志；② 按对应卡片向用户要**标准数据**（一次要全，不要挤牙膏）；③ 设计对照实验（一次只改一个变量）。
2. **先跑脚本再人工**：涉及渲染端窗口/样式/IPC 的现象，先跑 `python scripts/six_layer_check.py render-silent-fail <项目根>`——五项静默失效检查 30 秒内能排除/命中一半以上的高频根因（rule 79）。
3. **判定树走完再动手**：按卡片"判定顺序"从上往下，每步有结论才走下一步；证伪的假设立即落盘（rule 81：`[排错检查点] 已排除: X | 当前嫌疑: Y | 下一步: Z`）。
4. **修复后必须回归**：按卡末"回归验证"确认现象消失且无新现象（rule 43 两层制：dry-run 不够，关键路径真实执行）。

---

## 卡 1 · 窗口不可见 / "什么都看不到"

**标准五项数据（向用户或诊断日志要，一次全要）**：

| # | 数据 | 取法 |
|---|---|---|
| 1 | `visible` | `win.isVisible()` |
| 2 | `pos` | `win.getPosition()`（是否在屏幕外/多显示器坐标） |
| 3 | `size` | `win.getSize()`（是否 0×0） |
| 4 | `z-order` | `win.isAlwaysOnTop()` + 是否被全屏/其他置顶窗遮挡 |
| 5 | `render-mounted` | 渲染进程入口是否真的执行（`webContents` did-finish-load / 渲染端首行日志） |

**判定顺序**：
1. 主进程日志里 `did-finish-load` 触发了吗？→ 没触发：加载失败（路径 404 / vite 未打包该入口 → 先跑 `render-silent-fail` 查 vite input）
2. `visible=false` / 尺寸 0 / 坐标在屏外？→ 修窗口创建参数
3. `render-mounted` 日志出现了吗？→ 没出现：preload 未加载（`contextIsolation`/`sandbox` 配置）或 JS 报错（看 devtools console / `webContents` 的 `console-message`）
4. 都正常但用户看不见？→ **对照实验**：隐藏/关闭其他窗口排除 z-order 与遮挡；透明窗检查 `transparent:true` + 页面背景是否透明
5. 仍无结论 → 按卡末"证据升级"找用户要截图 + 操作系统/版本信息，进入 rule 64 纠错先检索（先查 knowledge 库再上网）

**高频根因（按命中率排序）**：① html 入口未进 vite input（404 白屏）② preload 路径错/未加载 → 渲染端 JS 崩 ③ 透明窗背景全透明 → "看似没渲染" ④ z-order/遮挡 ⑤ 多显示器坐标漂移

**回归验证**：正常启动一次 + 异常路径各一次（如断网/无数据），窗口均出现且渲染日志齐全。

---

## 卡 2 · 样式全丢 / "界面全没样式但 build 绿"

**判定顺序**：
1. **先跑 `render-silent-fail`**——tailwind content 漏扫是本现象第一根因（实测三轮才定位的案例：typecheck 绿/build 绿/不崩，UI 全无样式）
2. devtools 查 `<html>`/`<body>` 上有没有 tailwind 生成的工具类样式表：查 `<style>` 或 link 的 css 是否含 `.bg-`/`.flex` 规则 → 完全没有 = content/postcss 链断
3. CSS 文件产出了吗？→ 看 `dist/` 里 css 体积；0KB 或几 KB = content 没扫到任何类
4. postcss 配置链：`postcss.config.*` 是否存在、tailwind 插件是否注册、css 入口 `@tailwind`/`@import "tailwindcss"` 是否被引
5. 样式表在但个别元素没样式 → 查该组件是否在 content glob 覆盖的目录内（v4 则查 `@source`）

**高频根因**：① tailwind `content[]` 漏了新目录（第一根因，已脚本化）② postcss 未接 tailwind 插件 ③ css 入口文件没被页面引 ④ tailwind v3/v4 混用（v4 无 config，靠 `@source`）⑤ class 名动态拼接被 purge 掉（`bg-${color}` 类写法）

**回归验证**：改 content/配置后**重跑 build**（tailwind 是构建期扫描），确认产物 css 体积恢复 + 页面样式正常。

---

## 卡 3 · IPC 无响应 / "调用没返回"

**判定顺序**：
1. **先跑 `render-silent-fail`**——通道集合比对直接列出"preload 调了但主进程没注册"的通道（invoke 静默无响应 = Promise 永远 pending，不报错，极易误判为"卡了"）
2. 通道名逐字符核对：preload `invoke('win:info')` vs 主进程 `handle('win:info')`——拼写/大小写/冒号连字符差异（建议通道名常量化，两侧 import 同一常量文件）
3. handler 注册时机：`ipcMain.handle` 是否在 `app.whenReady()` 之前执行、是否有条件分支跳过注册（僵尸能力检查，rule 72）
4. preload 暴露检查：`contextBridge.exposeInMainWorld` 的 key 与渲染端 `window.<key>` 引用是否一致；`contextIsolation:true` 下渲染端无法直接 require
5. 返回值序列化：handler 返回了不可结构化克隆的对象（类实例/函数/循环引用）→ Promise reject 或静默丢——把返回值收敛为纯 JSON
6. 仍无结论 → 加两侧日志（invoke 前后 + handle 进出）定位断点在哪一侧

**高频根因**：① 通道拼写不一致（第一根因）② 主进程 handler 忘注册/注册被跳过 ③ preload 未重新编译（改了 preload 但没重启/没 rebuild）④ 返回值不可结构化克隆 ⑤ `sandbox:true` 导致 preload 受限

**回归验证**：每条涉及的通道真调一次（渲染端实际触发，非直调 handler），断言返回值正确（rule 43 真实交互路径）。

---

## 证据升级（三张卡走完仍无结论时）

按顺序收齐再升级，不要挤牙膏式提问：
1. 现象截图/录屏 + 期望行为描述
2. 版本信息（OS / Electron / Node / 关键依赖版本）
3. 复现步骤（最小复现路径）+ 是否必现
4. 上轮排错检查点记录（lessons.md 里的 `[排错检查点]` 行——已排除了什么，别重复排查）

然后走 rule 64 纠错先检索：`read_knowledge(现象关键词)` → WebSearch 同类问题 → 才考虑再动代码。

## 决策卡（可粘贴到任意开发窗口）

```
用户报了一个现象（不是报错）。按取证优先执行：
① 先跑 python scripts/six_layer_check.py render-silent-fail <项目根>（涉及窗口/样式/IPC 时）
② 按对应现象排查卡，一次向用户要全标准数据 + 加最小诊断日志
③ 设计对照实验（一次只改一个变量），每个被证伪的假设立即落盘 lessons.md
④ 超过 3 个假设证伪仍无结论 → 写断点小结再继续（rule 81）
⑤ 定位根因前禁止改代码；修复后按卡末回归验证 + 交付说明"根因是 X，改了 Y"
```
