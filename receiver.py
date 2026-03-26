import hashlib
import zipfile
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

class PartyTrickHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed = urlparse(self.path)
        sender_host = unquote(parsed.path).strip("/") or "Unknown"
        msg = self.headers.get('X-Message', 'No message')
        public_ip = self.headers.get('X-Public-IP', 'Unknown')
        local_ip = self.client_address[0]
        sent_hash = self.headers.get('X-File-Hash', '')

        # Read raw bytes
        content_length = int(self.headers.get('Content-Length', 0))
        raw_data = self.rfile.read(content_length)
        print(f"DEBUG: Received {len(raw_data)} bytes")

        # Try to interpret as zip
        is_zip = False
        original_filename = None
        extracted_bytes = None

        # First, check if the data is a zip file (magic bytes PK)
        if len(raw_data) >= 4 and raw_data[:4] == b'PK\x03\x04':
            print("DEBUG: Data appears to be a ZIP archive")
            try:
                with zipfile.ZipFile(io.BytesIO(raw_data)) as zf:
                    # Get the first file in the archive (should be the pub key)
                    file_list = zf.namelist()
                    if file_list:
                        original_filename = file_list[0]
                        with zf.open(original_filename) as f:
                            extracted_bytes = f.read()
                        print(f"DEBUG: Extracted {len(extracted_bytes)} bytes from {original_filename}")
                        is_zip = True
            except Exception as e:
                print(f"DEBUG: Failed to extract zip: {e}")

        if is_zip and extracted_bytes is not None:
            # Use extracted bytes as the actual file content
            file_bytes = extracted_bytes
            # Determine extension from original filename or default .pub
            if original_filename:
                ext = original_filename.split('.')[-1] if '.' in original_filename else 'pub'
                filename = f"received_{sender_host}_{original_filename}"
            else:
                filename = f"received_{sender_host}.pub"
        else:
            # Not a valid zip, treat as raw (maybe "Not found" text)
            file_bytes = raw_data
            filename = f"received_{sender_host}.txt"

        # Compute hash of the final file_bytes
        received_hash = hashlib.sha256(file_bytes).hexdigest()
        print(f"DEBUG: Received hash: {received_hash}")

        # Save the file
        with open(filename, 'wb') as f:
            f.write(file_bytes)

        # Verify hash if provided
        if sent_hash and sent_hash != "none" and sent_hash != received_hash:
            print(f"WARNING: Hash mismatch! Expected {sent_hash}, got {received_hash}")
            status_text = f"[bold red]Hash mismatch! Data may be corrupted.[/bold red]"
        else:
            status_text = f"[bold green]Saved {len(file_bytes)} bytes to {filename}[/bold green]"

        # Preview (try to decode as text)
        try:
            preview_text = file_bytes.decode('utf-8')
            preview = preview_text[:200] + ("..." if len(preview_text) > 200 else "")
        except UnicodeDecodeError:
            preview = f"<Binary data: {len(file_bytes)} bytes>"

        # Rich display
        content = Table.grid(padding=(0, 2))
        content.add_column(justify="left", style="bold cyan")
        content.add_column(justify="left")
        content.add_row("Host:", sender_host)
        content.add_row("Local IP:", local_ip)
        content.add_row("Public IP:", public_ip)
        content.add_row("Message:", msg)
        content.add_row("Status:", Text.from_markup(status_text))
        if preview:
            content.add_row("Preview:", Text(preview, style="dim white"))

        panel = Panel(content, title="[bold yellow]File Received[/bold yellow]",
                      expand=False, padding=(1, 5))
        console.print(panel)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Receiver is running. Waiting for POST requests.")

    def log_message(self, format, *args):
        pass

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, PartyTrickHandler)
    console.print("[bold yellow]Ready for the party trick![/bold yellow]")
    console.print(f"[dim]Listening on port {port}. Plug in the USB device now...[/dim]\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[bold red]Shutting down receiver...[/bold red]")
        httpd.server_close()

if __name__ == "__main__":
    run_server()