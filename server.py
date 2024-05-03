import socket
import threading
import subprocess


SERVER_HOST = 'localhost'
SERVER_PORT = 5050
BUFFER_SIZE = 1024

output = subprocess.check_output('bash -c "compgen -c"', shell=True, stderr=subprocess.STDOUT)
commands = output.decode().splitlines()
commands.append('show_clients')
commands.append('shutdown_server')


PREDEFINED_COMMANDS = ['ls', 'show_clients', 'shutdown_server','date', 'echo','pwd','cd','cal','mkdir','rmdir']

clients = {}
server_shutdown_requested = False
admin_password = 'AdminPass'
admin_client = None
shutdown_event = threading.Event()

def handle_client(client_socket, address):
    print(f"New connection from {address}")
    global admin_client
    is_admin = False

    while not shutdown_event.is_set():
        try:
            command = client_socket.recv(BUFFER_SIZE).decode().strip()
        except ConnectionAbortedError:
            break
        
        if command == admin_password:
            is_admin = True
            admin_client = client_socket
            client_socket.send("Welcome Admin".encode())
            continue

        if not command:
            print(f"Client {address} disconnected")
            if is_admin:
                admin_client = None
            del clients[address]
            break

        print(f"Command from {address}: '{command}'")

        try:
            if command.split()[0].lower() not in commands:
                output = "Error: Invalid command."
            elif command.split()[0].lower() not in PREDEFINED_COMMANDS:
            	 output = "Error: Command not allowed."
            else:
                if is_admin:
                    if command.lower() == 'show_clients':
                        client_socket.send(f"{len(clients)} Connected client(s):\n".encode() + "\n".join(str(addr) for addr in clients).encode())
                        continue

                    if command.lower() == 'shutdown_server':
                        print("Shutting down server...")
                        shutdown_event.set()
                        break
                output = "Output: "+subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10).decode()
            
        except subprocess.CalledProcessError:
            output = "Error: Invalid Command"
        except subprocess.TimeoutExpired:
            output = "Error: Command execution timed out."

        client_socket.send(output.encode())

    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    client_thread = threading.Thread(target=handle_client_connections, args=(server_socket,))
    client_thread.start()

    while not shutdown_event.is_set():
        pass

    server_socket.close()

def handle_client_connections(server_socket):
    while not shutdown_event.is_set():
        try:
            client_socket, address = server_socket.accept()
            clients[address] = client_socket
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()
        except OSError as e:
            if shutdown_event.is_set():
                break
            else:
                raise e

    for client_socket in clients.values():
        client_socket.close()

if __name__ == "__main__":
    start_server()
