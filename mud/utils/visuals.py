"""
Sistema de visualizações e animações para o terminal
"""

from typing import Optional
from mud.utils.ansi import ANSI

def create_bar(current: int, maximum: int, width: int = 20, filled_char: str = "█", 
               empty_char: str = "░", color_full: str = ANSI.BRIGHT_GREEN,
               color_medium: str = ANSI.BRIGHT_YELLOW, color_low: str = ANSI.RED) -> str:
    """
    Cria uma barra visual de progresso
    """
    if maximum == 0:
        return f"{color_full}{filled_char * width}{ANSI.RESET}"
    
    percentage = current / maximum
    filled = int(width * percentage)
    empty = width - filled
    
    # Escolhe cor baseada na porcentagem
    if percentage > 0.6:
        color = color_full
    elif percentage > 0.3:
        color = color_medium
    else:
        color = color_low
    
    bar = f"{color}{filled_char * filled}{ANSI.RESET}{empty_char * empty}"
    return bar

def format_hp_bar(current: int, maximum: int, label: str = "HP") -> str:
    """Formata barra de HP com cores consistentes baseadas na porcentagem"""
    if maximum == 0:
        percentage = 0
    else:
        percentage = current / maximum
    
    # Determina cor baseada na porcentagem (mesma cor para tudo)
    if percentage > 0.6:
        color = ANSI.BRIGHT_GREEN
    elif percentage > 0.3:
        color = ANSI.BRIGHT_YELLOW
    else:
        color = ANSI.RED
    
    # Cria barra com a cor determinada
    bar = create_bar(current, maximum, 20, "█", "░", color, color, color)
    percentage_int = int(percentage * 100) if maximum > 0 else 0
    
    # Aplica a mesma cor ao label, barra e valores
    return f"{color}{label}:{ANSI.RESET} {bar} {color}{current}/{maximum}{ANSI.RESET} {color}({percentage_int}%){ANSI.RESET}"

def get_hp_color(current: int, maximum: int) -> str:
    """Retorna a cor apropriada baseada na porcentagem de HP"""
    if maximum == 0:
        return ANSI.RED
    
    percentage = current / maximum
    if percentage > 0.6:
        return ANSI.BRIGHT_GREEN
    elif percentage > 0.3:
        return ANSI.BRIGHT_YELLOW
    else:
        return ANSI.RED

def format_monster_hp_bar(current: int, maximum: int, label: str = None) -> str:
    """Formata barra de HP de monstro de forma simplificada com cores consistentes"""
    if maximum == 0:
        percentage = 0
    else:
        percentage = current / maximum
    
    # Determina cor baseada na porcentagem (mesma cor para tudo)
    color = get_hp_color(current, maximum)
    
    # Cria barra com a cor determinada
    bar = create_bar(current, maximum, 15, "█", "░", color, color, color)
    
    # Se há label, aplica a mesma cor
    if label:
        return f"{color}{label}:{ANSI.RESET} {bar} {color}{current}/{maximum}{ANSI.RESET}"
    else:
        # Aplica a mesma cor à barra e valores
        return f"{bar} {color}{current}/{maximum}{ANSI.RESET}"

def format_stamina_bar(current: int, maximum: int, label: str = "Stamina") -> str:
    """Formata barra de Stamina"""
    bar = create_bar(current, maximum, 20, "█", "░", ANSI.BRIGHT_BLUE, ANSI.BRIGHT_YELLOW, ANSI.RED)
    percentage = int((current / maximum * 100)) if maximum > 0 else 0
    return f"{ANSI.BRIGHT_CYAN}{label}:{ANSI.RESET} {bar} {ANSI.BRIGHT_CYAN}{current}/{maximum}{ANSI.RESET} ({percentage}%)"

def format_mana_bar(current: int, maximum: int, label: str = "Mana") -> str:
    """Formata barra de Mana"""
    bar = create_bar(current, maximum, 20, "█", "░", ANSI.BRIGHT_MAGENTA, ANSI.BRIGHT_BLUE, ANSI.RED)
    percentage = int((current / maximum * 100)) if maximum > 0 else 0
    return f"{ANSI.BRIGHT_MAGENTA}{label}:{ANSI.RESET} {bar} {ANSI.BRIGHT_CYAN}{current}/{maximum}{ANSI.RESET} ({percentage}%)"

def get_attack_animation() -> list:
    """Retorna animação de ataque"""
    return [
        "⚔",
        "⚔ ",
        "⚔ →",
        "⚔ → →",
        "⚔ → → →",
        "⚔ → → → ✨",
        "⚔ → → → ✨ 💥",
    ]

def get_spell_animation() -> list:
    """Retorna animação de magia"""
    return [
        "✨",
        "✨ ✨",
        "✨ ✨ ⚡",
        "✨ ✨ ⚡ 💫",
        "✨ ✨ ⚡ 💫 🔮",
        "✨ ✨ ⚡ 💫 🔮 💥",
    ]

def get_heal_animation() -> list:
    """Retorna animação de cura"""
    return [
        "💚",
        "💚 💚",
        "💚 💚 ✨",
        "💚 💚 ✨ 🌟",
    ]

def display_animation(animation_frames: list, message: str = "") -> str:
    """Converte frames de animação em string"""
    if not animation_frames:
        return message
    return f"{animation_frames[-1]} {message}"

# Importa ASCII arts de arquivos separados
from mud.utils.ascii_players import get_player_ascii
from mud.utils.ascii_monsters import get_monster_ascii
from mud.utils.ascii_npcs import get_npc_ascii

