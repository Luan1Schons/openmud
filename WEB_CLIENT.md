# Cliente Web para OpenMud

Cliente web 100% Python que permite jogar o MUD diretamente no navegador!

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o Servidor MUD (em um terminal)

```bash
python3 server.py
```

O servidor MUD rodará na porta **4000** (padrão).

### 3. Iniciar o Servidor Web (em outro terminal)

```bash
python3 web_server.py
```

O servidor web rodará em:
- **HTTP**: `http://localhost:8000` (ou porta 80 se tiver permissões de root)
- **WebSocket**: `ws://localhost:8080`

### 4. Acessar no Navegador

Abra seu navegador e acesse:
```
http://localhost:8000
```

## 📋 Configuração

Você pode configurar as portas usando variáveis de ambiente:

```bash
# Porta HTTP (padrão: 80, fallback: 8000)
export WEB_PORT=8000

# Porta WebSocket (padrão: 8080)
export WS_PORT=8080

# Host e porta do servidor MUD (padrão: localhost:4000)
export MUD_HOST=localhost
export MUD_PORT=4000

# Iniciar servidor web
python3 web_server.py
```

## 🎮 Funcionalidades

- ✅ Interface web moderna com tema terminal
- ✅ Suporte completo a códigos ANSI (cores)
- ✅ Conexão em tempo real via WebSocket
- ✅ Reconexão automática
- ✅ Scroll automático
- ✅ Histórico de comandos visível

## 🔧 Estrutura

```
web_server.py    # Servidor HTTP + WebSocket Gateway
web/
  index.html     # Cliente web (HTML + CSS + JavaScript)
```

## 🌐 Deploy em Produção

Para produção, você pode:

1. **Usar porta 80 com sudo**:
```bash
sudo python3 web_server.py
```

2. **Ou usar proxy reverso (Nginx)**:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
    }
    
    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. **Ou usar variáveis de ambiente**:
```bash
WEB_PORT=8000 WS_PORT=8080 MUD_HOST=localhost MUD_PORT=4000 python3 web_server.py
```

## 📝 Notas

- O servidor web precisa que o servidor MUD esteja rodando
- O gateway WebSocket faz proxy entre o cliente web e o servidor MUD TCP
- Cores ANSI são processadas e exibidas no navegador
- A conexão é bidirecional: comandos do cliente → MUD, saída do MUD → cliente

