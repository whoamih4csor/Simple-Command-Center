import CommandCenter
import argparse
import sys
import time


def error(message):
    print('Falta el modo de ejecucion terminal o graphic')
    print(parser.usage)
    exit(1)
def mi_ayuda():
    print('\n')
    print(f'uso {__file__} [-h] -m MODO [-a DIRECCION] [-p PUERTO]')
    print(parser.description)
    print('\nopciones:')
    print('-h, --help      : Para mostar el panel de ayuda')
    print('-a DIRECCION, --direccion DIRECCION : Aqui va tu IP')
    print('-p PUERTO,    --puerto PUERTO : Aqui va tu PUERTO')
    print('-m MODO,      --modo MODO : Hay dos modos grafico y terminal')
    print('\n')
#create certs
#openssl req -nodes -x509 -newkey rsa:4096 -keyout server.key -out server.cer -days 356

# Create the parser
parser = argparse.ArgumentParser(
                    prog = sys.argv[0],
                    description = 'Este Programa Es un centro de comandos para recibir conexiones de clientes y enviarles comandos',
                    usage=f'{__file__} [-h] -m MODO [-a DIRECCION] [-p PUERTO]',
                    )

parser.error = error
parser.print_help = mi_ayuda
# Add an argument
parser.add_argument('-m','--modo',required=True)
parser.add_argument('-a','--direccion')
parser.add_argument('-p','--puerto')

# Parse the argument
args = parser.parse_args()

#to test without flags
#args.port = '4747'
#args.address = '192.168.0.10'
#args.mode = 'graphic'

if not args.direccion == None and not args.puerto== None:
    app = CommandCenter.Command_Center(args.direccion,args.puerto,args.modo)
else:
    app = CommandCenter.Command_Center(None,None,args.modo)


if args.modo == 'terminal':
    app.start_server()
    time.sleep(1) 
    app.start_terminal()
elif args.modo == 'grafico':
    app.Graphic_Interface()
else:
    parser.print_help()

