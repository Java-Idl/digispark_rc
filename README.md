# Digispark RC - VAPT Capstone Project

**Disclaimer:** This repository contains tools and scripts developed strictly for educational purposes as part of a Vulnerability Assessment and Penetration Testing (VAPT) course. Do not use these tools on systems or networks for which you do not have explicit authorization.

## Overview

This repository contains the source code for a 3rd-year, 6th-semester capstone project in Vulnerability Assessment and Penetration Testing. The project demonstrates a complete data exfiltration lifecycle. It shows how a payload can establish a connection, download a secondary executable, maintain persistence, and exfiltrate specific local files (in this case, SSH keys) back to a control server.

## Project Architecture

The attack simulation consists of three main components working together:

1.  **Command and Control (C2) Server:** A Python-based server that hosts the secondary payload and listens for incoming stolen data.
2.  **Initial Payload (Stager):** A PowerShell script that runs on the target machine, downloads the main executable, and sets up a Windows Scheduled Task so the program runs repeatedly.
3.  **Data Exfiltration Client:** A compiled C program that silently compresses the user's `.ssh` directory and uploads the resulting ZIP archive to the C2 server.

## File Descriptions

* **`receiver.py`**: A Python HTTP server. It serves two purposes: it allows the target to download `client.exe` via a GET request, and it receives the exfiltrated ZIP files via a POST request. It uses the `rich` library to display a clear, formatted log of received data in the terminal.
* **`payload.ps1`**: The initial script executed on the target. It attempts to download `client.exe` from the Python server with built-in retry logic. Once downloaded, it executes the file silently and registers a scheduled task for persistence.
* **`reverse_shell.c`**: The source code for `client.exe`. Despite the name, it functions as an exfiltration tool rather than a standard shell. When run, it executes a PowerShell command in memory to locate the `.ssh` folder, compress its contents into a ZIP archive, and upload it to the server.
* **`test.ps1`**: A minor test file indicating the expected server response format.

## Setup and Usage

### Prerequisites

* Python 3.x installed on the attacker machine.
* The Python `rich` library installed (`pip install rich`).
* A C compiler (like GCC or MinGW) to compile the executable.
* A target machine running Windows (for the PowerShell scripts and executable).

### Step 1: Configuration and Compilation

1.  Open `reverse_shell.c` in a text editor.
2.  Change the `DEFAULT_IP` to the IP address of the machine that will run `receiver.py`.
3.  Compile the C program into an executable named `client.exe`. If using GCC, the command is:
    ```bash
    gcc reverse_shell.c -o client.exe
    ```

### Step 2: Starting the Server

1.  Place the newly compiled `client.exe` in the same directory as `receiver.py`.
2.  Start the receiver server:
    ```bash
    python receiver.py
    ```
    The server will start listening on port 8080 by default.

### Step 3: Execution on the Target

1.  Open `payload.ps1` and ensure the `$clientUrl` variable matches the IP address of your Python server.
2.  Transfer `payload.ps1` to the target Windows machine.
3.  Run the PowerShell script. It will download the client, execute the exfiltration routine, and send the data back to your Python server.

## Features Demonstrated

* **File Transfer:** Serving binaries over HTTP.
* **Persistence:** Creating scheduled tasks in Windows to maintain access.
* **Data Compression:** Zipping directories dynamically in memory.
* **Data Exfiltration:** Sending files out of a network via HTTP POST requests.
* **Log Management:** Structuring server-side logging for incoming connections and data validation.
