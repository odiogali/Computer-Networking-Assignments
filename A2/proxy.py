import socket
import threading
from urllib.parse import urlparse
import errno
import os, random, mimetypes

HOST = "127.0.0.1"
DELAY = 1.0
PORT = 8080
CHUNK_SIZE = 1024
# Due to the separate threads, we need to have a system for which thread can access the image counter
image_counter_lock = threading.Lock() 
image_counter = 0

activeThreads = []

def recv_http_request(sock):
    """Receive function for an arbitrary HTTP request so we can get all of it"""
    data = b""
    try:
        while True:
            chunk = sock.recv(CHUNK_SIZE)
            if not chunk:
                break
            data += chunk
            if len(chunk) < CHUNK_SIZE:
                # If we received less than a full buffer, likely we're done
                break
    except socket.error as e:
        print(f"Error receiving data: {e}")
    print(data)
    return data

def is_https_request(request):
    """Check if the request is an HTTPS CONNECT request"""
    request_lines = request.split(b'\r\n')
    if not request_lines:
        return False

    first_line = request_lines[0].decode('utf-8', errors='ignore')
    method = first_line.split(' ')[0].upper()

    return method == "CONNECT"

def handle_https_request(request):
    """Generates and returns response for HTTPS request"""
    # Extract the target host and port from the CONNECT request
    request_line = request.split(b'\r\n')[0].decode('utf-8')
    target = request_line.split(' ')[1]
    host, port = target.split(':')
    port = int(port)

    print(f"HTTPS connection request detected to {host}:{port}")

    response = b"HTTP/1.1 501 Not Implemented\r\n"
    response += b"Content-Type: text/plain\r\n"
    response += b"Connection: close\r\n\r\n"
    response += b"This proxy does not support HTTPS connections. Please use HTTP only."

    return response

def recv_http_response(sock):
    """Receive function to ensure we receive the entire response (headers + body)"""
    # Read header data into byte buffer
    headers_data = b""
    while b"\r\n\r\n" not in headers_data:
        chunk = sock.recv(CHUNK_SIZE)
        if not chunk:
            return headers_data
        headers_data += chunk

    # Store the index of where the header ends (because we may have read some of the body as well) 
    header_end = headers_data.find(b"\r\n\r\n") + 4 # +4 tells us where the end of the headers is
    headers = headers_data[:header_end] # Separate headers and first part of body
    body = headers_data[header_end:]

    # Parse headers to find Content-Length or Transfer-Encoding
    header_lines = headers.split(b"\r\n")
    content_length = 0
    chunked = False

    for line in header_lines:
        if b"content-length:" in line.lower():
            content_length = int(line.split(b":", 1)[1].strip())
        elif line.lower().startswith(b"transfer-encoding:") and b"chunked" in line.lower():
            chunked = True

    # Handle remote response based on the way the body is encoded
    if chunked:
        print("Proxy does not offer support for chunked encoding.")
        return None
    elif content_length:
        current_length = len(body)
        
        # Continue receiving until the current amount of bytes that has been read is == content-length
        while current_length < content_length:
            chunk = sock.recv(CHUNK_SIZE)
            if not chunk:
                break # Connection closed early
            body += chunk
            current_length += len(chunk)
    else: # No content length or chunked encoding so we read until connection closes
        while True:
            chunk = sock.recv(CHUNK_SIZE)
            if not chunk:
                break
            body += chunk

    return headers + body

def should_replace_this_image():
    """Thread-safe function to determine if we should replace the current image"""
    global image_counter
    with image_counter_lock:
        should_replace = (image_counter % 2 == 0) # Replace every 2 image requests (50% of them)
        image_counter += 1
        print(f"Image counter: {image_counter}, replacing: {should_replace}")
        return should_replace

def is_image_request(request):
    """Check if the request is for an image"""
    # Extract URL from request
    request_lines = request.split(b"\r\n")
    if not request_lines:
        return False

    first_line = request_lines[0].decode('utf-8', errors='ignore')
    parts = first_line.split(' ')
    if len(parts) < 2:
        return False

    # Function just checks if the request url ends with any of the below filetypes
    url = parts[1]
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def is_google_request(request):
    """Check if the request is for google.com or google.ca"""
    request_lines = request.split(b'\r\n')
    if not request_lines:
        return False

    # Check first line for URL
    first_line = request_lines[0].decode('utf-8', errors='ignore')
    parts = first_line.split(' ')
    if len(parts) < 2:
        return False

    url = parts[1]

    if url.startswith("http://"):
        parsed_url = urlparse(url)
        host = parsed_url.netloc
    else:
        # Check Host header
        host = None
        for line in request_lines[1:]:
            line_str = line.decode('utf-8', errors='ignore')
            if line_str.lower().startswith('host:'):
                host = line_str.split(':', 1)[1].strip()
                break

    if host:
        return host.lower() in ['www.google.com', 'google.com', 'www.google.ca', 'google.ca']

    return False

def create_image_response(meme_path):
    """Create an HTTP response with the meme image"""
    # Read the meme file
    with open(meme_path, 'rb') as f:
        image_data = f.read()

    # Determine content type
    content_type = mimetypes.guess_type(meme_path)[0] or 'image/jpeg'
    print(f"Content-type: {content_type} for the following meme path: {meme_path}")

    # Build HTTP response
    response = []
    response.append(b"HTTP/1.1 200 OK")
    response.append(f"Content-Type: {content_type}".encode()) # .encode turns the string into byte
    response.append(f"Content-Length: {len(image_data)}".encode())
    response.append(b"Connection: close")
    response.append(b"")  # Empty line to separate headers from body

    # Combine headers and body
    full_response = b'\r\n'.join(response) + b'\r\n' + image_data
    return full_response # return bytes for handle_client to send

