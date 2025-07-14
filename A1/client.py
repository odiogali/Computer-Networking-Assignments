import socket
import time

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 6969

def recv_full(client_socket, delimiter="\r\n"):
    """Receive full message from server until delimiter is encountered."""
    buffer = ""
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                return None # Server has disconnected
            buffer += data # Add received data to buffer
            if delimiter in data: # Once delimiter is found, stop receiving
                break
        return buffer.split(delimiter)[0]
    except socket.timeout:
        print("Connection timed out.")
        return None
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None

def send_message(client_socket, message):
    """Send a message to the server with error handling."""
    try:
        client_socket.sendall((message + "\r\n").encode())
    except UnicodeEncodeError:
        print("Unable to encode the string. Try again.")
        return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
    return True

def handle_choice(choice, client_socket):
    """Handle user choice and interact with the server."""
    if choice == '3':
        print("Exiting the client...")
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        return False

    if choice in {'1', '2'}:
        input_string = input("Enter the string to check: ").strip()
        message_type = "simple" if choice == '1' else "complex"

        send_message(client_socket, f"{message_type}|{input_string}")
        response = recv_full(client_socket)

        if response:
            print(f"Server response: {response}")
        else:
            print("Server has disconnected.")
            return False
    else:
        print("Invalid option selected. Please try again.")
    
    return True

def connect_and_handle_client(client_socket):
    """Manage the client interaction loop."""
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        while True:
            print("\nMenu:")
            print("1. Simple Palindrome Check")
            print("2. Complex Palindrome Check")
            print("3. Exit")

            choice = input("Enter choice (1/2/3): ").strip()
            if not handle_choice(choice, client_socket):
                break
    except ConnectionRefusedError:
        print("Server is not available. Connection refused.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def start_client(host, port, retries=5, delay=2):
    """Attempt to connect to the server with retry logic."""
    for attempt in range(1, retries + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(5)
                print(f"Attempt {attempt}: Connecting to {host}:{port}...")
                connect_and_handle_client(client_socket)
                return
        except (socket.timeout, ConnectionRefusedError):
            print(f"Attempt {attempt}: Server {host}:{port} is not responding.")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed. Server is unreachable.")

if __name__ == "__main__":
    try:
        start_client(SERVER_HOST, SERVER_PORT)
    except KeyboardInterrupt:
        print("\nClient terminated by user.")
