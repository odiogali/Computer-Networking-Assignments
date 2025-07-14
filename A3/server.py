import socket
from threading import Thread
import random
import logging
import errno
import sys

Clients = {}
HOST = '127.0.0.1'
PORT = 6969

# Set up basic logging configuration
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

PANDA_EMOJIS = ["🐼","🎋", "⛩️", "🏯"]
PANDA_FACTS = [
    "Pandas spend about 14 hours a day eating bamboo.",
    "A panda's diet is 99% bamboo, but they can eat meat and other plants occasionally.",
    "Newborn pandas are pink, blind, and weigh only about 100 grams.",
    "Despite their large size, pandas are excellent climbers and can climb trees to escape predators.",
    "Pandas have a special 'thumb'—an extended wrist bone—that helps them grasp bamboo.",
    "A panda can eat up to 38 kg (84 lbs) of bamboo in a single day.",
    "Unlike most bears, pandas do not hibernate due to their bamboo diet providing low energy.",
    "Wild pandas are found only in a few mountain ranges in central China.",
    "Pandas communicate through vocalizations and scent markings.",
    "A group of pandas is called an 'embarrassment' or a 'cupboard' of pandas.",
    """
⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣿⡿⠗⠀⠠⠄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠀⠀⠀⠀⠈⠑⢶⣶⡄
⢀⣶⣦⣸⠀⢼⣟⡇⠀⠀⢀⣀⠀⠘⡿⠃
⠀⢿⣿⣿⣄⠒⠀⠠⢶⡂⢫⣿⢇⢀⠃⠀
⠀⠈⠻⣿⣿⣿⣶⣤⣀⣀⣀⣂⡠⠊⠀⠀
⠀⠀⠀⠃⠀⠀⠉⠙⠛⠿⣿⣿⣧⠀⠀⠀
⠀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⡇⠀⠀
⠀⠀⠀⣷⣄⡀⠀⠀⠀⢀⣴⡟⠿⠃⠀⠀
⠀⠀⠀⢻⣿⣿⠉⠉⢹⣿⣿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠁⠀⠀⠀⠉⠁⠀⠀⠀⠀⠀
    """
]

def setup():
    """Start the socket, and begin listening for connections"""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # set relevant sock options

        server_socket.bind((HOST, PORT)) # bind socket to process
        server_socket.listen(5) # Max amount of connections
        print(f"Server listening on {HOST}:{PORT}...")
        logging.info(f"Listening on {HOST}:{PORT}...")

        listen(server_socket)
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def shutdown(server_socket):
    """Properly shutdown the server and all connected clients"""
    print("\nShutting down the server...")

    # Close all active client connections
    for client_name, client_socket in list(Clients.items()):
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

        print(f"Closed connection with {client_name}.")
        logging.info(f"Closed connection with {client_name}.")
    
    Clients.clear()  # remove all clients from dict

    # Close the server socket
    server_socket.close()

    print("Server shut down successfully.")
    logging.info("Server socket closed successfully.")
    sys.exit(0)  # Exit the program

def listen(server_socket):
    """Listen for new client connections on main thread if valid, handle the client in a new thread"""
    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connection from: " + str(client_addr))
            logging.info("Connection received from: " + str(client_addr))

            # First message from client will be their username
            client_name = client_socket.recv(1024).decode()

            # If name is not unique, then stop the connection
            if client_name in Clients:
                client_socket.sendall(("Duplicate username! Try a different one!\r\n").encode())
                client_socket.close()

                print("Closed connection with: " + str(client_addr) + " due to duplicate username.")
                logging.info("Closed connection with: " + str(client_addr) + " due to duplicate username.")
                continue

            Clients[client_name] = client_socket # add name, socket pair to map of clients

            logging.info(f"{str(client_addr)} has selected the name {client_name}.")

            # Notify everyone connected that someone new has entered the chat
            broadcast_message(client_name, client_name + " has joined the chat!\r\n")

            # Start new thread to handle new client
            Thread(target = handle_new_client, args = (client_name, client_socket)).start()
    except socket.gaierror as e:
        print(f"Address resolution error: {e.strerror}")
    except ConnectionRefusedError:
        print(f"Connection refused on {HOST}:{PORT}")
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print(f"OS Error: Port {PORT} is already in use.")
        elif e.errno == errno.EADDRNOTAVAIL:
            print(f"OS Error: IP address {HOST} is not available on this machine.")
        elif e.errno == errno.EACCES:
            print(f"OS Error: Permission denied for port {PORT}.")
        else:
            print(f"Unexpected OS error: {e.strerror}")
    except KeyboardInterrupt: # if ctrl+c is hit, shutdown the server
        shutdown(server_socket)
    except Exception as e:
        print(f"Unexpected error in listen: {e}")

def broadcast_message(skip_client, message):
    """Send a message to all clients except the sender"""
    for client_name, client_socket in list(Clients.items()):
        if client_name != skip_client:
            client_socket.sendall(message.encode())

def handle_new_client(client_name, client_socket):
    """Handle message received from the client"""
    while True:
        client_message = client_socket.recv(1024).decode() # repeatedly read client messages

        # If we receive nothing, the connection has been/in process of closing
        if not client_message.strip():
            Clients.pop(client_name, None) # make sure client is removed from set of clients
            return

        # Handle commands if they are in the message
        if client_message.strip() == client_name + ": @leaves":
            Clients.pop(client_name, None) # First remove client from list of clients
            broadcast_message(client_name, client_name + " has left the chat!\r\n")
            client_socket.close()
            return
        elif client_message.strip() == client_name + ": @grove":
            pandas = []
            for key in Clients.keys():
                pandas.append(key)
            message = "List of connected pandas: " + str(pandas) + "\r\n"
            client_socket.sendall(message.encode())
        elif client_message.strip() == client_name + ": @bamboo":
            response = random.choice(PANDA_FACTS) + random.choice(PANDA_EMOJIS) + "\r\n"
            client_socket.sendall(response.encode())
        else: # Otherwise, broadcast client's message to other members
            broadcast_message(client_name, client_message.split("\r\n")[0] + " " + random.choice(PANDA_EMOJIS) + "\r\n")

if __name__ == "__main__":
    setup()
