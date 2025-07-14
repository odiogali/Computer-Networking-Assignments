import socket
import threading
import logging
from collections import Counter 
import errno

# Set up basic logging configuration
logging.basicConfig(filename='server_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Constants for the server configuration
HOST = 'localhost'
PORT = 6969

activeThreads = [] # list of active threads for ease of management

def recv_full(client_socket, delimiter ="\r\n"):
    """Handles receiving errors and continues receiving until ending sequence is found""" 
    try:
        buffer = ""
        while True:
            request_data = client_socket.recv(1024).decode()
            if not request_data:  # Client has closed the connection
                return None
            buffer += request_data # Add received data to the buffer
            if delimiter in request_data: # Once delimiter is seen, we can stop receiving
                break

        return buffer.split(delimiter)[0] # Remove delimiter and return it
    except socket.timeout:
        logging.error(f"Connection timed out on {HOST}:{PORT}") # Log timeout error if it occurs

def handle_client(client_socket, client_address):
    """ Handle incoming client requests. """
    logging.info(f"Connection from {client_address}")
    
    try:
        while True:
            # Receive data from the client
            request_data = recv_full(client_socket)
            if not request_data:  # Client has closed the connection
                break

            logging.info(f"Received request: {request_data}")
            
            # Here, the request is processed to determine the response
            response = process_request(request_data)
            try:
                client_socket.sendall(response.encode())
            except UnicodeEncodeError:
                logging.error(f"Encode error: Unable to encode the string '{response}' into UTF-8")
                break # if there was an issue sending, close the connection
            except Exception as e:
                logging.error(f"Send error: {e}")
                break # if there was an issue sending, close the connection

            logging.info(f"Sent response: {response}")
    except ConnectionResetError:
        logging.error(f"Connection reset by {HOST}")
    finally:
        # Close the client connection
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        logging.info(f"Closed connection with {client_address}")

def process_request(request_data):
    """ Process the client's request and generate a response. """
    try:
        # Students need to parse the request and call the appropriate palindrome function
        check_type, input_string = request_data.split('|')
        input_string = ''.join(e for e in input_string if e.isalnum()).lower()
        
        if check_type == 'simple':
            result = is_palindrome(input_string)
            return f"Is palindrome: {result}\r\n"
        elif check_type == 'complex':
            is_complex, swaps = complex_palindrome(input_string)
            return f"Can form a palindrome: {is_complex}\nComplexity score: {swaps} (number of swaps)\r\n"
        else: # There is some sort of error with the received request
            logging.info(f"Invalid client request type: {check_type}")
    except Exception as e:
        return f"Received possibly malformed data: {e}"

    return ""

def is_palindrome(input_string):
    """ Check if the given string is a palindrome. """
    return input_string == input_string[::-1]

def complex_palindrome(input_string):
    """Check if given string could be rearranged to form a palindrome, and how many swaps it would take"""
    occurences = {} # Hashmap for counting occurences of each letter

    # Count the occurences
    for c in input_string:
        if not occurences.get(c):
            occurences[c] = 1
        else:
            occurences[c] += 1

    oddOccurence = '#' # Store which character is the one that occurs an odd number of times
    oddOccurs = 0 # How many times a character occurs an odd number of times

    # Go through map, to find the odd occuring character and if there are more than one
    for c in occurences:
        if occurences[c] % 2 != 0: # if odd...
            oddOccurs += 1
            oddOccurence = c

        # If there is more than one character that appears an odd # of times, return False because we cannot
        # form a palindrome from a string with more than one character that appears an odd number of times
        if oddOccurs > 1: 
            return (False, 0)

    # By this point, it is guaranteed that input_string is a complex palindrome
    swaps = 0
    input_list = list(input_string)
    left, right = 0, len(input_list) - 1

    # First, swap the odd occurence with the middle character if string has odd number of characters
    if len(input_list) % 2 != 0:
        midIdx = len(input_list) // 2
        for i, c in enumerate(input_list):
            if c == oddOccurence:
                if i == midIdx: break
                input_list[midIdx], input_list[i] = input_list[i], input_list[midIdx]
                swaps += 1
                break

    # Go through the list, attempting to mirror the ends of the string, moving inward
    while left < right:
        if input_list[left] != input_list[right]: # If characters at the ends are not equal, search the inner list for their mirror
            for i in range(left + 1, right):
                if input_list[i] == input_list[right]:
                    input_list[i], input_list[left] = input_list[left], input_list[i]
                    swaps += 1
                    break

        left += 1 # Update the pointers until we get to the middle of the list
        right -= 1

    return (True, swaps)

def start_server():
    """ Start the server and listen for incoming connections. """
    global activeThreads

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to allow ports to be reused immediately
            server_socket.bind((HOST, PORT)) # Bind this program to this IP and PORT
            server_socket.listen(5) # Allow 5 devices to be in the backlog
            logging.info(f"Server started and listening on {HOST}:{PORT}")
            
            while True:
                # Accept new client connections and start a thread for each client
                client_socket, client_address = server_socket.accept()
                client_socket.settimeout(30) # To prevent hanging, connection with client should be removed after 30 secs
                thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                thread.daemon = True 
                thread.start()

                activeThreads.append(thread) # Add new thread to list of active threads
                # Filter list of active threads according to whether they are still alive
                activeThreads = list(filter(lambda t: t.is_alive(), activeThreads)) 
    except socket.gaierror as e:
        logging.error(f"Address resolution error: {e.strerror}")
    except ConnectionRefusedError:
        logging.error(f"Connection refused on {HOST}:{PORT}")
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logging.error(f"OS Error: Port {PORT} is already in use.")
        elif e.errno == errno.EADDRNOTAVAIL:
            logging.error(f"OS Error: IP address {HOST} is not available on this machine.")
        elif e.errno == errno.EACCES:
            logging.error(f"OS Error: Permission denied for port {PORT}.")
        else:
            logging.error(f"Unexpected OS error: {e.strerror}")
    except KeyboardInterrupt:
        print("\nTerminating the server connection...")
        shutdownServer()
    except Exception as e:
        logging.error(f"Unexpected error encountered: {e}")

def shutdownServer():
    logging.info(f"Beginning shutdown process for {HOST}:{PORT}...")

    for thread in activeThreads:
        thread.join() # Join back to the main process

    logging.info(f"Shutdown process for {HOST}:{PORT} has been completed cleanly.")

if __name__ == '__main__':
    start_server()
