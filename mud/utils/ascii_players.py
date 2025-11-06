"""
ASCII Art para Players (Jogadores)
Estilo baseado em Post-Coder Wars
Variações únicas para cada classe e raça
"""

PLAYER_ASCII = {
    'warrior': {
        'human': """
   /^\
  (o_o)
  /|-|\
   / \
  |___|
    """,
        'elf': """
   /^\
 <(o_o)>
  /|-|\
   / \
  |___|
    """,
        'dwarf': """
   __/^\__
  ( -o_o- )
   |  |  \
  /|--+--\
 /_|_/ \_|_\
    |   |
    |===|
    """
    },
    'mage': {
        'human': """
   /^\
  (o_o)
  /|-|\
   / \
  |___|
    """,
        'elf': """
  /\^/\
 <(o_o)>
  /|-|\
   / \
  |___|
    """,
        'dwarf': """
   __/^\__
  ( -o_o- )
   |  |  \
  /|--+--\
 /_|_/ \_|_\
    |   |
    |===|
    """,
    },
    'ranger': {
        'human': """
   ,/^\
  ( o_o )
   |'_'|
  /|_-_|\>
   /   \
  |_____| 
    """,
        'elf': """
   ,/^\
  <(o_o)>
   |'_'|
  /|_-_|\>
   /   \
  |_____| 
    """,
        'dwarf': """
  _/^\
 <(•_•)>
  /]-[\
   | |
  _|_|_
    """
    },
    'rogue': {
        'human': """
   .-^-.
  ( o_o )
   |_-_|
  /|_X_|\
    / \
   /___\

    """,
        'elf': """
   .-^-.
 <( o_o )>
   |_-_|
  /|_X_|\
    / \
   /___\

    """,
        'dwarf': """
  __===__
  [-o_o-]
   | : |
  /|_-_|\
   |___|
  /_____\ 
    """
    },
    'cleric': {
        'human': """
    /^\
   (o_o)
   /|+|\
    | |
   _|_|_
    """,
        'elf': """
    /^\
  <(o_o)>
   /|+|\
    | |
   _|_|_
    """,
        'dwarf': """
  __/^__
  [-o_o-]
   | + |
  /|_-_|\
   |___|
  (_____)
    """
    }
}

def get_player_ascii(class_id: str, race_id: str) -> str:
    """Retorna ASCII art do personagem"""
    if class_id in PLAYER_ASCII:
        if race_id in PLAYER_ASCII[class_id]:
            return PLAYER_ASCII[class_id][race_id]
        # Fallback para primeira raça disponível
        races = list(PLAYER_ASCII[class_id].keys())
        if races:
            return PLAYER_ASCII[class_id][races[0]]
    return """
   /^\
  (o_o)
  /|-|\
   / \
  |___|
    """
