import socket
import sys

ServerIP = sys.argv[1] #Por ejemplo, 127.0.0.1
ServerPort = int(sys.argv[2]) #Por ejemplo, 2023
VLCPort = sys.argv[3] #Por ejemplo, 7777

master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master.connect((ServerIP, ServerPort))
 
desconectar = False
print("Cliente abierto") #To test que abre very good the english

while not desconectar:
    comando = ""
    while (comando != "CONECTAR"):
        comando = input()

    master.send((comando + " " + VLCPort).encode())

    while (comando != "DESCONECTAR"):
        while (comando != "INTERRUMPIR" and comando != "DESCONECTAR"):
            comando = input()
            
        if (comando == "INTERRUMPIR"):
            master.send(comando.encode())

        while (comando != "CONTINUAR" and comando != "DESCONECTAR"):
            comando = input()

        if (comando == "CONTINUAR"):
            master.send(comando.encode())

    master.send(comando.encode())
    master.close()
    desconectar = True