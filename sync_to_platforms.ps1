# ============================================================
# sync_to_platforms.ps1 - Windows-native twin of sync_to_platforms.sh
# v1.0 - 2026-09-12 - added because this machine has ONLY WSL bash
#        (WSL cannot resolve the "C:/Users/..." paths used by the .sh script;
#         Git Bash is not installed). Keep both scripts in the repo.
#
# Usage:
#   powershell -File sync_to_platforms.ps1            # sync all three targets
#   powershell -File sync_to_platforms.ps1 wb         # only WorkBuddy
#   powershell -File sync_to_platforms.ps1 cb         # only CodeBuddy
#   powershell -File sync_to_platforms.ps1 codex      # only Codex
#   powershell -File sync_to_platforms.ps1 -Check     # read-only consistency check
#
# Behavior: copies SKILL.md + knowledge/ + references/ + scripts/ into each
#           platform skills dir; never touches .bak / archive in the targets.
# ASCII-only on purpose: Windows PowerShell 5.1 mis-decodes BOM-less UTF-8 .ps1.
# ============================================================
param(
  [Parameter(Position = 0)][string]$Target = '',
  [switch]$Check
)
$ErrorActionPreference = 'Stop'

$repo = $PSScriptRoot
$skill = 'SKILL.md'
$dirs = @('knowledge', 'references', 'scripts')
$targets = [ordered]@{
  wb    = 'C:\Users\one\.workbuddy\skills\six-layer-orchestrator'
  cb    = 'C:\Users\one\.codebuddy\skills\six-layer-orchestrator'
  codex = 'D:\Ai\codex\skills\six-layer-orchestrator'
}

function Get-FirstVersion([string]$path) {
  if (-not (Test-Path $path)) { return '<missing>' }
  $m = [regex]::Match((Get-Content $path -Raw -Encoding UTF8), 'v\d+\.\d+\.\d+')
  if ($m.Success) { return $m.Value } else { return '<none>' }
}

function Get-AssetCount([string]$dst) {
  $idx = Join-Path $dst 'knowledge\_index.md'
  if (-not (Test-Path $idx)) { return -1 }
  $txt = Get-Content $idx -Raw -Encoding UTF8
  return ([regex]::Matches($txt, '(?m)^\| (rules|decisions|guides|framework-skills)/')).Count
}

function Test-Consistency([string]$dst) {
  $bad = 0
  if (-not (Test-Path (Join-Path $dst $skill))) { Write-Host "  x missing $skill"; $bad++ }
  foreach ($d in $dirs) {
    if (-not (Test-Path (Join-Path $dst $d))) { Write-Host "  x missing dir $d/"; $bad++ }
  }
  $sv = Get-FirstVersion (Join-Path $repo $skill)
  $dv = Get-FirstVersion (Join-Path $dst $skill)
  if ($sv -eq $dv) { Write-Host "  ok version $sv" } else { Write-Host "  x version mismatch: repo=$sv target=$dv"; $bad++ }
  $sn = Get-AssetCount $repo
  $dn = Get-AssetCount $dst
  if ($sn -eq $dn -and $sn -ge 0) { Write-Host "  ok assets $sn" } else { Write-Host "  x asset count: repo=$sn target=$dn"; $bad++ }
  return $bad
}

function Sync-One([string]$dst) {
  Write-Host "=== sync -> $dst ==="
  if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
  Copy-Item (Join-Path $repo $skill) (Join-Path $dst $skill) -Force
  foreach ($d in $dirs) {
    $to = Join-Path $dst $d
    if (Test-Path $to) { Remove-Item $to -Recurse -Force }
    Copy-Item (Join-Path $repo $d) $to -Recurse -Force
  }
  Write-Host "  copied $skill + $($dirs -join '/')/"
  if ((Test-Consistency $dst) -eq 0) { Write-Host "  ok consistency passed" } else { Write-Host "  ! consistency has gaps (see above)" }
}

if ($Check) {
  Write-Host "=== consistency check (read-only) ==="
  foreach ($k in $targets.Keys) {
    Write-Host "[$k]"
    [void](Test-Consistency $targets[$k])
  }
  exit 0
}

if ($Target) {
  if (-not $targets.Contains($Target)) {
    Write-Host "unknown target: $Target (valid: $($targets.Keys -join ' / ') or -Check)"
    exit 1
  }
  Sync-One $targets[$Target]
} else {
  foreach ($k in $targets.Keys) { Sync-One $targets[$k] }
}

Write-Host ''
Write-Host 'done. verify with: powershell -File sync_to_platforms.ps1 -Check'
