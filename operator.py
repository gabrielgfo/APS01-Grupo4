"""
Sistema de Alertas de Defesa Civil — Simulador de Operador Central
Conecta-se à porta de operador do servidor e envia alertas para zonas.

Uso:
    python operator.py           → modo interativo
    python operator.py --demo    → envia sequência de alertas automáticos
"""

import socket
import time
import sys

SERVER_HOST = "127.0.0.1"
OPERATOR_PORT = 9001

DEMO_ALERTS = [
    ("zona_A", "⚠️  Chuva intensa prevista nas próximas 2 horas"),
    ("zona_B", "🌊 Risco de alagamento — evite áreas baixas"),
    ("zona_A", "⛰️  Deslizamento de terra detectado — evacuação imediata"),
    ("zona_C", "🌪️  Rajadas de vento acima de 80 km/h — abrigue-se"),
    ("zona_A", "✅  Situação normalizada — fim do alerta"),
]


def send_command(conn: socket.socket, cmd: str) -> str:
    conn.sendall((cmd.strip() + "\n").encode())
    return conn.recv(4096).decode(errors="ignore").strip()


def interactive_mode(conn: socket.socket):
    print("Operador Central — Comandos disponíveis:")
    print("  ALERT|<zona>|<mensagem>  → dispara alerta")
    print("  LIST                     → lista zonas e nº de inscritos")
    print("  sair                     → encerra\n")
    while True:
        try:
            cmd = input("operador> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[OPERADOR] Encerrando.")
            break
        if not cmd:
            continue
        if cmd.lower() in ("sair", "exit", "quit"):
            break
        resp = send_command(conn, cmd)
        print(f"[SERVIDOR] {resp}")


def demo_mode(conn: socket.socket):
    print("[DEMO] Iniciando sequência de alertas automáticos...\n")
    for zone, message in DEMO_ALERTS:
        cmd = f"ALERT|{zone}|{message}"
        print(f"[DEMO] Enviando → {cmd}")
        resp = send_command(conn, cmd)
        print(f"[SERVIDOR] {resp}\n")
        time.sleep(2)
    print("[DEMO] Sequência concluída.")


def main():
    demo = "--demo" in sys.argv

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((SERVER_HOST, OPERATOR_PORT))
        print(f"[OPERADOR] Conectado ao servidor {SERVER_HOST}:{OPERATOR_PORT}")
    except ConnectionRefusedError:
        print(f"[OPERADOR] Não foi possível conectar em {SERVER_HOST}:{OPERATOR_PORT}.")
        sys.exit(1)

    try:
        if demo:
            demo_mode(conn)
        else:
            interactive_mode(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
