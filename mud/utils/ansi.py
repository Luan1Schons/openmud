"""
Códigos ANSI para cores (compatível com TinTin++)
Sistema de cores padronizado para consistência visual
"""

class ANSI:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Cores de texto
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Cores brilhantes
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class Colors:
    """
    Sistema de cores padronizado para interface consistente
    Cores suaves e harmoniosas para melhor experiência visual
    """
    # Títulos e Headers
    TITLE = ANSI.BOLD + ANSI.BRIGHT_CYAN
    HEADER = ANSI.BRIGHT_CYAN
    SECTION = ANSI.BRIGHT_CYAN
    
    # Informações e Status
    INFO = ANSI.BRIGHT_GREEN
    SUCCESS = ANSI.BRIGHT_GREEN
    VALUE = ANSI.BRIGHT_YELLOW
    NUMBER = ANSI.BRIGHT_YELLOW
    
    # Avisos e Alertas
    WARNING = ANSI.YELLOW
    ALERT = ANSI.BRIGHT_YELLOW
    
    # Erros e Perigos
    ERROR = ANSI.RED
    DANGER = ANSI.BRIGHT_RED
    
    # Entidades do Jogo
    PLAYER = ANSI.BRIGHT_GREEN
    MONSTER = ANSI.BRIGHT_RED
    NPC = ANSI.BRIGHT_MAGENTA
    ITEM = ANSI.BRIGHT_CYAN
    SPELL = ANSI.BRIGHT_MAGENTA
    PERK = ANSI.BRIGHT_GREEN
    
    # Categorias e Tipos
    CATEGORY = ANSI.BRIGHT_MAGENTA
    TYPE = ANSI.BRIGHT_BLUE
    DESCRIPTION = ANSI.WHITE
    LABEL = ANSI.BRIGHT_CYAN
    
    # Ações e Comandos
    COMMAND = ANSI.BRIGHT_CYAN
    ACTION = ANSI.BRIGHT_GREEN
    HINT = ANSI.BRIGHT_BLACK
    
    # Separadores
    SEPARATOR = ANSI.BRIGHT_BLACK
    DIVIDER = ANSI.BRIGHT_BLACK
    
    # Reset
    RESET = ANSI.RESET

