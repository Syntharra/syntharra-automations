# setup_weekly_task.ps1
# Registers a Windows Task Scheduler job that runs the weekly self-improvement
# script every Monday at 07:00 using your Claude Code subscription.
#
# Run once (as Administrator):
#   powershell -ExecutionPolicy Bypass -File tools\setup_weekly_task.ps1

$TaskName   = "Syntharra-WeeklySelfImprovement"
$RepoRoot   = "c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations"
$PythonExe  = (Get-Command python -ErrorAction SilentlyContinue).Source
# Ensure npm global bin is on PATH so claude.cmd is found
$env:PATH   = "$env:APPDATA\npm;$env:PATH"
$ScriptPath = Join-Path $RepoRoot "tools\weekly_self_improvement.py"
$LogPath    = Join-Path $RepoRoot ".claude\weekly-task.log"

if (-not $PythonExe) {
    Write-Error "Python not found on PATH. Install Python and try again."
    exit 1
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $RepoRoot

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At "07:00AM"

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Redirect output to log file via wrapper
$WrapperScript = Join-Path $RepoRoot ".claude\run_weekly.ps1"
@"
Set-Location '$RepoRoot'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
Add-Content '$LogPath' "[`$timestamp] Weekly self-improvement started"
& '$PythonExe' '$ScriptPath' >> '$LogPath' 2>&1
Add-Content '$LogPath' "[`$timestamp] Done"
"@ | Set-Content $WrapperScript

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NonInteractive -File `"$WrapperScript`""

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Syntharra: weekly Claude Code self-improvement synthesis. Reads FAILURES.md + corrections, writes new rules to RULES.md." `
    -Force

Write-Host ""
Write-Host "Task registered: $TaskName"
Write-Host "Runs: Every Monday at 07:00"
Write-Host "Log:  $LogPath"
Write-Host ""
Write-Host "To run now (test): python tools\weekly_self_improvement.py --dry-run"
Write-Host "To remove task:    Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
