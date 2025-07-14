# Palindrome Server

This project implements a multi-threaded server and a client for checking if a given string is a palindrome. It supports two types of palindrome checks: 
- **Simple Check**: Determines if a string is a palindrome as-is.
- **Complex Check**: Determines if a string can be rearranged into a palindrome and calculates the number of swaps required.

## Compilation & Execution

### Running the Server

1. Ensure Python 3 is installed on your system.
2. Save the server code as `server.py`.
3. Open a terminal and navigate to the directory where `server.py` is saved.
4. Run the server using:
   ```bash
   python server.py
   ```

The server will start listening on `localhost:6969`.

### Running the Client

1. Save the client code as `client.py`.
2. Open a new terminal and navigate to the directory where `client.py` is saved.
3. Run the client using:
   ```bash
   python client.py
   ```
4. Follow the on-screen menu to interact with the server:
   ```
   1. Simple Palindrome Check
   2. Complex Palindrome Check
   3. Exit
   ```
   Example:
   ```
   Enter choice (1/2/3): 1
   Enter the string to check: racecar
   Server response: Is palindrome: True
   ```

## Example Inputs and Outputs

### Example 1 (Simple Palindrome Check)
#### Input:
```
1
racecar
```
#### Output:
```
Server response: Is palindrome: True
```

### Example 2 (Complex Palindrome Check)
#### Input:
```
2
aabbccdd
```
#### Output:
```
Server response: Can form a palindrome: True
Complexity score: 2 (number of swaps)
```

### Example 3 (Non-Palindromic Input)
#### Input:
```
1
hello
```
#### Output:
```
Server response: Is palindrome: False
```

## Assumptions and Limitations

- The server only accepts ASCII alphanumeric characters.
- The delimiter `|` must be used to separate the request type and the input string.
- The input string is case-insensitive, and special characters are ignored.
- The server handles multiple concurrent connections using threads.
- The client retries connecting to the server up to 5 times with a 2-second delay between attempts.
- The maximum allowed length of an input string is subject to system memory constraints.
- The server logs client requests and responses to `server_log.txt`.

## Logging

- All server interactions are logged in `server_log.txt`, including connections, received requests, and sent responses.
- Errors such as encoding issues, malformed requests, and unexpected disconnections are also logged.

## Termination

- To stop the server, use `CTRL+C` in the terminal running the server.
- The server ensures proper thread cleanup before shutting down.
- The client can be terminated by selecting option `3` or pressing `CTRL+C`.

## Dependencies

- Python 3.0
- Standard Python libraries (`socket`, `threading`, `logging`, `time`, `collections`, `errno`)

## Author

- Created by Odi Ogali

