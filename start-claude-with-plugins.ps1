#!/usr/bin/env pwsh
# start-claude-with-plugins.ps1
# Launch Claude with local plugin folders from this workspace.

$workspaceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pluginRoot = Join-Path $workspaceRoot 'plugins'

Write-Host "workspaceRoot=$workspaceRoot"
Write-Host "pluginRoot=$pluginRoot"
Write-Host "pluginRoot exists: " (Test-Path $pluginRoot)

if (-not (Test-Path $pluginRoot)) {
    Write-Error "Plugins folder not found: $pluginRoot"
    exit 1
}

$pluginDirs = Get-ChildItem -LiteralPath $pluginRoot -Recurse -Force -Directory -Filter '.claude-plugin' | ForEach-Object { Split-Path -Path $_.FullName -Parent } | Sort-Object -Unique

if ($pluginDirs.Count -eq 0) {
    Write-Error "No local Claude plugin directories found under $pluginRoot."
    exit 1
}

$claudeArgs = @()
foreach ($dir in $pluginDirs) {
    $claudeArgs += '--plugin-dir'
    $claudeArgs += $dir
}

if ($args) {
    $claudeArgs += $args
}

Write-Host "Starting Claude with local plugin dirs:"
foreach ($dir in $pluginDirs) {
    Write-Host "  $dir"
}

claude @claudeArgs
