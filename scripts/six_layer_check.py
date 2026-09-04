"""six_layer_check.py — 六层框架合规检查（rule 64 硬约束优先 · v3.9.12 新增）

来源：galagame 实战教训（2026-09-01）——调用 skill 但骨架流程被跳过
（无 Phase 0.5 / 无 Phase 7 蒸馏 / 无 lessons/cost_log），知识库零产出。
根因：SKILL.md 是提示词纪律（软约束），多轮/并发会话中会被稀释。
本脚本把"靠自觉记得走框架"变成"跑一下就知道缺什么"。

用法：
    python six_layer_check.py [项目目录] [--mode init|deliver|auto] [--json] [--strict]
    - 默认目录 = 当前工作目录
    - --mode init    ：开工前检查（应具备 Phase 0/0.5 痕迹）
    - --mode deliver ：收尾检查（应具备 Phase 5-7 痕迹）
    - --mode auto    ：全部检查（默认）
    - --json         ：输出 JSON（供程序消费）
    - --strict       ：有缺失即 exit 1（默认 exit 0=检查完成）

    python six_layer_check.py render-silent-fail <项目目录> [--json] [--strict]
    - 渲染端静默失效五项检查（rule 79 · v3.14.0 新增，2026-09-05 家俊 Electron 实战硬伤2）：
      tsconfig include / vite input / tailwind content / preload d.ts / IPC 通道一致性
      - 配置文件存在才检查，不存在标 SKIP（防误报）
      - typecheck 绿 + build 绿 + 不崩 ≠ 真的没坏：这五处任何一个漏扫都是静默失效

退出码：0=检查完成（非 strict） / 1=有缺失（strict） / 2=目录不存在
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# 检查项定义：(key, 名称, 目标路径/glob, 阶段, 说明)
# 阶段: init=开工前应备, deliver=收尾应备, both=全程
CHECKS = [
    ("git_repo",       "git 仓库（Phase 0 版本控制前置）",  ".git",              "init",
     "rule 11：无 git 禁止高风险开发"),
    ("git_baseline",   "git 已有提交基线",                  "git_commits",       "init",
     "rule 11：有仓库但无基线提交 = 未初始化"),
    ("knowledge_dir",  "知识资产目录（Phase 0.5）",          ("knowledge", "知识经验"), "init",
     "rule 11.1-11.4：防文件腐烂，缺则 read_knowledge 无入口"),
    ("knowledge_index","知识索引 _index.md",                ("knowledge/_index.md", "知识经验/_index.md"), "init",
     "rule 11.1：唯一入口路由表，缺失 = Phase 0.5 未初始化"),
    ("spec",           "spec.md（SDD 四件套）",             ("spec.md",),        "init",
     "rule 7：生产级/多模块项目应规格先行（可选）"),
    ("plan",           "plan.md",                           ("plan.md",),        "init", "rule 7"),
    ("tasks",          "tasks.md",                          ("tasks.md",),       "init", "rule 7"),
    ("constitution",   "constitution.md",                   ("constitution.md",), "init", "rule 7"),
    ("lessons",        "lessons.md（教训文件）",             ("lessons.md",),     "both",
     "rule 32/40：失败教训写入，重开先读"),
    ("cost_log",       "cost_log.md（成本账本）",            ("cost_log.md",),    "both",
     "rule 38/53：定长记录可 grep，异常类型列必填"),
    ("progress",       "progress.json（断点+三态）",         ("progress.json",),  "both",
     "rule 39：预期产物清单 + lifecycle 字段"),
    ("interfaces",     "interfaces.md（接口契约）",          ("interfaces.md",),  "both",
     "rule 18：并行对接唯一保障（单模块项目可无）"),
    ("phase_marks",    "PHASE_*_DONE/FAILED 标记",          "phase_marks",       "both",
     "rule 56：解析失败写 PHASE_X_FAILED，完成写 DONE"),
    ("memory_logs",    ".workbuddy/memory/ 过程日志",       ".workbuddy/memory", "both",
     "rule 66：过程文档先行，跨会话进 YYYY-MM-DD.md"),
    ("project_memory", ".workbuddy/memory/MEMORY.md",       ".workbuddy/memory/MEMORY.md", "deliver",
     "rule 66：长期项目约定沉淀"),
    ("handover_doc",   "交接文档.md（收尾强制）",           ("交接文档.md",),    "deliver",
     "全局收尾规则：项目根目录交接文档"),
    ("strategy_map",   "战略图.svg/html（收尾强制）",       ("战略图.svg", "战略图.html", "战略图.md"), "deliver",
     "全局收尾规则：进度/范围可视化"),
]


def _glob_exists(root: Path, patterns) -> bool:
    """任意一个路径/glob 存在即 True"""
    if isinstance(patterns, str):
        patterns = (patterns,)
    for p in patterns:
        # 目录存在性
        if (root / p).exists():
            return True
        # 带通配符则 glob
        if any(c in p for c in "*?"):
            if list(root.glob(p)):
                return True
    return False


def _git_has_commits(root: Path) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def _phase_marks_exist(root: Path) -> bool:
    return bool(list(root.glob("PHASE_*_DONE")) or list(root.glob("PHASE_*_FAILED")))


def check(project_dir: str, mode: str = "auto") -> dict:
    root = Path(project_dir)
    if not root.is_dir():
        return {"ok": False, "error": f"目录不存在: {project_dir}", "items": []}

    items = []
    missing = []
    for key, name, target, phase, note in CHECKS:
        if mode != "auto" and phase not in ("both", mode):
            continue
        if key == "git_baseline":
            exists = _git_has_commits(root)
        elif key == "phase_marks":
            exists = _phase_marks_exist(root)
        else:
            exists = _glob_exists(root, target)
        items.append({
            "key": key, "name": name, "phase": phase,
            "exists": exists, "note": note,
        })
        if not exists:
            missing.append(f"  ✗ [{phase}] {name}  <-  {note}")
    return {"ok": True, "root": str(root), "mode": mode, "items": items, "missing": missing}


def render_report(res: dict) -> str:
    if not res.get("ok"):
        return f"[six_layer_check] {res.get('error')}"
    lines = [f"[six_layer_check] 项目: {res['root']}  模式: {res['mode']}"]
    for it in res["items"]:
        mark = "✓" if it["exists"] else "✗"
        lines.append(f"  {mark} [{it['phase']:7s}] {it['name']}")
    missing = res.get("missing") or []
    if missing:
        lines.append("缺失项（= 框架骨架被跳过的证据）：")
        lines.extend(missing)
        lines.append("→ 开工前缺失：应补 Phase 0（git 基线）/ Phase 0.5（知识资产初始化 + read_knowledge 召回）")
        lines.append("→ 收尾缺失：应补 Phase 5 收尾核对（rule 51）+ Phase 7 蒸馏（六步含人工 Gate）")
    else:
        lines.append("✓ 全部检查项就绪")
    return "\n".join(lines)


# ---------- 渲染端静默失效五项检查（rule 79 · v3.14.0 新增） ----------
# 来源：2026-09-05 家俊 Electron 实战复盘硬伤2——Tailwind content 漏扫导致
# typecheck 绿 / build 绿 / 运行不崩，但 UI 全没样式，三轮才定位根因。
# 同类"静默失效"藏在五处配置里，本子命令一次扫完。
# 注意：这里做的是"计数/覆盖比对"，与上面 CHECKS 的"文件存在性"是两类检查，
# 不塞进 CHECKS 列表，独立成函数（Plan 评审结论）。

_SCAN_EXCLUDES = {"node_modules", ".git", "dist", "build", "out", "release",
                  "coverage", ".workbuddy", "archive", "__pycache__"}
_SRC_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte"}


def _walk_src(root: Path):
    """遍历源码文件（剪枝 node_modules/dist 等），yield (Path, 相对posix路径)"""
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        dirnames[:] = [d for d in dirnames
                       if d not in _SCAN_EXCLUDES and not d.startswith(".")]
        for fn in filenames:
            yield Path(dirpath) / fn, (rel / fn).as_posix() if str(rel) != "." else fn


def _iter_source_dirs(root: Path) -> set:
    """收集含源码/html 文件的目录（相对 posix 路径）"""
    dirs = set()
    for p, relp in _walk_src(root):
        if Path(relp).suffix.lower() in _SRC_EXTS | {".html"}:
            dirs.add(str(Path(relp).parent.as_posix()) if str(Path(relp).parent) != "." else ".")
    return dirs


def _glob_prefix(glob_pat: str) -> str:
    """把 glob 模式归约为'目录前缀'：./src/**/*.{js,ts} → src；src/*.{js,ts} → src；**/* → 空(覆盖一切)"""
    g = glob_pat.replace("\\", "/").strip()
    while g.startswith("./"):
        g = g[2:]
    i = g.find("/**")
    if i != -1:
        return g[:i].rstrip("/")
    g = re.sub(r"/\*.*$", "", g)   # 剥 /*、/*.{...}、/*.ts
    g = re.sub(r"\*.*$", "", g)    # 剥裸 * 开头
    return g.rstrip("/")


def _glob_covers(glob_pat: str, src_dir: str) -> bool:
    """近似判定 glob 是否覆盖某源码目录（宽进严出：有前缀关系即算覆盖，宁漏报不误报）"""
    g = _glob_prefix(glob_pat)
    if not g or g in ("**", "*"):
        return True
    d = src_dir.strip("/")
    if not d or d == ".":
        return True
    return d == g or d.startswith(g + "/") or g.startswith(d + "/")


def _check_tsconfig(root: Path, src_dirs: set) -> dict:
    name = "tsconfig include 覆盖源码目录"
    files = sorted(root.glob("tsconfig*.json"))
    if not files:
        return {"key": "tsconfig", "name": name, "status": "SKIP",
                "detail": "未找到 tsconfig*.json（可能不用 TS）"}
    patterns = []
    for f in files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)      # 去 jsonc 块注释
        txt = re.sub(r"^\s*//.*$", "", txt, flags=re.M)      # 去行注释
        try:
            cfg = json.loads(txt)
        except Exception:
            continue
        co = cfg.get("compilerOptions", {})
        patterns.extend(co.get("include") or [])
        patterns.extend(co.get("files") or [])
        if co.get("extends") and not patterns:
            return {"key": "tsconfig", "name": name, "status": "SKIP",
                    "detail": f"{f.name} extends {co['extends']}，include 在基配置中，需人工确认"}
    if not patterns:
        return {"key": "tsconfig", "name": name, "status": "PASS",
                "detail": "未显式 include/files（TS 默认包含全部）"}
    code_dirs = sorted(d for d in src_dirs if d != ".")
    uncovered = [d for d in code_dirs if not any(_glob_covers(p, d) for p in patterns)]
    if uncovered:
        return {"key": "tsconfig", "name": name, "status": "FAIL",
                "detail": "以下源码目录不在 include/files 内（typecheck 对其假绿，参照 R-008）: "
                          + ", ".join(uncovered)}
    return {"key": "tsconfig", "name": name, "status": "PASS",
            "detail": f"{len(patterns)} 个模式覆盖 {len(code_dirs)} 个源码目录"}


def _check_vite_input(root: Path) -> dict:
    name = "vite 多入口 input 登记"
    cfg_path = None
    for ext in ("ts", "js", "mjs", "cjs"):
        p = root / f"vite.config.{ext}"
        if p.exists():
            cfg_path = p
            break
    htmls = sorted(relp for _, relp in _walk_src(root)
                   if relp.lower().endswith(".html"))
    if not htmls:
        return {"key": "vite", "name": name, "status": "SKIP",
                "detail": "项目内无 html 入口"}
    if cfg_path is None:
        return {"key": "vite", "name": name, "status": "SKIP",
                "detail": "未找到 vite.config.*（可能不用 vite）"}
    txt = cfg_path.read_text(encoding="utf-8", errors="ignore")
    has_input = re.search(r"\binput\s*[:=]", txt)
    if len(htmls) == 1 and not has_input:
        return {"key": "vite", "name": name, "status": "PASS",
                "detail": "单入口，vite 默认 index.html"}
    if len(htmls) > 1 and not has_input:
        return {"key": "vite", "name": name, "status": "FAIL",
                "detail": f"发现 {len(htmls)} 个 html 但 vite 配置无 rollupOptions.input"
                          f"（新窗口不打包→加载 404 静默白屏）: {', '.join(htmls)}"}
    missing = [h for h in htmls if Path(h).name not in txt and h not in txt]
    if missing:
        return {"key": "vite", "name": name, "status": "FAIL",
                "detail": "以下 html 未出现在 vite input 中（不会被打包）: " + ", ".join(missing)}
    return {"key": "vite", "name": name, "status": "PASS",
            "detail": f"{len(htmls)} 个入口均已登记"}


def _check_tailwind_content(root: Path, src_dirs: set) -> dict:
    name = "tailwind content 覆盖源码目录"
    cfg_path = None
    for ext in ("js", "ts", "cjs", "mjs"):
        p = root / f"tailwind.config.{ext}"
        if p.exists():
            cfg_path = p
            break
    if cfg_path is None:
        for _, relp in _walk_src(root):
            if relp.lower().endswith(".css"):
                try:
                    if "tailwindcss" in (root / relp).read_text(encoding="utf-8", errors="ignore"):
                        return {"key": "tailwind", "name": name, "status": "SKIP",
                                "detail": "检测到 tailwind v4 CSS-first（@import \"tailwindcss\"），"
                                          "content 由 @source 管理，需人工核对"}
                except Exception:
                    pass
        return {"key": "tailwind", "name": name, "status": "SKIP",
                "detail": "未找到 tailwind.config.*（可能未用 tailwind）"}
    txt = cfg_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"content\s*:\s*\[(.*?)\]", txt, flags=re.S)
    if not m:
        return {"key": "tailwind", "name": name, "status": "SKIP",
                "detail": "配置中未解析到 content 数组（可能用 preset），需人工确认"}
    pats = re.findall(r"['\"`]([^'\"`]+)['\"`]", m.group(1))
    code_dirs = sorted(d for d in src_dirs if d != ".")
    uncovered = [d for d in code_dirs if not any(_glob_covers(p, d) for p in pats)]
    if uncovered:
        return {"key": "tailwind", "name": name, "status": "FAIL",
                "detail": "以下目录不在 content 覆盖内（UI 样式静默丢失，硬伤2 三轮根因）: "
                          + ", ".join(uncovered) + f"（当前 {len(pats)} 个模式：{'; '.join(pats)}）"}
    return {"key": "tailwind", "name": name, "status": "PASS",
            "detail": f"{len(pats)} 个 content 模式覆盖 {len(code_dirs)} 个源码目录"}


def _check_preload_dts(root: Path) -> dict:
    name = "preload window.* 引用均有类型声明"
    refs = set()
    dts_files = []
    for p, relp in _walk_src(root):
        suffix = Path(relp).suffix.lower()
        if relp.lower().endswith(".d.ts"):
            dts_files.append(p)
            continue
        if suffix in _SRC_EXTS | {".html"}:
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for mm in re.finditer(r"window\.(\w+)\.", txt):
                refs.add(mm.group(1))
    if not refs:
        return {"key": "preload", "name": name, "status": "SKIP",
                "detail": "renderer 未引用 window.*（可能经 import 暴露）"}
    if not dts_files:
        return {"key": "preload", "name": name, "status": "FAIL",
                "detail": f"renderer 引用了 window.{sorted(refs)[0]}.* 等，但项目无任何 .d.ts 声明"
                          f"（preload 类型假绿，改 API 名不会报错）"}
    declared = set()
    for p in dts_files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for mm in re.finditer(r"(\w+)\s*:\s*\{", txt):
            declared.add(mm.group(1))
        for mm in re.finditer(r"(?:readonly\s+)?(\w+)\s*[:(]", txt):
            declared.add(mm.group(1))
    missing = sorted(r for r in refs if r not in declared)
    if missing:
        return {"key": "preload", "name": name, "status": "FAIL",
                "detail": "以下 window.* 命名空间未在任何 d.ts 中声明: " + ", ".join(missing)}
    return {"key": "preload", "name": name, "status": "PASS",
            "detail": f"{len(refs)} 个 window.* 命名空间均有声明（{len(dts_files)} 个 d.ts）"}


def _check_ipc_consistency(root: Path) -> dict:
    name = "IPC 通道 preload↔main 集合一致"
    main_ch, preload_ch = set(), set()
    found = False
    for p, relp in _walk_src(root):
        if Path(relp).suffix.lower() not in _SRC_EXTS:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        txt = re.sub(r"/\*.*?\*/|^\s*//.*$", "", txt, flags=re.S | re.M)  # 去注释
        if "ipcMain" in txt:
            for mm in re.finditer(r"ipcMain\.(?:handle|on)\(\s*['\"`]([\w:.\-/]+)['\"`]", txt):
                main_ch.add(mm.group(1))
                found = True
        if "ipcRenderer" in txt:
            for mm in re.finditer(r"ipcRenderer\.(?:invoke|send|on)\(\s*['\"`]([\w:.\-/]+)['\"`]", txt):
                preload_ch.add(mm.group(1))
                found = True
    if not found:
        return {"key": "ipc", "name": name, "status": "SKIP",
                "detail": "未发现字符串字面量通道（可能经常量注册或不用 IPC）"}
    orphan_pre = sorted(preload_ch - main_ch)
    orphan_main = sorted(main_ch - preload_ch)
    if orphan_pre:
        extra = f"；另有未被调用的 handler: {', '.join(orphan_main)}" if orphan_main else ""
        return {"key": "ipc", "name": name, "status": "FAIL",
                "detail": "preload 调用但主进程未注册（invoke 静默无响应）: "
                          + ", ".join(orphan_pre) + extra}
    if orphan_main:
        return {"key": "ipc", "name": name, "status": "FAIL",
                "detail": "主进程注册但 preload 未调用（疑似僵尸 handler，参照 R-007）: "
                          + ", ".join(orphan_main)}
    return {"key": "ipc", "name": name, "status": "PASS",
            "detail": f"两侧通道一致（{len(main_ch)} 条）"}


def check_render_silent_fail(project_dir: str) -> dict:
    """渲染端静默失效五项检查（rule 79）。配置存在才查，不存在 SKIP 防误报。"""
    root = Path(project_dir)
    if not root.is_dir():
        return {"ok": False, "error": f"目录不存在: {project_dir}"}
    src_dirs = _iter_source_dirs(root)
    items = [
        _check_tsconfig(root, src_dirs),
        _check_vite_input(root),
        _check_tailwind_content(root, src_dirs),
        _check_preload_dts(root),
        _check_ipc_consistency(root),
    ]
    return {"ok": True, "root": str(root), "mode": "render-silent-fail",
            "items": items,
            "fail_count": sum(1 for r in items if r["status"] == "FAIL"),
            "skip_count": sum(1 for r in items if r["status"] == "SKIP")}


def render_silent_fail_report(res: dict) -> str:
    lines = [f"[six_layer_check] 项目: {res['root']}  模式: {res['mode']}"
             f"（渲染端静默失效五项 · rule 79）"]
    for it in res["items"]:
        mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "-"}.get(it["status"], "?")
        if it["status"] == "PASS":
            lines.append(f"  {mark} [{it['status']:4s}] {it['name']}  ({it['detail']})")
        else:
            lines.append(f"  {mark} [{it['status']:4s}] {it['name']}  <-  {it['detail']}")
    if res["fail_count"]:
        lines.append(f"✗ 发现 {res['fail_count']} 项静默失效隐患"
                     f"（SKIP {res['skip_count']} 项需人工复核）")
        lines.append("→ 处置对照 references/symptom_triage.md 卡2/卡3；知识库 R-008（类型门禁假绿）+ R-010")
    else:
        lines.append(f"✓ 五项检查通过（SKIP {res['skip_count']} 项：配置不存在，未触发）")
    return "\n".join(lines)


def main():
    argv = sys.argv[1:]
    verb = argv[0] if argv and argv[0] == "render-silent-fail" else None
    if verb:
        argv = argv[1:]
    args = [a for a in argv if not a.startswith("--")]
    flags = set(a for a in argv if a.startswith("--"))
    project_dir = args[0] if args else "."
    mode = "auto"
    for m in ("init", "deliver"):
        if f"--mode={m}" in flags or f"--mode {m}" in " ".join(sys.argv):
            mode = m
    strict = "--strict" in flags
    as_json = "--json" in flags

    if verb == "render-silent-fail":
        res = check_render_silent_fail(project_dir)
        if not res.get("ok"):
            print(f"[six_layer_check] {res.get('error')}")
            sys.exit(2)
        if as_json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(render_silent_fail_report(res))
        if strict and res.get("fail_count", 0) > 0:
            sys.exit(1)
        sys.exit(0)

    res = check(project_dir, mode)
    if not res.get("ok"):
        print(f"[six_layer_check] {res.get('error')}")
        sys.exit(2)
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render_report(res))
    if strict and res.get("missing"):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
