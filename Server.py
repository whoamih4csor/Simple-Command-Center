import CommandCenter
import argparse
import sys
import time

#create certs
#openssl req -nodes -x509 -newkey rsa:4096 -keyout server.key -out server.cer -days 356

# Create the parser
parser = argparse.ArgumentParser(
                    prog = sys.argv[0],
                    description = 'receives connections from Clients to send remote commands to them')
# Add an argument
parser.add_argument('-m','--mode',help='there are two graphic or terminal modes',required=True)
parser.add_argument('-a','--address')
parser.add_argument('-p','--port')

# Parse the argument
args = parser.parse_args()

#to test without flags
#args.port = '4747'
#args.address = '192.168.0.10'
#args.mode = 'graphic'

if not args.address == None and not args.port == None:
    app = CommandCenter.Command_Center(args.address,args.port,args.mode)
else:
    app = CommandCenter.Command_Center(None,None,args.mode)


if args.mode == 'terminal':
    app.start_server()
    time.sleep(1) 
    app.start_terminal()
elif args.mode == 'graphic':
    app.Graphic_Interface()
else:
    parser.print_help()

