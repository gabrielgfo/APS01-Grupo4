# Sistema de Alertas de Defesa Civil

Sistema distribuído de alertas baseados em localização usando **sockets TCP persistentes** e modelo **Push**.

---

## Arquitetura

```
Operador (operator.py)
       │  TCP :9001
       ▼
  Servidor (server.py)  ──── mantém lista de inscritos em memória
       │  TCP :9000
       ├──► Cliente A (zona_A)
       ├──► Cliente B (zona_A, zona_B)
       └──► Cliente C (zona_C)
```

- **Porta 9000** → clientes se conectam e se inscrevem em zonas  
- **Porta 9001** → operador central envia alertas  
- Alertas são replicados **instantaneamente** (Push) para todos os inscritos da zona

---

## Protocolo

### Cliente → Servidor (porta 9000)
| Comando | Descrição |
|---|---|
| `WATCH\|zona_X\n` | Inscreve-se na zona X |

### Servidor → Cliente (push)
```json
{"tipo": "ALERTA", "zona": "zona_A", "mensagem": "...", "timestamp": "..."}
{"tipo": "ACK",    "zona": "zona_A"}
{"tipo": "ERRO",   "detalhe": "..."}
```

### Operador → Servidor (porta 9001)
| Comando | Descrição |
|---|---|
| `ALERT\|zona_X\|mensagem\n` | Dispara alerta para zona X |
| `LIST\n` | Lista zonas e quantidade de inscritos |

---

## Como executar

### 1. Servidor
```bash
python server.py
```

### 2. Clientes (em terminais separados)
```bash
# Inscreve-se em zona_A e zona_C
python client.py zona_A zona_C

# Inscreve-se apenas em zona_B
python client.py zona_B
```

### 3. Operador — modo interativo
```bash
python operator.py
```
```
operador> LIST
operador> ALERT|zona_A|Risco de deslizamento — evacuação imediata
operador> ALERT|zona_B|Chuva intensa prevista para as próximas 2h
```

### 3. Operador — modo demo (alertas automáticos)
```bash
python operator.py --demo
```

---

## Exemplo de saída

**Terminal cliente (zona_A):**
```
[CLIENTE] Conectado ao servidor 127.0.0.1:9000
[CLIENTE] Inscrito com sucesso na zona: zona_A

⚠️  ALERTA [zona_A] 2026-05-10T14:32:01 → Risco de deslizamento — evacuação imediata
✅  ALERTA [zona_A] 2026-05-10T14:35:00 → Situação normalizada — fim do alerta
```

**Terminal servidor:**
```
[SERVIDOR] Aguardando clientes em 0.0.0.0:9000
[SERVIDOR] Aguardando operadores em 0.0.0.0:9001
[SERVIDOR] Cliente conectado: ('127.0.0.1', 54210)
[SERVIDOR] ('127.0.0.1', 54210) inscrito em 'zona_A'
[SERVIDOR] Alerta 'Risco de deslizamento' → zona 'zona_A' → 1 cliente(s)
```

---

## Detalhes de implementação

- **Threading**: cada cliente e operador roda em thread própria (`daemon=True`)
- **Lock**: `threading.Lock` protege o dicionário `subscriptions` de race conditions
- **Conexões mortas**: detectadas no momento do `sendall` e removidas automaticamente
- **Múltiplas zonas**: um cliente pode se inscrever em várias zonas simultaneamente
- **Sem dependências externas**: usa apenas a biblioteca padrão do Python 3.8+
