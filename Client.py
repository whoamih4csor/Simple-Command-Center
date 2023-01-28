import socket
persist = False
s = ''

def ConnectServer():
    global s
    s = socket.socket()
    while True:
        try:
            s.connect(('127.0.0.1',4747))
            break
        except:
            pass

ConnectServer()

while True:
    command = s.recv(1024)
    if command:
        command = command.decode()
        if command == 'ok':
            s.sendall(b'Connection Established')
        if command == 'terminate':
            s.sendall(b'Closing Connection')
            s.close()
            break
    elif persist == True:
        ConnectServer()
    else:
        s.close()
        break
