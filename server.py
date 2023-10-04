import socket
import threading
import sys
import time

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

                with clientes_lock:
                    clientes.remove((ipCliente, puertoCliente))
                cliente.close()
                desconectar = True
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", se desconecta")

            elif comando.startswith('CONECTAR'):
                
                ipCliente = cliente.getpeername()[0]
                _, puertoStr = comando.split(' ') #Si el comando es CONECTAR <puerto>, con split me quedo con la parte de la derecha (el puerto)
                puertoCliente = int(puertoStr)

                with clientes_lock:
                    clientes.append((ipCliente, puertoCliente))
                    with condicionManejador:
                        condicionManejador.notify() #Lo pongo dentro de clientes_lock para garantizar que nadie modifico clientes[]
                    with condicionCliente:
                        condicionCliente.wait() #Espero a sincronizarme con el hilo manejador.
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", se conecta")
                
            elif comando == 'INTERRUMPIR':

                with clientes_lock:
                    clientes.remove((ipCliente, puertoCliente))
                print("Quitado " + ipCliente + ":" + str(puertoCliente), ", interrumpe")

            elif comando == 'CONTINUAR':

                with clientes_lock:
                    clientes.append((ipCliente, puertoCliente))
                print("Agregado " + ipCliente + ":" + str(puertoCliente), ", continua")

        except Exception as e:
            print("Error:", e)
            break

# Función para manejar un grupo de clientes
def enviarStreamClientes(limInf):
    while True:
        datagrama, _ = sktStream.recvfrom(16384)
        i = limInf
        while i < len(clientes) and i < i+2: #Mando desde la posicion i hasta i+10, cada hilo envia a 10 clientes
            clienteIp, clientePuerto = clientes[i]
            sktEnvio.sendto(datagrama, (clienteIp, clientePuerto))
            i += 1

def manejadorClientes():
    lim = 0
    hiloDefault = threading.Thread(target=enviarStreamClientes, args=(lim,))
    hiloDefault.start()
    
    while True:
        with condicionManejador:
            condicionManejador.wait()
            if len(clientes) % 2 == 0:
                lim += 2
                hilo = threading.Thread(target=enviarStreamClientes, args=(lim,) )
                hilo.start()
            with condicionCliente:
                condicionCliente.notify() #Sincronizo con el hilo que me desperto



##############################      MAIN      ##############################

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

print("Server abierto") #Para probar que abre

clientes = [] #Lista global donde se guardarán los clientes "activos"

# Variable condition para despertar al hilo que maneja los hilos que envian el stream a los clientes
condicionManejador = threading.Condition()
condicionCliente = threading.Condition()

#Hilo que se encarga de crear otros hilos para mandar el stream. sera despertado cuando se agregue un nuevo hilo
hiloMain = threading.Thread(target=manejadorClientes,)
hiloMain.start()    
print("test") #Para probar que abre

while True:
        cliente, _ = sktC.accept()
        thread = threading.Thread(target = aceptarControl, args=(cliente,))
        thread.start()