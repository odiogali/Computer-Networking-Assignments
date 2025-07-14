# Chat Application - README

## Introduction
This project is a simple chat application consisting of a server and a client, built using Python's socket and threading modules. The server handles multiple clients, allowing them to communicate in a chatroom-like environment and handling special commands. The client connects to the server, sending and receiving messages.

---

## Compilation and Execution

### Requirements
Ensure you have Python 3 installed on your system.

### Running the Server
1. Open a terminal or command prompt.
2. Navigate to the directory containing the `server.py` file.
3. Run the following command:
   ```sh
   python server.py
   ```
4. The server will start listening for incoming client connections on `127.0.0.1:6969`.

### Running the Client
1. Open a terminal or command prompt.
2. Navigate to the directory containing the `client.py` file.
3. Run the following command:
   ```sh
   python client.py
   ```
4. Enter a unique username when prompted.
5. Start sending messages or special commands to the server.

---

## Example Inputs and Outputs

### Example Session
#### Server Output:
```
Server listening on 127.0.0.1:6969...
Connection from: ('127.0.0.1', 54321)
Connection from: ('127.0.0.1', 54322)
```

#### Client 1 (Alice):
```
Enter your unique username: Alice
> Hello everyone!
> @bamboo
Pandas spend about 14 hours a day eating bamboo.
```

#### Client 2 (Bob):
```
Enter your unique username: Bob
> Hi Alice!
Alice: Hello everyone!🐼
Bob: Hi Alice!🎋
```

### Commands Available:
| Command   | Description |
|-----------|-------------|
| `@leaves` | Disconnects from the server. |
| `@grove`  | Lists all connected clients. |
| `@bamboo` | Returns a random panda fact. |

---

## Assumptions
1. **Unique Usernames:** Each client must enter a unique username. Duplicate usernames are rejected.

2. **Client-Server Model:** The server listens for incoming connections and spawns a new thread for each client.

3. **Message Format:** Messages are structured as `username: message\r\n` to ensure all data is received for large messages.

4. **Encoding:** All messages are encoded in UTF-8 to support Unicode characters, including emojis.

5. **Error Handling:** The server and client handle various socket errors and unexpected disconnections.

6. **Logging:** The server logs all connections, disconnections, and errors in `server_log.txt`.

7. **Graceful Shutdown:** The server properly shuts down all client connections upon exit.

   

## Report

- I decided to go with a more procedural structure for the program as opposed to a functional or object-oriented structure so that the program would be easier to debug
   - In terms of structure though, the code is not much different from in previous assignments: for each function, I only passed in the needed components which was mainly the server/client socket and sometimes the name of the client
- Surprisingly I struggled with handling errors due to the many possible points of error - the threads, the socket connections, prematurely removing entries from the set of clients or not removing clients soon enough
  - My biggest struggle was an error I had that seemed to be coming from me not removing the client from the set of clients right after closing the socket which resulted in me being stuck with a bad descriptor exception for days
- For extra features, I added a user prompt so that the user could more easily see what their messages were and where they were typing, I also added ASCII art as part of the random panda messages you could receive
---

## Troubleshooting
### Problem: Client cannot connect to the server.
- Ensure the server is running before starting the client.
- Check if another process is using port 6969.
- If running on a different machine, update the `HOST` in both files.

### Problem: Messages are not displaying correctly.
- Ensure your terminal supports Unicode.
- Verify that messages are correctly encoded and decoded as UTF-8.

### Problem: Server crashes unexpectedly.
- Check `server_log.txt` for errors.
- Ensure the port is available before running the server.

---

## Conclusion
This chat application demonstrates the use of Python sockets for real-time communication. It includes basic chat functionalities, user management, and interactive commands while handling multiple clients efficiently.

