# Digispark RC — USB Party Trick

A two-part project: a **Digispark ATtiny85** USB device that auto-types a command on plug-in, and a **Python HTTP receiver** that catches the message and displays it in a styled terminal panel.

## Project Structure

```
digispark_rc/
├── receiver.py                          # Python HTTP server (Rich UI)
├── requirements.txt                     # Python dependencies
├── digispark_sketch/
│   └── digispark_sketch.ino             # Arduino sketch for Digispark
└── README.md
```

## Setup

### 1. Python Receiver

```bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Start the receiver
python receiver.py
```

The server listens on **port 8080** by default.

### 2. Digispark Sketch

1. Open `digispark_sketch/digispark_sketch.ino` in the **Arduino IDE**.
2. Install the **Digistump AVR Boards** package via Board Manager.
3. Edit the configuration at the top of the sketch:
   - `RECEIVER_IP` — IP address of the machine running `receiver.py`
   - `RECEIVER_PORT` — Port (default `8080`)
   - `MESSAGE` — The text you want to appear on the receiver
4. Select **Digispark (Default — 16.5 MHz)** as the board.
5. Click **Upload**, then plug in the Digispark when prompted.

## How It Works

1. Plug the Digispark into a Windows machine.
2. It emulates a keyboard and types a PowerShell one-liner that sends an HTTP GET request to the receiver.
3. The Python receiver catches the request and displays the message in a Rich-styled terminal panel.
