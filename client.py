"""
Sistema de Alertas de Defesa Civil — Cliente TCP
Conecta-se ao servidor, inscreve-se em zonas e recebe alertas em tempo real.

Uso:
    python client.py [zona_A zona_B ...]

Exemplo:
    python client.py zona_A zona_C
"""

import socket
import threading
import json
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000


def listen_for_alerts(conn: socket.socket):
    """Thread dedicada a receber mensagens push do servidor."""
    buf = ""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                print("\n[CLIENTE] Conexão encerrada pelo servidor.")
                break
            buf += data.decode(errors="ignore")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[CLIENTE] Mensagem bruta: {line}")
                    continue

                tipo = msg.get("tipo", "")
                if tipo == "ALERTA":
                    print(
                        f"\n⚠️  ALERTA [{msg.get('zona', '?')}] {msg.get('timestamp', '')} "
                        f"→ {msg.get('mensagem', '')}"
                    )
                elif tipo == "ACK":
                    print(f"[CLIENTE] Inscrito com sucesso na zona: {msg.get('zona')}")
                elif tipo == "ERRO":
                    print(f"[CLIENTE] Erro do servidor: {msg.get('detalhe')}")
                else:
                    print(f"[CLIENTE] Resposta: {msg}")
    except OSError:
        pass


def main():
    zones = sys.argv[1:] if len(sys.argv) > 1 else []
    if not zones:
        # modo interativo
        zonas_input = input("Informe as zonas (ex: zona_A zona_B): ").strip()
        zones = zonas_input.split() if zonas_input else ["zona_A"]

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CLIENTE] Conectado ao servidor {SERVER_HOST}:{SERVER_PORT}")
    except ConnectionRefusedError:
        print(f"[CLIENTE] Não foi possível conectar em {SERVER_HOST}:{SERVER_PORT}. Servidor está rodando?")
        sys.exit(1)

    # Inscreve-se nas zonas
    for zone in zones:
        msg = f"WATCH|{zone}\n"
        conn.sendall(msg.encode())

    # Thread para receber alertas (push)
    t = threading.Thread(target=listen_for_alerts, args=(conn,), daemon=True)
    t.start()

    print("[CLIENTE] Aguardando alertas... (Ctrl+C para sair)")
    try:
        t.join()
    except KeyboardInterrupt:
        print("\n[CLIENTE] Encerrando.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
