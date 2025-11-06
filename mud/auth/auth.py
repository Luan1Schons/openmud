"""
Sistema de autenticação (login/registro)
"""

import asyncio
from mud.utils.ansi import ANSI
from mud.core.database import Database

async def authenticate(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, database: Database) -> tuple[bool, str]:
    """
    Processa autenticação (login/registro)
    Retorna (sucesso, username)
    """
    writer.write(f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}=== Bem-vindo ao MUD! ==={ANSI.RESET}\r\n".encode())
    writer.write(f"{ANSI.BRIGHT_YELLOW}Você precisa fazer login ou criar uma conta.{ANSI.RESET}\r\n".encode())
    await writer.drain()
    
    while True:
        writer.write(f"\r\n{ANSI.BRIGHT_GREEN}1.{ANSI.RESET} Login\r\n".encode())
        writer.write(f"{ANSI.BRIGHT_GREEN}2.{ANSI.RESET} Registrar\r\n".encode())
        writer.write(f"{ANSI.BRIGHT_YELLOW}Escolha uma opção:{ANSI.RESET} ".encode())
        await writer.drain()
        
        try:
            choice_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
            if not choice_data:
                return False, ""
            
            choice = choice_data.decode().strip()
            
            if choice == "1":
                return await login(writer, reader, database)
            elif choice == "2":
                return await register(writer, reader, database)
            else:
                writer.write(f"{ANSI.RED}Opção inválida.{ANSI.RESET}\r\n".encode())
                await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return False, ""

async def login(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, database: Database) -> tuple[bool, str]:
    """Processa login"""
    writer.write(f"\r\n{ANSI.BOLD}=== Login ==={ANSI.RESET}\r\n".encode())
    await writer.drain()
    
    for attempt in range(3):
        writer.write(f"{ANSI.BRIGHT_GREEN}Username:{ANSI.RESET} ".encode())
        await writer.drain()
        
        username_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not username_data:
            return False, ""
        
        username = username_data.decode().strip()
        
        if not database.account_exists(username):
            writer.write(f"{ANSI.RED}Conta não encontrada. Tente novamente.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            continue
        
        writer.write(f"{ANSI.BRIGHT_GREEN}Senha:{ANSI.RESET} ".encode())
        await writer.drain()
        
        password_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not password_data:
            return False, ""
        
        password = password_data.decode().strip()
        
        if database.verify_login(username, password):
            writer.write(f"{ANSI.BRIGHT_GREEN}Login realizado com sucesso!{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return True, username
        
        writer.write(f"{ANSI.RED}Senha incorreta. Tentativas restantes: {2 - attempt}{ANSI.RESET}\r\n".encode())
        await writer.drain()
    
    writer.write(f"{ANSI.RED}Muitas tentativas falhas.{ANSI.RESET}\r\n".encode())
    await writer.drain()
    return False, ""

async def register(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, database: Database) -> tuple[bool, str]:
    """Processa registro"""
    writer.write(f"\r\n{ANSI.BOLD}=== Registrar Nova Conta ==={ANSI.RESET}\r\n".encode())
    await writer.drain()
    
    while True:
        writer.write(f"{ANSI.BRIGHT_GREEN}Escolha um username:{ANSI.RESET} ".encode())
        await writer.drain()
        
        username_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not username_data:
            return False, ""
        
        username = username_data.decode().strip()
        
        if not username:
            writer.write(f"{ANSI.RED}Username não pode estar vazio.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            continue
        
        if database.account_exists(username):
            writer.write(f"{ANSI.RED}Username já está em uso. Tente outro.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            continue
        
        writer.write(f"{ANSI.BRIGHT_GREEN}Escolha uma senha:{ANSI.RESET} ".encode())
        await writer.drain()
        
        password_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not password_data:
            return False, ""
        
        password = password_data.decode().strip()
        
        success, message = database.register_account(username, password)
        writer.write(f"{ANSI.BRIGHT_GREEN if success else ANSI.RED}{message}{ANSI.RESET}\r\n".encode())
        await writer.drain()
        
        if success:
            return True, username
        
        # Permite tentar novamente
        writer.write(f"{ANSI.YELLOW}Tente novamente.{ANSI.RESET}\r\n".encode())
        await writer.drain()

