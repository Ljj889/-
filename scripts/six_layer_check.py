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

退出码：0=检查完成（非 strict） / 1=有缺失（strict） / 2=目录不存在
"""
import json
import os
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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    project_dir = args[0] if args else "."
    mode = "auto"
    for m in ("init", "deliver"):
        if f"--mode={m}" in flags or f"--mode {m}" in " ".join(sys.argv):
            mode = m
    strict = "--strict" in flags
    as_json = "--json" in flags

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
