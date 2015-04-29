Invoke-expression -Command "C:\Windows\System32\schtasks.exe /DELETE /tn 'vote' /F"
$vote_time = (get-date).AddHours(12).AddMinutes(15).ToString("HH:mm:ss")
Invoke-expression -Command "C:\Windows\System32\schtasks.exe /create /tn 'vote' /tr 'powershell D:\selenium\vote.ps1' /sc daily /st $vote_time /RL HIGHEST"
Invoke-expression -Command "C:\Python27\python.exe D:\selenium\molten.py"
