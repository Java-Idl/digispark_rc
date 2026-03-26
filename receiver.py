import base64
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

        # Read the raw POST body (as string, since we sent a string)
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8')

        # Attempt to decode as Base64; if it fails, treat as plain text
        try:
            # The body should be a Base64 string. Decode it to raw bytes.
            file_bytes = base64.b64decode(raw_body)
            is_base64 = True
        except Exception:
            # Not valid Base64 – treat as plain text (e.g., "Not found")
            file_bytes = raw_body.encode('utf-8')
            is_base64 = False

        # Determine filename extension
        if is_base64 and file_bytes.startswith(b'ssh-'):
            ext = '.pub'
        elif is_base64:
            ext = '.bin'
        else:
            ext = '.txt'

        filename = f"received_{sender_host}{ext}"
        with open(filename, 'wb') as f:
            f.write(file_bytes)

        # Prepare preview
        try:
            # If it's a text file, show a preview
            preview_text = file_bytes.decode('utf-8')
            preview = preview_text[:200] + ("..." if len(preview_text) > 200 else "")
            status_text = f"[bold green]Saved {len(file_bytes)} bytes to {filename}[/bold green]"
        except UnicodeDecodeError:
            preview = f"<Binary data: {len(file_bytes)} bytes>"
            status_text = f"[bold green]Saved {len(file_bytes)} bytes (binary) to {filename}[/bold green]"

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

        # Debug print
        print(f"DEBUG: Received {len(file_bytes)} bytes from {sender_host} -> {filename}")

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