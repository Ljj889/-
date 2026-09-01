#!/usr/bin/env bash
# ============================================================
# sync_to_platforms.sh — 将 six-layer-orchestrator 仓库同步到三处平台 skills 目录
# v1.0 · 2026-09-01 · rule 64 引擎化（能脚本化的不靠自觉）
#
# 用法：
#   ./sync_to_platforms.sh            # 同步全部三处
#   ./sync_to_platforms.sh wb         # 只同步 WorkBuddy
#   ./sync_to_platforms.sh cb         # 只同步 CodeBuddy
#   ./sync_to_platforms.sh codex      # 只同步 Codex
#   ./sync_to_platforms.sh --check    # 只校验三处一致性，不改动文件
#
# 前置：本脚本位于仓库根目录（与 SKILL.md 同级）。
# 行为：复制 SKILL.md + knowledge/ + references/ + scripts/ 到目标目录；
#       不触碰目标目录的 .bak / archive（历史备份）。
# ============================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="SKILL.md"
DIRS=("knowledge" "references" "scripts")

# 目标平台定义（可自行增删）
declare -A TARGETS=(
  [wb]="C:/Users/one/.workbuddy/skills/six-layer-orchestrator"
  [cb]="C:/Users/one/.codebuddy/skills/six-layer-orchestrator"
  [codex]="D:/Ai/codex/skills/six-layer-orchestrator"
)

check_consistency() {
  local dst="$1"
  local missing=0
  [[ -f "$dst/$SKILL" ]] || { echo "  ✗ 缺 $SKILL"; missing=1; }
  for d in "${DIRS[@]}"; do
    [[ -d "$dst/$d" ]] || { echo "  ✗ 缺目录 $d/"; missing=1; }
  done
  # 版本号一致性（取 SKILL.md 中首个 vX.Y.Z 形式的版本标记）
  local src_ver dst_ver
  src_ver="$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' "$REPO_DIR/$SKILL" | head -1 || true)"
  dst_ver="$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' "$dst/$SKILL" | head -1 || true)"
  if [[ "$src_ver" == "$dst_ver" ]]; then
    echo "  ✓ 版本一致: $src_ver"
  else
    echo "  ✗ 版本不一致: 仓库=$src_ver 目标=$dst_ver"; missing=1
  fi
  # 知识资产条数
  local src_n dst_n
  src_n="$(grep -c '^| \(rules\|decisions\|guides\|framework-skills\)/' "$REPO_DIR/knowledge/_index.md" || true)"
  dst_n="$(grep -c '^| \(rules\|decisions\|guides\|framework-skills\)/' "$dst/knowledge/_index.md" || true)"
  if [[ "$src_n" == "$dst_n" ]]; then
    echo "  ✓ 知识资产 $src_n 条"
  else
    echo "  ✗ 资产数不一致: 仓库=$src_n 目标=$dst_n"; missing=1
  fi
  return $missing
}

sync_one() {
  local dst="$1"
  echo "=== 同步 → $dst ==="
  if [[ ! -d "$dst" ]]; then
    echo "  目标目录不存在，创建…"
    mkdir -p "$dst"
  fi
  cp "$REPO_DIR/$SKILL" "$dst/$SKILL"
  for d in "${DIRS[@]}"; do
    rm -rf "$dst/$d"
    cp -r "$REPO_DIR/$d" "$dst/$d"
  done
  echo "  已复制 $SKILL + ${DIRS[*]}/"
  check_consistency "$dst" && echo "  ✓ 一致性通过" || echo "  ⚠ 一致性检查有缺（见上）"
}

# 入口
if [[ "${1:-}" == "--check" ]]; then
  echo "=== 一致性校验（只读）==="
  for key in "${!TARGETS[@]}"; do
    echo "[$key]"
    check_consistency "${TARGETS[$key]}" || true
  done
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  key="$1"
  [[ -n "${TARGETS[$key]:-}" ]] || { echo "未知平台: $key（可选: ${!TARGETS[*]} / --check）"; exit 1; }
  sync_one "${TARGETS[$key]}"
else
  for key in "${!TARGETS[@]}"; do
    sync_one "${TARGETS[$key]}"
  done
fi

echo ""
echo "完成。三处同步后建议跑: ./sync_to_platforms.sh --check"
