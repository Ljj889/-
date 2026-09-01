#!/usr/bin/env bash
# ============================================================
# push_to_remote.sh — 建私有仓 + 推送 six-layer-orchestrator
# v1.0 · 2026-09-01
#
# 前置：先完成 gh 登录（凭据类操作，由家俊本人执行）：
#   D:/tools/bin/gh.exe auth login     # GitHub.com → HTTPS → 浏览器授权
# 本脚本会用系统代理访问 GitHub（家俊机器实测 127.0.0.1:7897）。
#
# 用法：
#   ./push_to_remote.sh                 # 建仓（如不存在）+ 推送（含 tag）
#   ./push_to_remote.sh --push-only     # 仓库已存在，只推送
# ============================================================

set -euo pipefail

GH="D:/tools/bin/gh.exe"
PROXY="http://127.0.0.1:7897"
REPO_NAME="six-layer-orchestrator"

echo "=== 1/4 检查 gh 登录状态 ==="
if ! HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" "$GH" auth status >/dev/null 2>&1; then
  echo "✗ 未登录。请先执行："
  echo "  $GH auth login"
  echo "（选 GitHub.com → HTTPS → 浏览器授权）"
  exit 1
fi
echo "✓ 已登录"

echo "=== 2/4 检查远程仓库是否存在 ==="
if HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" "$GH" repo view "$REPO_NAME" >/dev/null 2>&1; then
  echo "仓库已存在，跳过建仓"
  REMOTE_URL="https://github.com/$(HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" "$GH" api user --jq '.login')/$REPO_NAME.git"
else
  if [[ "${1:-}" == "--push-only" ]]; then
    echo "✗ 远程仓库不存在且指定了 --push-only，无法推送"
    exit 1
  fi
  echo "仓库不存在，创建私有仓…"
  REMOTE_URL="$(HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" "$GH" repo create "$REPO_NAME" --private --source . --remote origin --push 2>&1 | tail -1)"
  echo "✓ 已建仓并推送: $REMOTE_URL"
  echo "=== 3/4 推送 tag ==="
  git push origin --tags
  echo "=== 4/4 完成 ==="
  git remote -v
  exit 0
fi

echo "=== 3/4 配置 remote 并推送 ==="
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"
git push -u origin HEAD:master
git push origin --tags

echo "=== 4/4 完成 ==="
git remote -v
