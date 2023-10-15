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

clientes_lock = threading.Lock()

print("Server abierto") #Para probar que abre :P

clientes = [] #Lista global donde se guardarán los clientes "activos"

#Funcion para enviar respuesta al cliente
#evita repetir codigo
def enviar_cliente(comando, cliente):
    comando = comando.encode()
    total_bytes = len(comando)
    bytes_enviados = 0

    while bytes_enviados < total_bytes:
        try:
            enviados = cliente.send(comando[bytes_enviados:])
            bytes_enviados += enviados
        except socket.error:
            cliente.close()
            break

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
        buffer = b""
        comando = b""
        try:
            while b'\n' not in comando:
                buffer = cliente.recv(1)
                comando += buffer
                #Si se interrumpe el cliente, se cierra el socket por lo que se recibe 0 bytes de informacion, de esta forma
                #se detecta si el cliente cierra de forma inesperada sin usar DESCONECTAR
                if not buffer:
                    raise Exception

            comando = comando.decode('utf-8')
            comando, _ = comando.split('\n', 1)


            if comando.startswith('CONECTAR'):
                ipCliente = cliente.getpeername()[0]
                _, puertoStr = comando.split(' ') #Si el comando es CONECTAR <puerto>, con split me quedo con la parte de la derecha (el puerto)
                puertoCliente = int(puertoStr)
                with clientes_lock:
                    if (ipCliente, puertoCliente) not in clientes:
                        clientes.append((ipCliente, puertoCliente))
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", se conecta")
                enviar_cliente("OK\n", cliente)

            elif comando == 'INTERRUMPIR':
                with clientes_lock:
                    if (ipCliente, puertoCliente) in clientes:
                        clientes.remove((ipCliente, puertoCliente))
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", interrumpe")
                enviar_cliente("OK\n", cliente)

            elif comando == 'CONTINUAR':
                with clientes_lock:
                    if (ipCliente, puertoCliente) not in clientes:
                        clientes.append((ipCliente, puertoCliente))
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", continua")
                enviar_cliente("OK\n", cliente)

            elif comando == 'DESCONECTAR':
                with clientes_lock:
                    if (ipCliente, puertoCliente) in clientes:
                        clientes.remove((ipCliente, puertoCliente))
                desconectar = True
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", se desconecta")
                enviar_cliente("OK\n", cliente)
                cliente.close()

        except Exception:
            cliente.close()
            with clientes_lock:
                if (ipCliente, puertoCliente) in clientes:
                        clientes.remove((ipCliente, puertoCliente))
            print("Quitado " + ipCliente + ":" + str(puertoCliente), ", ocurrió una excepción")
            desconectar = True

# Se inicia el hilo para las conexiones de control
threadControl = threading.Thread(target = aceptarConexiones, args=(sktC,))
threadControl.start()

# Main, desde donde se reenvian todos los datagramas recibidos
while True:
    datagrama, (ip, puerto) = sktStream.recvfrom(16384)
    for clienteIp, clientePuerto in clientes:
        sktEnvio.sendto(datagrama, (clienteIp, clientePuerto))
