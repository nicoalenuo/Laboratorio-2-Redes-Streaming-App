import socket
import threading
import sys

ServerIP = sys.argv[1] #Por ejemplo, 127.0.0.1
ServerPort = int(sys.argv[2]) #Por ejemplo, 2023

SourceIP = '127.0.0.1' #Colocar la IP de donde vendrá el stream de VLC 
SourcePort = 9999

sktStream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Todo esto es lo mismo que en el pseudo-codigo
sktStream.bind((SourceIP, SourcePort))

sktEnvio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sktC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sktC.bind((ServerIP, ServerPort))
sktC.listen()

print("Server abierto") #Para probar que abre :P

clientes = [] #Lista global donde se guardarán los clientes "activos"

# Función para aceptar conexiones TCP
def aceptarConexiones(sktControl):
    while True:
        cliente, _ = sktControl.accept()
        thread = threading.Thread(target = aceptarControl, args=(cliente,))
        thread.start()

# Función para manejar la conexiones de control
def aceptarControl(cliente):
    cliente.settimeout(None)
    desconectar = False
    ipCliente = None
    puertoCliente = None

    while not desconectar:
        try:
            comando = cliente.recv(4096)
            comando = comando.decode('utf-8')

            if comando == 'DESCONECTAR':
                clientes.remove((ipCliente, puertoCliente))
                cliente.close()
                desconectar = True
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", se desconecta")
            elif comando.startswith('CONECTAR'):
                ipCliente = cliente.getpeername()[0]
                _, puertoStr = comando.split(' ') #Si el comando es CONECTAR <puerto>, con split me quedo con la parte de la derecha (el puerto)
                puertoCliente = int(puertoStr)
                clientes.append((ipCliente, puertoCliente))
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", se conecta")
            elif comando == 'INTERRUMPIR':
                clientes.remove((ipCliente, puertoCliente))
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", interrumpe")
            elif comando == 'CONTINUAR':
                clientes.append((ipCliente, puertoCliente))
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", continua")

        except Exception as e:
            print("Error:", e)
            break

# Se inicia el hilo para las conexiones de control
threadControl = threading.Thread(target = aceptarConexiones, args=(sktC,))
threadControl.start()

# Main, desde donde se reenvian todos los datagramas recibidos
while True:
    datagrama, (ip, puerto) = sktStream.recvfrom(16384)
    for clienteIp, clientePuerto in clientes:
        sktEnvio.sendto(datagrama, (clienteIp, clientePuerto))
