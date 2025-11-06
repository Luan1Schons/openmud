"""
Teste de compatibilidade visual para verificar suporte a acentos e cores
"""

import asyncio
from mud.utils.ansi import ANSI

async def run_compatibility_test(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, database, username: str) -> bool:
    """
    Executa teste de compatibilidade visual
    Retorna True se o teste foi completado, False se foi cancelado
    """
    writer.write(f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}=== Teste de Compatibilidade Visual ==={ANSI.RESET}\r\n".encode())
    writer.write(f"{ANSI.BRIGHT_YELLOW}Este teste verifica se seu cliente suporta acentos e cores.{ANSI.RESET}\r\n".encode())
    writer.write(f"{ANSI.BRIGHT_YELLOW}Você só precisará fazer este teste uma única vez.{ANSI.RESET}\r\n\r\n".encode())
    await writer.drain()
    
    # Teste 1: Acentos
    writer.write(f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}--- Teste 1: Acentos ---{ANSI.RESET}\r\n\r\n".encode())
    await writer.drain()
    
    # Exemplo com acentos
    accent_example = (
        f"{ANSI.BRIGHT_GREEN}Exemplo com acentos:{ANSI.RESET}\r\n"
        f"  - {ANSI.BRIGHT_CYAN}Você consegue ver os acentos?{ANSI.RESET}\r\n"
        f"  - {ANSI.BRIGHT_CYAN}á, à, â, ã, é, ê, í, ó, ô, õ, ú, ç{ANSI.RESET}\r\n"
        f"  - {ANSI.BRIGHT_CYAN}Palavras: ação, coração, experiência, situação{ANSI.RESET}\r\n"
        f"  - {ANSI.BRIGHT_CYAN}Frases: 'Você está pronto?' 'Não se esqueça!'{ANSI.RESET}\r\n\r\n"
    )
    writer.write(accent_example.encode())
    await writer.drain()
    
    # Pergunta sobre acentos
    while True:
        writer.write(f"{ANSI.BRIGHT_YELLOW}Você consegue ver os acentos corretamente? (sim/não):{ANSI.RESET} ".encode())
        await writer.drain()
        
        try:
            response_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not response_data:
                return False
            
            response = response_data.decode().strip().lower()
            
            if response in ['sim', 's', 'yes', 'y', 'sí']:
                accent_ok = True
                break
            elif response in ['não', 'nao', 'no', 'n']:
                accent_ok = False
                break
            else:
                writer.write(f"{ANSI.RED}Por favor, responda 'sim' ou 'não'.{ANSI.RESET}\r\n".encode())
                await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return False
    
    # Teste 2: Cores
    writer.write(f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}--- Teste 2: Cores ---{ANSI.RESET}\r\n\r\n".encode())
    await writer.drain()
    
    # Exemplo com cores
    color_example = (
        f"{ANSI.BRIGHT_GREEN}Exemplo com cores:{ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_RED}●{ANSI.RESET} {ANSI.BRIGHT_RED}Vermelho (Red){ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_GREEN}●{ANSI.RESET} {ANSI.BRIGHT_GREEN}Verde (Green){ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_YELLOW}●{ANSI.RESET} {ANSI.BRIGHT_YELLOW}Amarelo (Yellow){ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_BLUE}●{ANSI.RESET} {ANSI.BRIGHT_BLUE}Azul (Blue){ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_MAGENTA}●{ANSI.RESET} {ANSI.BRIGHT_MAGENTA}Magenta{ANSI.RESET}\r\n"
        f"  {ANSI.BRIGHT_CYAN}●{ANSI.RESET} {ANSI.BRIGHT_CYAN}Ciano (Cyan){ANSI.RESET}\r\n"
        f"  {ANSI.WHITE}●{ANSI.RESET} {ANSI.WHITE}Branco (White){ANSI.RESET}\r\n"
        f"  {ANSI.YELLOW}●{ANSI.RESET} {ANSI.YELLOW}Amarelo normal{ANSI.RESET}\r\n"
        f"  {ANSI.RED}●{ANSI.RESET} {ANSI.RED}Vermelho normal{ANSI.RESET}\r\n\r\n"
    )
    writer.write(color_example.encode())
    await writer.drain()
    
    # Pergunta sobre cores
    while True:
        writer.write(f"{ANSI.BRIGHT_YELLOW}Você consegue ver as cores acima? (sim/não):{ANSI.RESET} ".encode())
        await writer.drain()
        
        try:
            response_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not response_data:
                return False
            
            response = response_data.decode().strip().lower()
            
            if response in ['sim', 's', 'yes', 'y', 'sí']:
                color_ok = True
                break
            elif response in ['não', 'nao', 'no', 'n']:
                color_ok = False
                break
            else:
                writer.write(f"{ANSI.RED}Por favor, responda 'sim' ou 'não'.{ANSI.RESET}\r\n".encode())
                await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return False
    
    # Resumo e confirmação final
    writer.write(f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}--- Resumo do Teste ---{ANSI.RESET}\r\n\r\n".encode())
    
    # Status dos testes
    accent_status = f"{ANSI.BRIGHT_GREEN}✓ OK{ANSI.RESET}" if accent_ok else f"{ANSI.BRIGHT_RED}✗ Problemas detectados{ANSI.RESET}"
    color_status = f"{ANSI.BRIGHT_GREEN}✓ OK{ANSI.RESET}" if color_ok else f"{ANSI.BRIGHT_RED}✗ Problemas detectados{ANSI.RESET}"
    
    writer.write(f"{ANSI.BRIGHT_YELLOW}Acentos:{ANSI.RESET} {accent_status}\r\n".encode())
    writer.write(f"{ANSI.BRIGHT_YELLOW}Cores:{ANSI.RESET} {color_status}\r\n\r\n".encode())
    await writer.drain()
    
    # Avisos se houver problemas
    if not accent_ok:
        writer.write(f"{ANSI.BRIGHT_YELLOW}Aviso:{ANSI.RESET} Se você não consegue ver acentos, pode haver problemas com a codificação do seu cliente.\r\n".encode())
        writer.write(f"{ANSI.BRIGHT_YELLOW}Recomendação:{ANSI.RESET} Configure seu cliente para usar UTF-8.\r\n\r\n".encode())
        await writer.drain()
    
    if not color_ok:
        writer.write(f"{ANSI.BRIGHT_YELLOW}Aviso:{ANSI.RESET} Se você não consegue ver cores, o jogo será menos visual, mas ainda funcionará.\r\n".encode())
        writer.write(f"{ANSI.BRIGHT_YELLOW}Recomendação:{ANSI.RESET} Use um cliente que suporte ANSI colors (como TinTin++).\r\n\r\n".encode())
        await writer.drain()
    
    # Confirmação final
    while True:
        writer.write(f"{ANSI.BRIGHT_YELLOW}Confirmar resultado do teste? (sim/não):{ANSI.RESET} ".encode())
        await writer.drain()
        
        try:
            response_data = await asyncio.wait_for(reader.readline(), timeout=60.0)
            if not response_data:
                return False
            
            response = response_data.decode().strip().lower()
            
            if response in ['sim', 's', 'yes', 'y', 'sí']:
                # Marca teste como completo no banco
                database.mark_compatibility_test_done(username)
                writer.write(f"\r\n{ANSI.BRIGHT_GREEN}Teste concluído! Obrigado pelas informações.{ANSI.RESET}\r\n\r\n".encode())
                await writer.drain()
                return True
            elif response in ['não', 'nao', 'no', 'n']:
                writer.write(f"{ANSI.YELLOW}Teste cancelado. Você poderá tentar novamente na próxima vez.{ANSI.RESET}\r\n".encode())
                await writer.drain()
                return False
            else:
                writer.write(f"{ANSI.RED}Por favor, responda 'sim' ou 'não'.{ANSI.RESET}\r\n".encode())
                await writer.drain()
        except asyncio.TimeoutError:
            writer.write(f"{ANSI.RED}Tempo esgotado.{ANSI.RESET}\r\n".encode())
            await writer.drain()
            return False

