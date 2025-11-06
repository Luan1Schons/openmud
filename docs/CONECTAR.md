# Como Conectar ao MUD

<div align="center">
  <img src="openmud.png" alt="OpenMud Logo" width="400">
</div>

## Método 1: Usando o Script (Recomendado)

```bash
./connect.sh
```

Ou se não tiver permissão de execução:
```bash
bash connect.sh
```

## Método 2: Usando TinTin++ Diretamente

### Opção A: Com arquivo de configuração
```bash
tt++ -t tintin_config.tin
```

### Opção B: Conexão manual dentro do TinTin++
```bash
tt++
```
Depois, dentro do TinTin++, digite:
```
#session mud_local localhost 4000
```

## Método 3: Usando Telnet (teste simples)
```bash
telnet localhost 4000
```

## Método 4: Usando Netcat (nc)
```bash
nc localhost 4000
```

## Troubleshooting

### Erro: "Servidor não está rodando"
Certifique-se de que o servidor está rodando:
```bash
python3 server.py
```

### Erro: "TinTin++ não está instalado"
Instale o TinTin++:
- **Ubuntu/Debian**: `sudo apt install tintin++`
- **Fedora**: `sudo dnf install tintin++`
- **Arch**: `sudo pacman -S tintin++`
- **macOS**: `brew install tintin++`

### Erro: "CONNECT: THE PORT {TO} SHOULD BE A NUMBER"
Não use o comando `#connect` diretamente. Use `#session` em vez disso:
```
#session mud_local localhost 4000
```

### Comandos dentro do TinTin++
- `#help` - Mostra ajuda
- `#session mud_local localhost 4000` - Conecta ao servidor
- `#quit` ou `#exit` - Sai do TinTin++
- `#read tintin_config.tin` - Carrega configurações

## Aliases Úteis (já configurados no tintin_config.tin)
- `n` = `norte`
- `s` = `sul`
- `e` = `leste`
- `o` = `oeste`
- `l` = `look`
- `w` = `who`
- `i` ou `inv` = `inventory`
- `st` = `stats`

