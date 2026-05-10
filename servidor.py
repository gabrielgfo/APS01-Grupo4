import socket
import threading

HOST = '0.0.0.0'
PORT = 5000


zonas = {}


clientes = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Servidor iniciado...")


def enviar_alerta(zona, mensagem):
    if zona in zonas:
        for cliente in zonas[zona]:
            try:
                cliente.send(f"ALERTA [{zona}] -> {mensagem}".encode())
            except:
                pass


def tratar_cliente(cliente):
    while True:
        try:
            mensagem = cliente.recv(1024).decode()

            if not mensagem:
                break

            print("Recebido:", mensagem)

            partes = mensagem.split("|")

            comando = partes[0]

            
            if comando == "WATCH":

                zona = partes[1]

                if zona not in zonas:
                    zonas[zona] = []

                if cliente not in zonas[zona]:
                    zonas[zona].append(cliente)

                cliente.send(
                    f"Você foi inscrito na zona {zona}".encode()
                )

            
            elif comando == "ALERT":

                zona = partes[1]
                texto = partes[2]

                enviar_alerta(zona, texto)

        except:
            break

    cliente.close()


while True:
    cliente, endereco = server.accept()

    print("Novo cliente conectado:", endereco)

    clientes.append(cliente)

    thread = threading.Thread(
        target=tratar_cliente,
        args=(cliente,)
    )

    thread.start()