def get_random_meme():
    """Get a random meme file path from the Memes directory"""
    return os.getcwd() + "/Memes/" + random.choice(os.listdir(os.getcwd()+"/Memes"))        

def forward_request(request, host = "", port = 0):
    """Alters and sends request to server specified in Host"""
    try:
        if b"\r\n\r\n" in request:
            headers_part, body_part = request.split(b"\r\n\r\n", 1)
        else:
            headers_part = request
            body_part = b""

        header_lines = headers_part.split(b"\r\n")

        # Parse request searching for where to forward the request
        first_line = header_lines[0]
        url = first_line.split(b' ')[1]
        parsed_url = urlparse(url.decode('utf-8'))

        host = parsed_url.hostname # We get hostname from parsed url as well as the path
        path = parsed_url.path + "?" + parsed_url.query if parsed_url.query else parsed_url.path
        if not path: # If path is null, we just get the root of the webpage
            path = "/"

        # Port is 80 by default unless otherwise specified 
        port = parsed_url.port if parsed_url.port else 80

        # Proxy needs to alter the first line slightly before forwarding
        modified_headers = []
        modified_headers.append(first_line.split(b" ")[0] + b" " + path.encode() + b" " + first_line.split(b" ")[2])

        has_host = False
        has_content_length = False

        for line in header_lines[1:]:
            if line.startswith(b"Host:"):
                has_host = True
                modified_headers.append(line)
            elif line.startswith(b"Content-Length:"):
                has_content_length = True
                if body_part:
                    modified_headers.append(f"Content-Length: {len(body_part)}".encode())
                else:
                    modified_headers.append(line)
            elif line.startswith(b"Transfer-Encoding:") and b'chunked' in line:
                continue # do not add this header to new headers
            else: # For any other headers, simply append them
                modified_headers.append(line)

        if not has_host: # If there is no host specified
            print("Unable to find a host to forward the request to.")
            return None

        if not has_content_length and body_part:
            content_length_header = f"Content-Length: {len(body_part)}".encode()
            modified_headers.append(content_length_header)
        elif not has_content_length and not body_part:
            modified_headers.append(b"Content-Length: 0")

        modified_request = b"\r\n".join(modified_headers) + b"\r\n\r\n" + body_part

        if not port or port <= 0:
            print(f"Error regarding the host: {host} or port: {port}")
            print(f"Host : {host}, Port: {port}")
            return None  

        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((host, port))
        remote_socket.sendall(modified_request)
        print(f"Client request forwarded to remote server: {host}")

        return remote_socket
    except IndexError:
        print("Malformed HTTP request: Missing first line.")
    except ValueError:
        print("Invalid URL in request.")
    except socket.gaierror:
        print(f"DNS resolution failed for host: {host}.")
    except socket.timeout:
        print(f"Connection to {host}:{port} timed out.")
    except socket.error as e:
        print(f"Socket error encountered while forwarding request: {e}.")

    return None

def handle_client(client_socket, client_address):
    """Main functionality of proxy when a client has just connected"""
    # Receive request from client
    print("Receiving client request...")
    request = recv_http_request(client_socket)
    if not request:
        print("Received null request from client.")
        client_socket.close()
        return

    if is_https_request(request):
        response = handle_https_request(request)
        client_socket.sendall(response)
        print(f"Server cannot handle {client_address}'s HTTPS request.")
        client_socket.close()
        return 

    if is_google_request(request):
        print("Google request detected, replacing with meme...")
        meme_path = get_random_meme()
        print(f"Meme selected: {meme_path}")

        if meme_path and os.path.exists(meme_path):
            response = create_image_response(meme_path)
            if response:
                print(f"Sending meme image response instead of Google.")
                client_socket.sendall(response)
                client_socket.close()
                return
        else: 
            print(f"Meme file not found or invalid: {meme_path}.")

    # Received request is either image request or not
    if is_image_request(request) and should_replace_this_image():
        print("Detected image request, replacing with meme...")
        meme_path = get_random_meme()
        print(f"Meme selected: {meme_path}")

        if meme_path and os.path.exists(meme_path):
            response = create_image_response(meme_path)
            if response:
                print(f"Sending meme image response: {meme_path}.")
                client_socket.sendall(response)
                client_socket.close()
                return
        else: 
            print(f"Meme file not found or invalid: {meme_path}.")
            return

    print(f"Forwarding request from {client_address} to remote server...")
    remote_socket = forward_request(request)
    if not remote_socket:
        print("Failed to establish connection with remote server.")
        client_socket.close()
        return

    # Receive response from remote server
    print("Receiving response from remote server...")
    response = recv_http_response(remote_socket)
    if not response:
        print("Received null response from remote server")
        remote_socket.close()
        client_socket.close()
        return

    # Forward the response back to the client
    print("Sending response back to client...")
    client_socket.sendall(response)
    print("Response sent to client successfully")
    
    # Clean up sockets
    remote_socket.close()
    client_socket.close()
    print(f"Connection closed with {client_address}.\n")

def start_proxy():
    global activeThreads

    p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    p_socket.bind((HOST, PORT))
    p_socket.listen(5) # 5 connections can be held in queue
    print(f"Proxy listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = p_socket.accept()
            print(f"Connection accepted from {addr}.")
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            activeThreads.append(thread)
            thread.start()
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
    except KeyboardInterrupt:
        print("\nTerminating the server connection...")
        end_proxy()
    finally:
        p_socket.shutdown(socket.SHUT_RDWR)
        p_socket.close()

def end_proxy():
    print(f"Beginning shutdown process for {HOST}:{PORT}...")

    for thread in activeThreads:
        thread.join() # Join back to main process

    print(f"Shutdown process for {HOST}:{PORT} has been successfully completed.")

if __name__ == "__main__":
    start_proxy()
