#!/bin/bash
# Script para conectar ao MUD usando TinTin++

# Verifica se TinTin++ está instalado
if ! command -v tt++ &> /dev/null; then
    echo "TinTin++ não está instalado."
    echo "Instale com:"
    echo "  Ubuntu/Debian: sudo apt install tintin++"
    echo "  Fedora: sudo dnf install tintin++"
    echo "  Arch: sudo pacman -S tintin++"
    exit 1
fi

# Verifica se o servidor está rodando
if ! nc -z localhost 4000 2>/dev/null; then
    echo "Servidor não está rodando na porta 4000."
    echo "Inicie o servidor primeiro com: python3 server.py"
    exit 1
fi

# Conecta usando TinTin++ com arquivo de configuração
echo "Conectando ao MUD local..."
tt++ -t tintin_config.tin

