import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORT))


def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024).decode()
            print("\n" + mensagem)
        except:
            break


thread = threading.Thread(target=receber_mensagens)
thread.start()

while True:

    print("\n1 - Inscrever em zona")
    print("2 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":

        zona = input("Digite a zona: ")

        mensagem = f"WATCH|{zona}"

        cliente.send(mensagem.encode())

    elif opcao == "2":
        break

cliente.close()