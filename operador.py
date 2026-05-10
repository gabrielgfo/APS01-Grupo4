import socket

HOST = '127.0.0.1'
PORT = 5000

operador = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
operador.connect((HOST, PORT))

while True:

    zona = input("Zona: ")
    alerta = input("Mensagem do alerta: ")

    mensagem = f"ALERT|{zona}|{alerta}"

    operador.send(mensagem.encode())