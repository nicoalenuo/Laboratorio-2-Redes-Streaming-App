import socket
import sys

ServerIP = sys.argv[1] #Por ejemplo, 127.0.0.1
ServerPort = int(sys.argv[2]) #Por ejemplo, 2023
VLCPort = sys.argv[3] #Por ejemplo, 7777

master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master.connect((ServerIP, ServerPort))
desconectar = False
#Funcion para enviar los comandos al server
#Evita repetir codigo
def enviar_server(comando):
    respuesta = b""
    buffer = b""
    comando = comando.encode() 
    total_bytes = len(comando)
    bytes_enviados = 0

    while bytes_enviados < total_bytes:
        try:
            enviados = master.send(comando[bytes_enviados:])
            bytes_enviados += enviados
        except socket.error:
            master.close()
            print("Ocurrio un error")
            exit()

    while b'OK\n' not in respuesta:
        buffer = master.recv(16)
        respuesta += buffer
    print("OK")

#Comienza el main
while not desconectar:
    comando = ""

    while (comando != "CONECTAR" and comando != "DESCONECTAR"):
        comando = input()

    if comando == "CONECTAR":
        enviar_server(comando + " " + VLCPort + "\n")

    while (comando != "DESCONECTAR"):
        
        while (comando != "INTERRUMPIR" and comando != "DESCONECTAR"):
            comando = input()
            
        if (comando == "INTERRUMPIR"):
            enviar_server(comando + "\n")

        while (comando != "CONTINUAR" and comando != "DESCONECTAR"):
            comando = input()

        if (comando == "CONTINUAR"):
            enviar_server(comando + "\n")

    enviar_server(comando + "\n")
    master.close()
    desconectar = True
