import socket

SERVER_HOST = 'localhost'
SERVER_PORT = 5050
BUFFER_SIZE = 1024

def send_command_to_server(command, client_socket):
    try:
        client_socket.send(command.encode())
        output = client_socket.recv(BUFFER_SIZE).decode().rstrip()
        if output.startswith('Error'):
            print(output)
        elif output:
            print(f"{output}")
        else:
            print("Server closed or blank response from server...")
    except Exception as e:
        print(f"Error communicating with server: {str(e)}")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to server (type 'exit' to quit)")
        while True:
            try:
                command = input("Enter command: ")
                if command.lower() == 'exit':
                    break
                send_command_to_server(command, client_socket)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
    except Exception as e:
        print(f"Failed to connect to server: {str(e)}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
