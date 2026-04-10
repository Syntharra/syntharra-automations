Set-Location 'c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
Add-Content 'c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations\.claude\weekly-task.log' "[$timestamp] Weekly self-improvement started"
& 'C:\Python314\python.exe' 'c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations\tools\weekly_self_improvement.py' >> 'c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations\.claude\weekly-task.log' 2>&1
Add-Content 'c:\Users\danie\Desktop\Syntharra\Cowork\Syntharra Project\syntharra-automations\.claude\weekly-task.log' "[$timestamp] Done"
