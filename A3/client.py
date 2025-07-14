import socket
from threading import Thread
import os
import sys

HOST = '127.0.0.1'
PORT = 6969

def setup():
    """Handles connection of client to server"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize a socket
    
    try:
        client_socket.connect((HOST, PORT)) # connect to server
        client_name = input("Enter your unique username: ") # specify username
        talk_to_server(client_name, client_socket)
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}. Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"Error during setup: {e}")
        client_socket.close()
        sys.exit(1)

def talk_to_server(client_name, client_socket):
    """Send username and initialize two new threads: one for sending, one for receiving"""
    try:
        client_socket.sendall(client_name.encode()) # send client name to server
        Thread(target = receive_message, args=(client_socket, )).start() # start thread for receiving
        send_message(client_name, client_socket) # Repeatedly listen for user input and send it
    except KeyboardInterrupt:
        # When keyboard interrupt happens, server should react as if @leaves was sent
        client_socket.sendall((client_name + ": @leaves\r\n").encode())
        sys.exit(0)
    except Exception as e:
        print(f"Error in talk_to_server: {e}")
        client_socket.close()
        sys.exit(1)

def receive_message(client_socket):
    """Listen and show server messages"""
    server_message = ""
    try:
        while True:
            server_message = client_socket.recv(1024).decode()

            # If received nothing, should terminate
            if not server_message.strip():
                print("\nConnection closed.")
                client_socket.close()
                os._exit(0)

            if "\r\n" not in server_message: # If delimiter not in message, keep receiving
                continue

            print("\r" + server_message.split("\r\n")[0])
            sys.stdout.flush()
            print("> ", end="", flush=True)  # Reprint prompt on same line
    except socket.timeout:
        print("Connection timed out.")
    except ConnectionResetError:
        print("\nConnection reset by server. Server may have shut down.")
    except Exception as e:
        print(f"Error receiving data: {e}")

def send_message(client_name, client_socket):
    """Listen for client input and send message to server"""
    while True:
        try:
                client_input = input("> ")
                client_message = client_name + ": " + client_input + "\r\n"
                client_socket.sendall(client_message.encode())
        except UnicodeEncodeError:
            print("Unable to encode the string. Try again.")

if __name__ == "__main__":
    setup()
