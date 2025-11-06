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
    """Formata barra de HP"""
    bar = create_bar(current, maximum, 20, "█", "░", ANSI.BRIGHT_GREEN, ANSI.BRIGHT_YELLOW, ANSI.RED)
    percentage = int((current / maximum * 100)) if maximum > 0 else 0
    return f"{ANSI.BRIGHT_RED}{label}:{ANSI.RESET} {bar} {ANSI.BRIGHT_CYAN}{current}/{maximum}{ANSI.RESET} ({percentage}%)"

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

# ASCII Art para personagens, monstros e NPCs

CHARACTER_ASCII = {
    'warrior': {
        'human': """
    ╔═══╗
    ║ ⚔ ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'elf': """
    ╔═══╗
    ║ 🏹 ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'dwarf': """
    ╔═══╗
    ║ ⚔ ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """
    },
    'mage': {
        'human': """
    ╔═══╗
    ║ 🔮 ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'elf': """
    ╔═══╗
    ║ ✨ ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'dwarf': """
    ╔═══╗
    ║ 🔥 ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """
    },
    'ranger': {
        'human': """
    ╔═══╗
    ║ 🏹 ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'elf': """
    ╔═══╗
    ║ 🌿 ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """,
        'dwarf': """
    ╔═══╗
    ║ ⚔ ║
    ╚═╦═╝
      │
     ╔╩╗
    ╔╩╩╗
    """
    }
}

MONSTER_ASCII = {
    'goblin': """
    ╔═══╗
    ║ 👹 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'wolf': """
    ╔═══╗
    ║ 🐺 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'spider': """
    ╔═══╗
    ║ 🕷 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'orc': """
    ╔═══╗
    ║ 👹 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'orc_warrior': """
    ╔═══╗
    ║ ⚔👹 ║
    ╚═╦═╝
      │
     ╔╩╗
    """
}

NPC_ASCII = {
    'shopkeeper': """
    ╔═══╗
    ║ 💰 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'quest_giver': """
    ╔═══╗
    ║ 📜 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'trader': """
    ╔═══╗
    ║ 🛒 ║
    ╚═╦═╝
      │
     ╔╩╗
    """,
    'normal': """
    ╔═══╗
    ║ 👤 ║
    ╚═╦═╝
      │
     ╔╩╗
    """
}

def get_character_ascii(class_id: str, race_id: str) -> str:
    """Retorna ASCII art do personagem"""
    if class_id in CHARACTER_ASCII:
        if race_id in CHARACTER_ASCII[class_id]:
            return CHARACTER_ASCII[class_id][race_id]
        # Fallback para primeira raça disponível
        races = list(CHARACTER_ASCII[class_id].keys())
        if races:
            return CHARACTER_ASCII[class_id][races[0]]
    return """
    ╔═══╗
    ║ 👤 ║
    ╚═╦═╝
      │
     ╔╩╗
    """

def get_monster_ascii(monster_id: str) -> str:
    """Retorna ASCII art do monstro"""
    return MONSTER_ASCII.get(monster_id, """
    ╔═══╗
    ║ 👹 ║
    ╚═╦═╝
      │
     ╔╩╗
    """)

def get_npc_ascii(npc_type: str) -> str:
    """Retorna ASCII art do NPC"""
    return NPC_ASCII.get(npc_type, NPC_ASCII['normal'])

