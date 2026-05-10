"""
Sistema de Alertas de Defesa Civil — Servidor TCP
Mantém conexões persistentes e replica alertas por zona em modelo Push.
"""

import socket
import threading
import json
import datetime

HOST = "0.0.0.0"
PORT = 9000
OPERATOR_PORT = 9001  # porta exclusiva para o operador/simulador enviar alertas

# Estrutura: { "zona_A": [conn1, conn2, ...], "zona_B": [...] }
subscriptions: dict[str, list[socket.socket]] = {}
lock = threading.Lock()


def broadcast_alert(zone: str, message: str) -> int:
    """Envia alerta para todos os clientes inscritos na zona. Retorna nº de envios."""
    payload = json.dumps({
        "tipo": "ALERTA",
        "zona": zone,
        "mensagem": message,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }) + "\n"

    dead: list[socket.socket] = []
    sent = 0

    with lock:
        targets = list(subscriptions.get(zone, []))

    for conn in targets:
        try:
            conn.sendall(payload.encode())
            sent += 1
        except OSError:
            dead.append(conn)

    # limpa conexões mortas
    with lock:
        for conn in dead:
            subscriptions.get(zone, [None]).remove(conn) if conn in subscriptions.get(zone, []) else None

    return sent


def remove_client(conn: socket.socket):
    """Remove cliente de todas as zonas."""
    with lock:
        for zone in subscriptions:
            if conn in subscriptions[zone]:
                subscriptions[zone].remove(conn)


def handle_client(conn: socket.socket, addr):
    print(f"[SERVIDOR] Cliente conectado: {addr}")
    buf = ""
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buf += data.decode(errors="ignore")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                # Protocolo: WATCH|zona_X
                if line.startswith("WATCH|"):
                    zone = line.split("|", 1)[1].strip()
                    with lock:
                        subscriptions.setdefault(zone, [])
                        if conn not in subscriptions[zone]:
                            subscriptions[zone].append(conn)
                    ack = json.dumps({"tipo": "ACK", "zona": zone}) + "\n"
                    conn.sendall(ack.encode())
                    print(f"[SERVIDOR] {addr} inscrito em '{zone}'")
                else:
                    err = json.dumps({"tipo": "ERRO", "detalhe": "Comando desconhecido"}) + "\n"
                    conn.sendall(err.encode())
    except OSError:
        pass
    finally:
        remove_client(conn)
        conn.close()
        print(f"[SERVIDOR] Cliente desconectado: {addr}")


def handle_operator(conn: socket.socket, addr):
    """Operador/simulador envia: ALERT|zona_X|Mensagem de alerta"""
    print(f"[SERVIDOR] Operador conectado: {addr}")
    buf = ""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data.decode(errors="ignore")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                if line.startswith("ALERT|"):
                    parts = line.split("|", 2)
                    if len(parts) < 3:
                        conn.sendall(b"ERRO: formato ALERT|zona|mensagem\n")
                        continue
                    _, zone, message = parts
                    sent = broadcast_alert(zone, message)
                    resp = f"OK: alerta enviado para {sent} cliente(s) em '{zone}'\n"
                    conn.sendall(resp.encode())
                    print(f"[SERVIDOR] Alerta '{message}' → zona '{zone}' → {sent} cliente(s)")
                elif line == "LIST":
                    with lock:
                        summary = {z: len(v) for z, v in subscriptions.items()}
                    conn.sendall((json.dumps(summary) + "\n").encode())
                else:
                    conn.sendall(b"ERRO: use ALERT|zona|mensagem ou LIST\n")
    except OSError:
        pass
    finally:
        conn.close()
        print(f"[SERVIDOR] Operador desconectado: {addr}")


def start_client_listener():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(50)
    print(f"[SERVIDOR] Aguardando clientes em {HOST}:{PORT}")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


def start_operator_listener():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, OPERATOR_PORT))
    srv.listen(5)
    print(f"[SERVIDOR] Aguardando operadores em {HOST}:{OPERATOR_PORT}")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle_operator, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    threading.Thread(target=start_operator_listener, daemon=True).start()
    start_client_listener()
