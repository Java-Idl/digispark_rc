import hashlib
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
        print(f"DEBUG: First 100 bytes: {raw_data[:100]}")

        # Compute hash of received data
        received_hash = hashlib.sha256(raw_data).hexdigest()
        print(f"DEBUG: Received hash: {received_hash}")

        # Save raw bytes to file
        filename = f"received_{sender_host}.pub"
        with open(filename, 'wb') as f:
            f.write(raw_data)

        # Verify hash if provided
        if sent_hash and sent_hash != received_hash:
            print(f"WARNING: Hash mismatch! Expected {sent_hash}, got {received_hash}")
            status_text = f"[bold red]Hash mismatch! Data may be corrupted.[/bold red]"
        else:
            status_text = f"[bold green]Saved {len(raw_data)} bytes to {filename}[/bold green]"

        # Preview (try to decode as text)
        try:
            preview_text = raw_data.decode('utf-8')
            preview = preview_text[:200] + ("..." if len(preview_text) > 200 else "")
        except UnicodeDecodeError:
            preview = f"<Binary data: {len(raw_data)} bytes>"

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