param([ValidateSet('packs','full')][string]$Kind = 'packs')

# Sends a Board Paper Machine reminder email to Henry. Invoked by Windows Task Scheduler.
$repo = "C:\Users\henry.anderson\OneDrive - HSJ Information Ltd\Documents\My assistant\projects\Board-paper-machine"
Set-Location -Path $repo

if ($Kind -eq 'full') {
    # Fires every Monday but only the FIRST Monday of the month should send.
    if ((Get-Date).Day -gt 7) { return }
    $subject = '[BPM reminder] Monthly FULL date scan due today'
    $body    = 'reminders\bpm_fullscan_reminder.md'
} else {
    $subject = '[BPM reminder] Packs run due today (Mon/Thu)'
    $body    = 'reminders\bpm_packs_reminder.md'
}

python send_email.py --to henry.anderson@hsj.co.uk --subject $subject --body-file $body --env-file .env.local --from-name "Board paper machine"