# Aliases para compatibilidade
def get_character_ascii(class_id: str, race_id: str) -> str:
    """Retorna ASCII art do personagem (alias para get_player_ascii)"""
    return get_player_ascii(class_id, race_id)

def format_ascii_with_text(ascii_art: str, text: str, ascii_width: int = 20) -> str:
    """
    Formata ASCII art à esquerda e texto à direita lado a lado.
    
    Args:
        ascii_art: String com o ASCII art (pode ter múltiplas linhas)
        text: Texto a ser exibido à direita (pode conter códigos ANSI e \r\n)
        ascii_width: Largura reservada para o ASCII art (padrão 20)
    
    Returns:
        String formatada com ASCII à esquerda e texto à direita
    """
    # Divide o ASCII art em linhas
    ascii_lines_raw = ascii_art.split('\n')
    
    # Remove linhas vazias do início e fim
    while ascii_lines_raw and not ascii_lines_raw[0].strip():
        ascii_lines_raw.pop(0)
    while ascii_lines_raw and not ascii_lines_raw[-1].strip():
        ascii_lines_raw.pop()
    
    if not ascii_lines_raw:
        return text
    
    # Remove toda a indentação inicial de todas as linhas, alinhando tudo à esquerda
    # Isso garante que o ASCII art fique totalmente alinhado
    ascii_lines = []
    for line in ascii_lines_raw:
        if line.strip():  # Linha com conteúdo
            # Remove toda a indentação inicial, alinhando à esquerda
            ascii_lines.append(line.lstrip())
        else:  # Linha vazia
            ascii_lines.append("")
    
    # Remove linhas vazias consecutivas no final
    while ascii_lines and not ascii_lines[-1].strip():
        ascii_lines.pop()
    
    # Processa o texto - remove \r e divide por \n primeiro
    text_clean = text.replace('\r', '')
    text_paragraphs = text_clean.split('\n')
    
    # Quebra cada parágrafo em linhas se necessário
    text_lines = []
    max_text_width = 55  # Largura máxima do texto à direita (aumentado para acomodar mais info)
    
    for paragraph in text_paragraphs:
        if not paragraph.strip():
            text_lines.append("")
            continue
            
        # Remove códigos ANSI temporariamente para calcular largura
        import re
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        text_without_ansi = ansi_pattern.sub('', paragraph)
        
        # Se o texto cabe em uma linha, adiciona direto
        if len(text_without_ansi) <= max_text_width:
            text_lines.append(paragraph)
        else:
            # Quebra em palavras, mas preserva códigos ANSI
            words = paragraph.split()
            current_line = ""
            current_line_no_ansi = ""
            
            for word in words:
                word_no_ansi = ansi_pattern.sub('', word)
                if len(current_line_no_ansi) + len(word_no_ansi) + 1 <= max_text_width:
                    if current_line:
                        current_line += " " + word
                        current_line_no_ansi += " " + word_no_ansi
                    else:
                        current_line = word
                        current_line_no_ansi = word_no_ansi
                else:
                    if current_line:
                        text_lines.append(current_line)
                    current_line = word
                    current_line_no_ansi = word_no_ansi
            if current_line:
                text_lines.append(current_line)
    
    # Encontra a largura máxima do ASCII art (para alinhar todas as linhas)
    max_ascii_width = 0
    for line in ascii_lines:
        if line.strip():
            line_width = len(line.rstrip())
            max_ascii_width = max(max_ascii_width, line_width)
    
    # SEMPRE usa a largura desejada (ascii_width) para garantir alinhamento consistente
    # entre diferentes ASCII arts. Se o ASCII for maior, ainda usa ascii_width para
    # manter o texto sempre na mesma coluna (mas pode cortar ASCII muito grande)
    # Se o ASCII for menor, preenche com espaços até ascii_width
    final_ascii_width = ascii_width
    
    # Combina ASCII e texto linha por linha
    result_lines = []
    max_lines = max(len(ascii_lines), len(text_lines))
    
    for i in range(max_lines):
        ascii_part = ascii_lines[i] if i < len(ascii_lines) else ""
        text_part = text_lines[i] if i < len(text_lines) else ""
        
        # Remove espaços à direita e calcula largura real
        ascii_clean = ascii_part.rstrip() if ascii_part.strip() else ""
        ascii_real_width = len(ascii_clean)
        
        # Se o ASCII for maior que a largura desejada, trunca (mas preserva o máximo possível)
        # Se for menor, preenche com espaços
        if ascii_real_width > final_ascii_width:
            # Trunca o ASCII se for muito grande (mantém alinhamento)
            ascii_formatted = ascii_clean[:final_ascii_width]
        else:
            # Preenche o ASCII até a largura desejada (garantindo alinhamento consistente)
            # Todas as linhas terão exatamente final_ascii_width caracteres
            ascii_formatted = ascii_clean + " " * (final_ascii_width - ascii_real_width)
        
        # Combina ASCII e texto
        # IMPORTANTE: Todas as linhas devem ter a mesma largura total (ASCII + espaços)
        # para que o texto comece sempre na mesma coluna
        if text_part:
            # Linha com texto: ASCII (final_ascii_width) + 2 espaços + texto
            result_lines.append(f"{ascii_formatted}  {text_part}")
        else:
            # Linha sem texto: apenas ASCII preenchido até final_ascii_width
            # Isso mantém o alinhamento visual mesmo sem texto
            result_lines.append(ascii_formatted)
    
    return "\r\n".join(result_lines)

