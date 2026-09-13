#Requires -Version 5.1
<#
  収集(collect.py)からagent-trend-dataへのpushまでを一気通貫で行う
  ローカル実行用オーケストレーションスクリプト。

  前提: agent-trend-dataがagent-trend-radarと同階層の兄弟ディレクトリ
  (..\agent-trend-data)にcloneされていること。GitHub Actions経由の
  PAT連携(.github/workflows/collect-and-publish.yml)を発行するまでの
  暫定手段(Issue.md #24参照)。
#>

$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$hubPath = Resolve-Path (Join-Path $repoRoot "..\agent-trend-data")
$runDate = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")

function Invoke-Step {
    param([string]$Description, [scriptblock]$Action)
    Write-Host "== $Description =="
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "$Description に失敗しました(exit $LASTEXITCODE)"
    }
}

Push-Location $repoRoot
try {
    Invoke-Step "収集(collect.py)" { uv run scripts/collect.py }

    $exportPath = Join-Path $repoRoot "hub_export\metrics.json"
    Invoke-Step "ハブ向けスナップショット出力" { uv run scripts/export_hub_snapshot.py $exportPath }

    $snapshotDir = Join-Path $hubPath "snapshots\$runDate"
    New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
    Copy-Item $exportPath (Join-Path $snapshotDir "metrics.json") -Force
    Copy-Item $exportPath (Join-Path $hubPath "latest\metrics.json") -Force

    $manifestPath = Join-Path $hubPath "manifest.json"
    Invoke-Step "manifest.json更新" { uv run scripts/update_hub_manifest.py $manifestPath $runDate }
}
finally {
    Pop-Location
}

Push-Location $hubPath
try {
    git add snapshots manifest.json latest
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "agent-trend-dataに変更はありません。pushをスキップします。"
    }
    else {
        git commit -m "data: $runDate snapshot"
        if ($LASTEXITCODE -ne 0) { throw "agent-trend-dataへのcommitに失敗しました" }
        git push
        if ($LASTEXITCODE -ne 0) { throw "agent-trend-dataへのpushに失敗しました(コンフリクト等の可能性)" }
        Write-Host "agent-trend-dataへpushしました($runDate)。"
    }
}
finally {
    Pop-Location
}
