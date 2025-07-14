# Assignment 2: Meme-Generating Proxy

**Author**: Odi Ogali, 30172645

This is a simple HTTP proxy server written in Python that intercepts web traffic and has two special features:
1. It replaces every other image request with a random meme from a local directory
2. It replaces all HTTP requests to Google domains (google.com and google.ca) with random memes

## Prerequisites

- Python 3.6 or higher
- A collection of meme images for replacement in the working directory of the server titled "Memes"
- Basic understanding of HTTP proxies

## Setup

1. Clone or download this repository to your local machine.

2. Create a `Memes` directory in the same folder as the proxy script:
   ```
   mkdir Memes
   ```

3. Add your meme images to the `Memes` directory. Supported formats include JPG, JPEG, PNG, GIF, WebP, and SVG.
   ```
   cp /path/to/your/memes/*.jpg Memes/
   ```

## Configuration

The default configuration uses:
- **Host**: 127.0.0.1 (localhost)
- **Port**: 8080

You can modify these settings by editing the following variables at the top of the script:
```python
HOST = "127.0.0.1"
PORT = 8080
```

## Running the Server

1. Open a terminal and navigate to the directory containing the proxy script.

2. Run the script:
   ```
   python proxy.py
   ```

3. The server will start and display a message:
   ```
   Proxy listening on 127.0.0.1:8080...
   ```
   
4. To stop the server, press `Ctrl+C` in the terminal.

## Configuring Your Browser to Use the Proxy

### Chrome

1. Open Chrome and go to Settings.
2. Search for "proxy" and click on "Open your computer's proxy settings".
3. In Windows:
   - Go to the "Manual proxy setup" section.
   - Enable "Use a proxy server".
   - Set the address to "127.0.0.1" and the port to "8080".
4. In macOS:
   - Select "Web Proxy (HTTP)".
   - Set the server to "127.0.0.1" and the port to "8080".
5. In Linux:
   - The exact steps depend on your desktop environment.
   - Generally, look for "Network Proxy" in the system settings.

### Firefox

1. Open Firefox and go to Settings/Preferences.
2. Scroll down to "Network Settings" and click on "Settings".
3. Select "Manual proxy configuration".
4. Set "HTTP Proxy" to "127.0.0.1" and the port to "8080".
5. Click "OK" to save your settings.

**NOTE**: For most browsers, you will likely need to turn off a setting that changes HTTP requests to HTTPS.

## Testing

1. Make sure the proxy is running.
2. Configure your browser to use the proxy.
3. Visit any HTTP website to verify that the proxy is working.
4. Visit http://www.google.com or http://www.google.ca to verify that the Google meme replacement is working.
5. Visit various websites with images to see the "every other image" meme replacement in action.

## Features

- **HTTP Proxy**: Forwards all HTTP requests to their destinations and returns the responses.
- **Google Replacement**: Replaces any requests to google.com or google.ca with a random meme.
- **Image Replacement**: Replaces every other image request (based on a counter) with a random meme.
- **HTTPS Handling**: The proxy does not support HTTPS connections and will return a 501 Not Implemented error for HTTPS CONNECT requests.

## Limitations

- This proxy only supports HTTP, not HTTPS.
- The proxy does not support chunked encoding in responses.
- The proxy is designed for educational and entertainment purposes and may not handle all HTTP edge cases.

## Troubleshooting

- **Connection Refused Error**: Make sure the proxy is running and the port is not being used by another application.
- **No Memes Showing**: Verify that the `Memes` directory exists and contains image files.
- **Browser Cannot Connect**: Check that your browser's proxy settings are correctly configured.
