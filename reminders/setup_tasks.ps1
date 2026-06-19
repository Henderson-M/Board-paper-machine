# Registers the Board Paper Machine reminder scheduled tasks on this Windows machine.
# Re-run this on a new machine to recreate the reminders. Safe to re-run (uses -Force).
# These are REMINDERS only — they email Henry to run BPM himself; they do NOT run BPM or send team alerts.

$script = "C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine\reminders\send_reminder.ps1"
$settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

# Packs reminder — Monday + Thursday 09:00 local
$aAction  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`" packs"
$aTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Thursday -At 9:00am
Register-ScheduledTask -TaskName "BPM Reminder - Packs (Mon Thu)" -Action $aAction -Trigger $aTrigger -Settings $settings -Principal $principal -Force

# Full date-scan reminder — every Monday 09:00, but send_reminder.ps1 only emails on the FIRST Monday of the month
$bAction  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`" full"
$bTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00am
Register-ScheduledTask -TaskName "BPM Reminder - Full date scan (monthly)" -Action $bAction -Trigger $bTrigger -Settings $settings -Principal $principal -Force

Write-Host "Done. View/edit in Task Scheduler under the names above, or run: Get-ScheduledTask -TaskName 'BPM Reminder*'"
