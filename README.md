# 🚨 Sistema de Alertas por Zonas

Sistema distribuído de alertas em tempo real utilizando modelo **Publisher/Subscriber**, onde clientes se inscrevem em zonas geográficas e recebem notificações automáticas enviadas por operadores.

---



## 🚀 Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/gabrielgfo/APS01-Grupo4
```

### 2. Entrar na pasta do projeto

```bash
cd sistemadistribuido
```

---

## ▶️ Executando os Componentes

O sistema possui três componentes que devem ser executados em terminais separados.

### 🖥️ Servidor

Abra um terminal e execute:

```bash
python servidor.py
```

**Saída esperada:**

```
Servidor iniciado...
```

---

### 👤 Cliente

Abra **outro terminal** e execute:

```bash
python cliente.py
```

**Exemplo de uso:**

```
1 - Inscrever em zona
2 - Sair

Escolha: 1
Digite a zona: zona_A
```

---

### 📡 Operador

Abra **outro terminal** e execute:

```bash
python operador.py
```

**Exemplo de uso:**

```
Zona: zona_A
Mensagem do alerta: Chuva intensa nas próximas horas
```

---

## 💡 Exemplo de Funcionamento

Veja abaixo um fluxo completo de comunicação entre os componentes:

**1. Cliente se inscreve em uma zona:**
```
zona_A
```

**2. Operador envia um alerta:**
```
ALERT|zona_A|Chuva intensa
```

**3. Cliente recebe automaticamente:**
```
ALERTA [zona_A] -> Chuva intensa
```

---

## 🏗️ Arquitetura

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   Operador   │──────▶│   Servidor   │──────▶│   Cliente    │
│  (publisher) │  alerta│  (broker)    │notifica│ (subscriber) │
└──────────────┘        └──────────────┘        └──────────────┘
                                │
                         Gerencia zonas
                         e inscrições
```



