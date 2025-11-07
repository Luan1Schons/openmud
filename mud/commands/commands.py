"""
Sistema de comandos do MUD
"""

import unicodedata

from typing import Optional, Dict, List
from mud.core.models import Player, Monster, Room
from mud.utils.ansi import ANSI, Colors
from mud.managers.world_manager import WorldManager
from mud.core.database import Database
from mud.managers.game_data import GameDataManager
from mud.managers.lore_manager import LoreManager
from mud.systems.combat import CombatSystem
from mud.managers.quest_manager import QuestManager

class CommandHandler:
    """Processa comandos dos jogadores"""
    
    _MAP_TILE_WIDTH = 6
    _MAP_TILE_HEIGHT = 4
    _MAP_PATH_COLOR = ANSI.BRIGHT_YELLOW
    _MAP_TILE_TEMPLATES = {
        'forest': (
            (
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
            ),
            (
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
            ),
            (
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
            ),
            (
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.GREEN),
                ('░', ANSI.BRIGHT_GREEN),
            ),
        ),
        'swamp': (
            (
                ('≈', ANSI.BRIGHT_GREEN),
                ('≈', ANSI.GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
                ('≈', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
            ),
            (
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
                ('≈', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
                ('≈', ANSI.BRIGHT_GREEN),
            ),
            (
                ('≈', ANSI.GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.BRIGHT_GREEN),
                ('≈', ANSI.GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
            ),
            (
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
                ('≈', ANSI.BRIGHT_GREEN),
                ('▒', ANSI.BRIGHT_BLACK),
                ('≈', ANSI.GREEN),
                ('≈', ANSI.BRIGHT_GREEN),
            ),
        ),
        'water': (
            (
                ('≈', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('~', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
                ('~', ANSI.BRIGHT_CYAN),
            ),
            (
                ('~', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('~', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
            ),
            (
                ('≈', ANSI.BRIGHT_BLUE),
                ('~', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('~', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
            ),
            (
                ('~', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('~', ANSI.BRIGHT_BLUE),
                ('≈', ANSI.BRIGHT_CYAN),
                ('≈', ANSI.BRIGHT_BLUE),
            ),
        ),
        'mountain': (
            (
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
            ),
            (
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
            ),
            (
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
            ),
            (
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
                ('╲', ANSI.BRIGHT_BLACK),
                ('▲', ANSI.BRIGHT_WHITE),
                ('╱', ANSI.BRIGHT_BLACK),
            ),
        ),
        'cave': (
            (
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.WHITE),
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.WHITE),
            ),
            (
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
            ),
            (
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.WHITE),
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.BRIGHT_BLACK),
                ('▒', ANSI.WHITE),
            ),
            (
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
                ('▒', ANSI.BRIGHT_BLACK),
                ('▓', ANSI.WHITE),
            ),
        ),
        'city': (
            (
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_CYAN),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
            ),
            (
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_CYAN),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
            ),
            (
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_CYAN),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
            ),
            (
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_CYAN),
                ('▓', ANSI.BRIGHT_MAGENTA),
                ('▒', ANSI.BRIGHT_WHITE),
                ('▓', ANSI.BRIGHT_MAGENTA),
            ),
        ),
        'desert': (
            (
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
            ),
            (
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
            ),
            (
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
            ),
            (
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
                ('.', ANSI.YELLOW),
                ('·', ANSI.BRIGHT_YELLOW),
            ),
        ),
        'snow': (
            (
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
            ),
            (
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
            ),
            (
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
            ),
            (
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_CYAN),
                ('✶', ANSI.BRIGHT_WHITE),
            ),
        ),
        'lava': (
            (
                ('≈', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('~', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
                ('~', ANSI.RED),
            ),
            (
                ('~', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('~', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
            ),
            (
                ('≈', ANSI.BRIGHT_RED),
                ('~', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('~', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
            ),
            (
                ('~', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('~', ANSI.BRIGHT_RED),
                ('≈', ANSI.RED),
                ('≈', ANSI.BRIGHT_RED),
            ),
        ),
        'neutral': (
            (
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
            ),
            (
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
            ),
            (
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
            ),
            (
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
                ('·', ANSI.BRIGHT_BLACK),
                ('·', ANSI.BRIGHT_WHITE),
            ),
        ),
        'empty': (
            (
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
            ),
            (
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
            ),
            (
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
            ),
            (
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
                (' ', ANSI.BRIGHT_BLACK),
            ),
        ),
    }
    _MAP_ENV_SYMBOLS = {
        'forest': ('♣', ANSI.BRIGHT_GREEN),
        'swamp': ('≈', ANSI.GREEN),
        'water': ('≈', ANSI.BRIGHT_CYAN),
        'mountain': ('▲', ANSI.BRIGHT_WHITE),
        'cave': ('◆', ANSI.BRIGHT_BLACK),
        'city': ('■', ANSI.BRIGHT_MAGENTA),
        'desert': ('·', ANSI.BRIGHT_YELLOW),
        'snow': ('✶', ANSI.BRIGHT_WHITE),
        'lava': ('♨', ANSI.BRIGHT_RED),
        'neutral': ('●', ANSI.BRIGHT_WHITE),
        'empty': (' ', ANSI.BRIGHT_BLACK),
    }
    _MAP_LEGEND_DESCRIPTIONS = {
        'forest': 'Floresta / Grama',
        'swamp': 'Pântano / Lama',
        'water': 'Água / Costas',
        'mountain': 'Montanha / Rocha',
        'cave': 'Caverna / Subterrâneo',
        'city': 'Construções / Cidade',
        'desert': 'Deserto / Areia',
        'snow': 'Neve / Gelo',
        'lava': 'Lava / Vulcânico',
        'neutral': 'Terreno neutro',
    }
    _MAP_ENV_KEYWORDS = [
        ('lava', ('lava', 'vulcao', 'vulcão', 'magma', 'vulcanico', 'vulcânico')),
        ('cave', ('caverna', 'catacumba', 'gruta', 'mina', 'cripta', 'subsolo', 'subterraneo', 'subterrâneo', 'tunel', 'túnel', 'ruina', 'ruína', 'ruinas', 'ruínas', 'catacumbas')),
        ('swamp', ('pantano', 'pântano', 'brejo', 'lodo', 'lama', 'lodoso')),
        ('water', ('rio', 'lago', 'mar', 'oceano', 'praia', 'cachoeira', 'porto', 'ilha', 'baia', 'baía', 'caverna marinha', 'laguna')),
        ('snow', ('neve', 'gelo', 'glacial', 'inverno', 'gelado', 'gelada', 'tundra')),
        ('forest', ('floresta', 'bosque', 'arvore', 'árvore', 'vale', 'campo', 'clareira', 'selva', 'grama', 'prado', 'raiz', 'folha', 'arvores', 'árvores', 'copa', 'tronco')),
        ('mountain', ('montanha', 'pico', 'penhasco', 'falésia', 'falesia', 'rocha', 'desfiladeiro', 'cume', 'encosta', 'picos', 'cordilheira')),
        ('city', ('cidade', 'praça', 'templo', 'torre', 'distrito', 'mercado', 'vilarejo', 'aldeia', 'fortaleza', 'castelo', 'oficina', 'sala', 'laboratorio', 'laboratório', 'casa', 'cabana', 'porto')),
        ('desert', ('deserto', 'areia', 'duna', 'oasis', 'oásis', 'arido', 'árido', 'seco')),
    ]
    _MAP_OPPOSITE_DIRECTIONS = {
        'norte': 'sul',
        'sul': 'norte',
        'leste': 'oeste',
        'oeste': 'leste',
        'nordeste': 'sudoeste',
        'sudoeste': 'nordeste',
        'noroeste': 'sudeste',
        'sudeste': 'noroeste',
        'cima': 'baixo',
        'baixo': 'cima',
    }
    
    def __init__(self, game, world_manager: WorldManager, database: Database, 
                 game_data: GameDataManager, lore_manager: LoreManager, quest_manager: QuestManager, world_lore_manager=None, dungeon_manager=None):
        self.game = game
        self.world_manager = world_manager
        self.database = database
        self.game_data = game_data
        self.lore_manager = lore_manager
        self.quest_manager = quest_manager
        self.world_lore_manager = world_lore_manager
        self.dungeon_manager = dungeon_manager
        
        # Sistema de magias
        from mud.systems.spells import SpellSystem
        self.spell_system = SpellSystem()
        self.directions = {
            'norte': 'norte', 'n': 'norte',
            'sul': 'sul', 's': 'sul',
            'leste': 'leste', 'e': 'leste',
            'oeste': 'oeste', 'o': 'oeste',
            'nordeste': 'nordeste', 'ne': 'nordeste',
            'noroeste': 'noroeste', 'no': 'noroeste',
            'sudeste': 'sudeste', 'se': 'sudeste',
            'sudoeste': 'sudoeste', 'so': 'sudoeste'
        }
        # Monstros em combate por jogador
        self.in_combat: dict[str, str] = {}  # player_name -> monster_id
        # Estado do combate estilo Pokémon (armazena informações do combate atual)
        self.combat_state: dict[str, dict] = {}  # player_name -> {monster_instance_id, turn_waiting, etc}
        
        # Sistema de identificadores de monstros (estilo MUD tradicional)
        # {world_id: {room_id: {monster_instance_id: Monster}}}
        self.monster_instances: Dict[str, Dict[str, Dict[int, Monster]]] = {}
        # Contador de IDs de monstros por sala
        self.monster_id_counter: Dict[str, Dict[str, int]] = {}  # {world_id: {room_id: counter}}
        
        # Mapa de comandos para funções (dispatch table) - O(1) lookup
        # Estrutura: {comando: (função, precisa_args, precisa_post_processamento)}
        self._command_map = {
            # Comandos sem argumentos
            'look': (self.cmd_look, False, False),
            'l': (self.cmd_look, False, False),
            'who': (self.cmd_who, False, False),
            'players': (self.cmd_who, False, False),
            'online': (self.cmd_who, False, False),  # alias adicional
            'help': (self.cmd_help, True, False),  # Aceita args opcionais (página/categoria)
            '?': (self.cmd_help, True, False),
            'afk': (self.cmd_afk, True, False),  # Comando exclusivo do lobby
            'voltar': (self.cmd_voltar, False, False),  # Comando exclusivo do lobby
            'back': (self.cmd_voltar, False, False),  # alias
            'lobby': (self.cmd_lobby, False, False),  # Comando para voltar ao lobby
            'respawn': (self.cmd_respawn, False, False),  # Comando exclusivo do lobby
            'server': (self.cmd_server_status, False, False),  # Comando exclusivo do lobby
            'status_server': (self.cmd_server_status, False, False),  # alias
            'lore': (self.cmd_world_lore, False, False),
            'world': (self.cmd_world_lore, False, False),
            'intro': (self.cmd_world_lore, False, False),
            'quit': (self.cmd_quit, False, False),
            'exit': (self.cmd_quit, False, False),
            'stats': (self.cmd_stats, False, False),
            'status': (self.cmd_stats, False, False),
            'inventory': (self.cmd_inventory, True, False),  # Aceita args opcionais (busca/página)
            'inv': (self.cmd_inventory, True, False),
            'i': (self.cmd_inventory, True, False),
            'sair': (self.cmd_exit_dungeon, False, False),
            'exit_dungeon': (self.cmd_exit_dungeon, False, False),
            'channels': (self.cmd_channels, False, False),
            'chan': (self.cmd_channels, False, False),
            'inspect': (self.cmd_inspect, True, False),
            'examine': (self.cmd_inspect, True, False),
            'lookat': (self.cmd_inspect, True, False),
            'view': (self.cmd_inspect, True, False),
            'mapa': (self.cmd_mapa, False, False),
            'map': (self.cmd_mapa, False, False),
            
            # Comandos com argumentos
            'say': (self.cmd_say, True, False),
            '"': (self.cmd_say, True, False),
            'shout': (self.cmd_shout, True, False),
            'global': (self.cmd_shout, True, False),
            'join': (self.cmd_join, True, False),
            'leave': (self.cmd_leave, True, False),
            'attack': (self.cmd_attack, True, True),  # precisa atualizar quests
            'kill': (self.cmd_attack, True, True),
            'k': (self.cmd_attack, True, True),  # alias curto para kill
            'get': (self.cmd_get, True, False),
            'take': (self.cmd_get, True, False),
            'drop': (self.cmd_drop, True, False),
            'talk': (self.cmd_talk, True, False),
            'speak': (self.cmd_talk, True, False),
            'read': (self.cmd_read, True, False),
            'use': (self.cmd_use, True, False),
            'buy': (self.cmd_buy, True, False),
            'sell': (self.cmd_sell, True, False),
            'shop': (self.cmd_shop, True, False),
            'list': (self.cmd_shop, True, False),
            'trade': (self.cmd_trade, True, False),
            'quest': (self.cmd_quest, True, False),
            'quests': (self.cmd_quest, True, False),
            'accept': (self.cmd_accept_quest, True, False),
            'complete': (self.cmd_complete_quest, True, False),
            'finish': (self.cmd_complete_quest, True, False),
            'cancel': (self.cmd_cancel_quest, True, False),
            'abandon': (self.cmd_cancel_quest, True, False),
            'entrar': (self.cmd_enter, True, False),
            'enter': (self.cmd_enter, True, False),
            'spells': (self.cmd_spells, False, False),
            'magias': (self.cmd_spells, False, False),
            'cast': (self.cmd_cast, True, False),
            'lançar': (self.cmd_cast, True, False),
            'equipar': (self.cmd_equip_spell, True, False),
            'equip_spell': (self.cmd_equip_spell, True, False),
            'desequipar': (self.cmd_unequip_spell, True, False),
            'unequip_spell': (self.cmd_unequip_spell, True, False),
            'equip': (self.cmd_equip, True, False),
            'unequip': (self.cmd_unequip, True, False),
            'desequip': (self.cmd_unequip, True, False),
            'improve': (self.cmd_improve_spell, True, False),
            'melhorar': (self.cmd_improve_spell, True, False),
            'learn': (self.cmd_learn_spell, True, False),
            'aprender': (self.cmd_learn_spell, True, False),
            'perks': (self.cmd_perks, False, False),
            'points': (self.cmd_distribute_points, True, True),  # Aceita args opcionais
            'pontos': (self.cmd_distribute_points, True, True),
            'distribute': (self.cmd_distribute_points, True, True),
        }
    
    async def handle_command(self, player: Player, command: str):
        """
        Processa um comando do jogador usando dispatch table para melhor performance.
        Complexidade: O(1) lookup em vez de O(n) com if/elif chain.
        """
        parts = command.strip().lower().split()
        if not parts:
            return
        
        cmd = parts[0]
        args_str = ' '.join(parts[1:]) if len(parts) > 1 else ''
        
        # Se está em combate, só permite comandos de combate (menu estilo Pokémon)
        if player.name in self.in_combat:
            # Comandos permitidos durante combate: números (1-9) para menu, ou comandos específicos
            if cmd.isdigit():
                # É uma escolha do menu de combate
                await self._handle_combat_menu_choice(player, int(cmd))
                return
            elif cmd in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                await self._handle_combat_menu_choice(player, int(cmd))
                return
            else:
                # Mostra menu de combate e ignora outros comandos
                await self._show_combat_menu(player)
                return
        
        # Verifica se é um comando de direção (movimento) - tratado separadamente
        if cmd in self.directions:
            if player.name in self.in_combat:
                await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode se mover!{ANSI.RESET}")
            else:
                await self.cmd_move(player, self.directions[cmd])
            return
        
        # Busca o comando no mapa de comandos (O(1) lookup)
        command_info = self._command_map.get(cmd)
        
        if command_info:
            handler, precisa_args, precisa_post = command_info
            try:
                # Executa o handler apropriado
                if precisa_args:
                    await handler(player, args_str)
                else:
                    await handler(player)
                
                # Pós-processamento para comandos específicos (ex: atualizar quests após attack)
                if precisa_post:
                    await self._update_kill_quests(player, args_str)
                    
            except Exception as e:
                await self.send_message(player, f"{ANSI.RED}Erro ao executar comando: {e}{ANSI.RESET}")
        else:
            # Verifica se é uma saída normal da sala primeiro
            room = self.world_manager.get_room(player.world_id, player.room_id, self.dungeon_manager)
            if room and cmd in room.exits:
                # Se está em combate, não pode se mover
                if player.name in self.in_combat:
                    await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode se mover!{ANSI.RESET}")
                    return
                # É uma saída normal, usa movimento
                await self.cmd_move(player, cmd)
                return
            
            # Verifica se é um comando de entrada em porta/dungeon
            if self.dungeon_manager:
                dungeon = self.dungeon_manager.get_dungeon_by_entry_room(player.world_id, player.room_id)
                if dungeon:
                    entry_command = dungeon.get('entry_command', '').lower().strip()
                    # Remove "entrar" do início se presente para comparar apenas o comando base
                    entry_base = entry_command.replace('entrar', '').strip()
                    if entry_base == cmd or entry_command == cmd:
                        # É um comando de entrada em porta/dungeon
                        # Verifica se está em combate
                        if player.name in self.in_combat:
                            await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode se mover!{ANSI.RESET}")
                            return
                        await self.cmd_enter(player, cmd)
                        return
            
            await self.send_message(player, f"{ANSI.RED}Comando desconhecido: {cmd}. Digite 'help' para ajuda.{ANSI.RESET}")
    
    async def cmd_look(self, player: Player):
        """Comando look - mostra informações da sala atual"""
        # Tenta buscar na sala normal primeiro, depois em dungeon
        room = self.world_manager.get_room(player.world_id, player.room_id, self.dungeon_manager)
        if not room:
            return
        
        # Se estiver em uma dungeon, spawna monstros e itens
        if self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, player.room_id):
            await self._spawn_dungeon_entities(player, player.room_id)
        
        message = f"\r\n{Colors.TITLE}{room.name}{Colors.RESET}\r\n"
        message += f"{Colors.SEPARATOR}{'=' * len(room.name)}{Colors.RESET}\r\n\r\n"
        
        # Descrição da sala + lore (apenas se ainda não foi vista)
        message += f"{Colors.DESCRIPTION}{room.description}{Colors.RESET}\r\n"
        room_lore = self.lore_manager.get_room_lore(player.world_id, player.room_id)
        if room_lore and 'story' in room_lore:
            # Verifica se o jogador já viu esta lore
            if not self.database.has_viewed_lore(player.name, player.world_id, player.room_id):
                message += f"\r\n{Colors.INFO}{room_lore['story']}{Colors.RESET}\r\n"
                # Marca como vista
                self.database.mark_lore_as_viewed(player.name, player.world_id, player.room_id)
        
        # Informações especiais do lobby
        if player.room_id == "lobby":
            message += f"\r\n{Colors.SECTION}=== Comandos Exclusivos do Lobby ==={Colors.RESET}\r\n"
            message += f"{Colors.COMMAND}afk [mensagem]{Colors.RESET} - Marca como AFK\r\n"
            message += f"{Colors.COMMAND}voltar / back{Colors.RESET} - Volta do AFK\r\n"
            message += f"{Colors.COMMAND}lobby{Colors.RESET} - Volta ao Hall de Entrada (de qualquer lugar)\r\n"
            message += f"{Colors.COMMAND}respawn{Colors.RESET} - Regenera completamente HP e Stamina\r\n"
            message += f"{Colors.COMMAND}server / status_server{Colors.RESET} - Mostra status do servidor\r\n"
        
        message += "\r\n"
        
        # Entidades na sala
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Monstros com identificadores (estilo MUD)
        room_key = f"{player.world_id}:{player.room_id}"
        if room_key not in self.monster_instances:
            self.monster_instances[player.world_id] = {player.room_id: {}}
            self.monster_id_counter[player.world_id] = {player.room_id: 0}
        
        # Spawna slimes aleatoriamente em salas específicas (antes de garantir instâncias, não no lobby)
        if player.room_id != "lobby":
            await self._spawn_random_slimes(player)
        
        # Spawna monstros baseado na configuração da sala (se não estiver em dungeon e não estiver no lobby)
        if (player.room_id != "lobby" and 
            not (self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, player.room_id))):
            await self._spawn_room_monsters(player)
        
        # Garante que todos os monstros da sala têm instâncias
        await self._ensure_monster_instances(player.world_id, player.room_id, entities['monsters'])
        
        monster_instances = self.monster_instances[player.world_id].get(player.room_id, {})
        
        if monster_instances:
            message += f"{Colors.MONSTER}Monstros aqui:{Colors.RESET}\r\n"
            # Ordena por ID para mostrar em ordem
            from mud.utils.visuals import get_monster_ascii, format_hp_bar, format_ascii_with_text
            for monster_instance_id in sorted(monster_instances.keys()):
                monster = monster_instances[monster_instance_id]
                if monster and monster.is_alive():
                    # ASCII art do monstro
                    monster_ascii = get_monster_ascii(monster.id)
                    
                    # Monta informações do monstro
                    level_info = f"{Colors.NUMBER}[Nível {monster.level}]{Colors.RESET}"
                    weapon_info = ""
                    if monster.weapon:
                        weapon_info = f" {Colors.HINT}({monster.weapon}){Colors.RESET}"
                    
                    race_info = ""
                    if monster.race_id:
                        from mud.systems.monster_races import get_race_icon, get_race_name
                        race_info = f" {get_race_icon(monster.race_id)} {Colors.TYPE}[{get_race_name(monster.race_id)}]{Colors.RESET}"
                    
                    # Monta texto com informações do monstro
                    from mud.utils.visuals import format_monster_hp_bar
                    monster_info = f"{Colors.LABEL}[{monster_instance_id}]{Colors.RESET} {Colors.MONSTER}{monster.name}{Colors.RESET}{race_info}{level_info}{weapon_info}"
                    monster_info += f"\r\n{format_monster_hp_bar(monster.current_hp, monster.max_hp, 'HP')}"
                    
                    # Formata monstro com ASCII à esquerda e informações à direita
                    formatted_monster = format_ascii_with_text(monster_ascii, monster_info, ascii_width=22)
                    message += f"{formatted_monster}\r\n\r\n"
        
        # NPCs
        if entities['npcs']:
            message += f"{Colors.NPC}NPCs aqui:{Colors.RESET}\r\n"
            from mud.utils.visuals import get_npc_ascii, format_ascii_with_text
            for npc_id in entities['npcs']:
                npc = self.game_data.get_npc(player.world_id, npc_id)
                if npc:
                    npc_ascii = get_npc_ascii(npc.npc_type)
                    # Formata NPC com ASCII à esquerda e informações à direita
                    npc_info = f"{Colors.NPC}{npc.name}{Colors.RESET}"
                    if npc.description:
                        npc_info += f" {Colors.DESCRIPTION}{npc.description}{Colors.RESET}"
                    formatted_npc = format_ascii_with_text(npc_ascii, npc_info, ascii_width=22)
                    message += f"{formatted_npc}\r\n\r\n"
        
        # Itens no chão
        if entities['items']:
            message += f"\r\n{Colors.ITEM}Itens aqui:{Colors.RESET} "
            item_names = []
            for item_id in entities['items']:
                item = self.game_data.get_item(item_id)
                if item:
                    item_names.append(f"{Colors.ITEM}{item.name}{Colors.RESET}")
            message += f"{', '.join(item_names)}\r\n"
        
        # Mostra saídas disponíveis
        if room.exits:
            exits = list(room.exits.keys())
            message += f"\r\n{Colors.INFO}Saídas:{Colors.RESET} {Colors.COMMAND}{', '.join(exits)}{Colors.RESET}\r\n"
        
        # Mostra portas de dungeon se houver
        if self.dungeon_manager:
            dungeon = self.dungeon_manager.get_dungeon_by_entry_room(player.world_id, player.room_id)
            if dungeon:
                message += f"\r\n{Colors.CATEGORY}Porta:{Colors.RESET} {Colors.ITEM}{dungeon['name']}{Colors.RESET}\r\n"
                message += f"{Colors.HINT}Use: {Colors.COMMAND}{dungeon.get('entry_command', 'entrar')}{Colors.RESET}\r\n"
        
        # Mostra outros jogadores na sala
        other_players = [p.name for p in self.game.get_players_in_room(player.world_id, player.room_id) if p.name != player.name]
        if other_players:
            message += f"\r\n{Colors.WARNING}Também aqui:{Colors.RESET} {Colors.PLAYER}{', '.join(other_players)}{Colors.RESET}\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_move(self, player: Player, direction: str):
        """Comando move - move o jogador para outra sala"""
        # Verifica se o jogador está em combate
        if player.name in self.in_combat:
            await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode sair da sala até o combate acabar.{ANSI.RESET}")
            return
        
        # Tenta buscar na sala normal primeiro, depois em dungeon
        room = self.world_manager.get_room(player.world_id, player.room_id, self.dungeon_manager)
        if not room:
            return
        
        if direction not in room.exits:
            await self.send_message(player, f"{ANSI.RED}Não há saída para {direction}.{ANSI.RESET}")
            return
        
        old_room_id = player.room_id
        new_room_id = room.exits[direction]
        
        # Se sair de dungeon, volta para o mundo normal
        if direction == 'sair' and self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, player.room_id):
            dungeon = self.dungeon_manager.get_dungeon_for_room(player.world_id, player.room_id)
            if dungeon:
                dungeon_data = self.dungeon_manager.get_dungeon_info(player.world_id, dungeon)
                if dungeon_data:
                    entry_room = dungeon_data.get('entry_room')
                    if entry_room:
                        new_room_id = entry_room
                        new_room = self.world_manager.get_room(player.world_id, new_room_id, self.dungeon_manager)
                    else:
                        new_room = self.world_manager.get_room(player.world_id, new_room_id, self.dungeon_manager)
                else:
                    new_room = self.world_manager.get_room(player.world_id, new_room_id, self.dungeon_manager)
            else:
                new_room = self.world_manager.get_room(player.world_id, new_room_id, self.dungeon_manager)
        else:
            new_room = self.world_manager.get_room(player.world_id, new_room_id, self.dungeon_manager)
        
        if not new_room:
            await self.send_message(player, f"{ANSI.RED}Erro: sala de destino não encontrada.{ANSI.RESET}")
            return
        
        # Remove de combate se estiver
        if player.name in self.in_combat:
            del self.in_combat[player.name]
        
        # Move o jogador
        player.room_id = new_room_id
        
        # Se entrou em dungeon, spawna monstros e itens
        if self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, new_room_id):
            await self._spawn_dungeon_entities(player, new_room_id)
        
        # Limpa instâncias de monstros da sala antiga (se não estiver mais lá)
        if old_room_id != new_room_id:
            # Não limpa imediatamente, pode ter outros jogadores na sala
            pass
        
        # Salva no banco de dados
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        
        # Notifica outros jogadores na sala antiga
        await self.game.broadcast_to_room(
            player.world_id,
            old_room_id,
            f"{player.name} sai para {direction}.",
            exclude_player=player.name
        )
        
        # Notifica outros jogadores na nova sala
        await self.game.broadcast_to_room(
            player.world_id,
            new_room_id,
            f"{player.name} entra.",
            exclude_player=player.name
        )
        
        # Spawna monstros baseado na configuração da sala (se não estiver em dungeon e não estiver no lobby)
        if (new_room_id != "lobby" and 
            not (self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, new_room_id))):
            await self._spawn_room_monsters(player)
        
        # Mostra a nova sala para o jogador
        await self.cmd_look(player)
        
        # Verifica se há monstros agressivos que devem atacar automaticamente (não no lobby)
        if new_room_id != "lobby":
            await self._handle_aggressive_monsters(player)
    
    async def _handle_player_death(self, player: Player):
        """Trata a morte do jogador: teleporta para lobby, remove item aleatório, restaura HP"""
        import random
        
        # Remove do combate
        if player.name in self.in_combat:
            del self.in_combat[player.name]
        
        # Remove 1 item aleatório do inventário (se tiver itens)
        lost_item = None
        if player.inventory and len(player.inventory) > 0:
            # Escolhe um item aleatório do inventário
            lost_item_id = random.choice(player.inventory)
            player.remove_item(lost_item_id)
            # Busca o nome do item para mostrar na mensagem
            lost_item = self.game_data.get_item(lost_item_id)
        
        # Teleporta para o lobby
        old_room_id = player.room_id
        player.room_id = "lobby"
        
        # Restaura HP ao máximo
        player.current_hp = player.max_hp
        
        # Salva no banco de dados
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns,
            'unspent_points': player.unspent_points
        }
        self.database.update_player_stats(player.name, stats)
        
        # Notifica outros jogadores na sala antiga
        await self.game.broadcast_to_room(
            player.world_id,
            old_room_id,
            f"{player.name} foi derrotado e desapareceu.",
            exclude_player=player.name
        )
        
        # Mostra mensagem ao jogador
        await self.send_message(player, f"{ANSI.BRIGHT_RED}Você foi derrotado!{ANSI.RESET}\r\n")
        
        if lost_item:
            await self.send_message(player, f"{ANSI.YELLOW}Você perdeu: {lost_item.name}{ANSI.RESET}\r\n")
        
        await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Você foi transportado de volta ao Hall de Entrada.{ANSI.RESET}\r\n")
        
        # Mostra a sala do lobby
        await self.cmd_look(player)
    
    async def cmd_enter(self, player: Player, target: str):
        """Comando enter - entra em uma dungeon/porta ou usa saída normal 'entrar'"""
        # Verifica se o jogador está em combate
        if player.name in self.in_combat:
            await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode sair da sala até o combate acabar.{ANSI.RESET}")
            return
        
        # Primeiro verifica se 'entrar' é uma saída normal da sala
        room = self.world_manager.get_room(player.world_id, player.room_id, self.dungeon_manager)
        if room and 'entrar' in room.exits:
            # Se 'entrar' é uma saída normal, usa movimento normal
            await self.cmd_move(player, 'entrar')
            return
        
        # Se não é saída normal, procura por dungeon
        if not self.dungeon_manager:
            await self.send_message(player, f"{ANSI.YELLOW}Sistema de dungeons não disponível.{ANSI.RESET}")
            return
        
        # Verifica se há dungeon disponível na sala atual
        dungeon = self.dungeon_manager.get_dungeon_by_entry_room(player.world_id, player.room_id)
        if not dungeon:
            await self.send_message(player, f"{ANSI.YELLOW}Não há dungeon ou porta aqui.{ANSI.RESET}")
            return
        
        # Verifica se o comando corresponde (flexível - aceita se target está no entry_command ou se entry_command está vazio)
        entry_command = dungeon.get('entry_command', '').lower()
        if entry_command:
            # Se há um comando específico, verifica se o target corresponde
            if target:
                # Remove "entrar" do início se presente para comparar apenas o objeto
                target_clean = target.lower().replace('entrar', '').strip()
                entry_clean = entry_command.lower().replace('entrar', '').strip()
                
                # Verifica se o target está no comando ou vice-versa
                if target_clean not in entry_clean and entry_clean not in target_clean:
                    await self.send_message(player, f"{ANSI.YELLOW}Use: {dungeon.get('entry_command', 'entrar')}{ANSI.RESET}")
                    return
            else:
                # Se não há target, mostra o comando correto
                await self.send_message(player, f"{ANSI.YELLOW}Use: {dungeon.get('entry_command', 'entrar')}{ANSI.RESET}")
                return
        
        # Entra na dungeon
        entry_room_id = self.dungeon_manager.get_dungeon_entry_room(player.world_id, dungeon['id'])
        if not entry_room_id:
            await self.send_message(player, f"{ANSI.RED}Erro ao entrar na dungeon.{ANSI.RESET}")
            return
        
        old_room_id = player.room_id
        player.room_id = entry_room_id
        
        # Spawna monstros e itens na entrada
        await self._spawn_dungeon_entities(player, entry_room_id)
        
        # Salva no banco
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        
        # Notifica
        await self.game.broadcast_to_room(
            player.world_id,
            old_room_id,
            f"{player.name} entra na {dungeon['name']}.",
            exclude_player=player.name
        )
        
        await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Você entra na {dungeon['name']}...{ANSI.RESET}")
        await self.cmd_look(player)
        
        # Verifica se há monstros agressivos que devem atacar automaticamente (não no lobby)
        if entry_room_id != "lobby":
            await self._handle_aggressive_monsters(player)
    
    async def cmd_exit_dungeon(self, player: Player):
        """Comando sair - sai de uma dungeon"""
        # Verifica se o jogador está em combate
        if player.name in self.in_combat:
            await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode sair da sala até o combate acabar.{ANSI.RESET}")
            return
        
        if not self.dungeon_manager:
            await self.send_message(player, f"{ANSI.YELLOW}Sistema de dungeons não disponível.{ANSI.RESET}")
            return
        
        if not self.dungeon_manager.is_dungeon_room(player.world_id, player.room_id):
            await self.send_message(player, f"{ANSI.YELLOW}Você não está em uma dungeon.{ANSI.RESET}")
            return
        
        dungeon = self.dungeon_manager.get_dungeon_for_room(player.world_id, player.room_id)
        if not dungeon:
            await self.send_message(player, f"{ANSI.RED}Erro ao sair da dungeon.{ANSI.RESET}")
            return
        
        dungeon_data = self.dungeon_manager.get_dungeon_info(player.world_id, dungeon)
        if not dungeon_data:
            await self.send_message(player, f"{ANSI.RED}Erro ao sair da dungeon.{ANSI.RESET}")
            return
        
        entry_room = dungeon_data.get('entry_room')
        if not entry_room:
            await self.send_message(player, f"{ANSI.RED}Erro: sala de entrada não encontrada.{ANSI.RESET}")
            return
        
        old_room_id = player.room_id
        player.room_id = entry_room
        
        # Salva no banco
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        
        # Notifica
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você saiu da dungeon.{ANSI.RESET}")
        await self.cmd_look(player)
    
    async def _spawn_dungeon_entities(self, player: Player, room_id: str):
        """Spawna monstros e itens em uma sala de dungeon"""
        if not self.dungeon_manager:
            return
        
        # Limpa respawns expirados
        self.database.cleanup_old_respawns(player.world_id, room_id)
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Pega lista de monstros que podem spawnar nesta sala
        monster_ids = self.dungeon_manager.get_room_monsters(player.world_id, room_id)
        
        if monster_ids:
            # Verifica quantos monstros vivos existem de cada tipo
            alive_instances = {}
            if player.world_id in self.monster_instances and room_id in self.monster_instances[player.world_id]:
                for instance_id, instance in self.monster_instances[player.world_id][room_id].items():
                    if instance.is_alive() and instance.id in monster_ids:
                        if instance.id not in alive_instances:
                            alive_instances[instance.id] = []
                        alive_instances[instance.id].append(instance_id)
            
            # Conta quantos de cada tipo devem existir
            required_counts = {}
            for monster_id in monster_ids:
                required_counts[monster_id] = required_counts.get(monster_id, 0) + 1
            
            # Verifica quais monstros podem respawnar
            room_respawns = self.database.get_room_respawns(player.world_id, room_id)
            
            for monster_id in monster_ids:
                current_count = len(alive_instances.get(monster_id, []))
                required_count = required_counts.get(monster_id, 1)
                
                # Verifica quantos deste tipo podem respawnar
                can_respawn_count = 0
                for key, respawn_info in room_respawns.items():
                    if respawn_info['monster_id'] == monster_id and respawn_info['can_respawn']:
                        can_respawn_count += 1
                
                # Se precisa de mais monstros e pode respawnar (ou não há nenhum vivo)
                if current_count < required_count:
                    if current_count == 0 or can_respawn_count > 0:
                        # Adiciona monstros que podem respawnar
                        monsters_to_add = min(required_count - current_count, required_count)
                        for _ in range(monsters_to_add):
                            if monster_id not in entities['monsters']:
                                entities['monsters'].append(monster_id)
        
        # Garante instâncias para os novos monstros (verificando respawns)
        await self._ensure_monster_instances(player.world_id, room_id, entities['monsters'])
        
        # Spawna itens (chance menor)
        import random
        item_ids = self.dungeon_manager.get_room_items(player.world_id, room_id)
        for item_id in item_ids:
            if random.random() < 0.3:  # 30% de chance de spawnar cada item
                if item_id not in entities['items']:
                    entities['items'].append(item_id)
    
    async def _ensure_monster_instances(self, world_id: str, room_id: str, monster_templates: List[str]):
        """Garante que todos os monstros da sala têm instâncias criadas com IDs únicos"""
        if world_id not in self.monster_instances:
            self.monster_instances[world_id] = {}
        if room_id not in self.monster_instances[world_id]:
            self.monster_instances[world_id][room_id] = {}
        
        if world_id not in self.monster_id_counter:
            self.monster_id_counter[world_id] = {}
        if room_id not in self.monster_id_counter[world_id]:
            self.monster_id_counter[world_id][room_id] = 0
        
        # Remove instâncias mortas primeiro
        dead_instances = []
        for instance_id, instance in self.monster_instances[world_id][room_id].items():
            if not instance.is_alive():
                dead_instances.append(instance_id)
        for instance_id in dead_instances:
            del self.monster_instances[world_id][room_id][instance_id]
        
        # Conta quantas instâncias de cada tipo já existem
        instance_counts: Dict[str, int] = {}
        for instance_id, instance in self.monster_instances[world_id][room_id].items():
            if instance.is_alive():
                instance_counts[instance.id] = instance_counts.get(instance.id, 0) + 1
        
        # Verifica respawns pendentes
        room_respawns = self.database.get_room_respawns(world_id, room_id)
        
        # Cria instâncias para monstros que ainda não têm (ou que precisam de mais)
        for monster_template_id in monster_templates:
            # Conta quantas instâncias deste template já existem
            existing_count = instance_counts.get(monster_template_id, 0)
            # Conta quantas deste template deveriam existir
            required_count = monster_templates.count(monster_template_id)
            
            # Verifica quantas instâncias deste tipo podem respawnar
            can_respawn_for_this_type = 0
            for key, respawn_info in room_respawns.items():
                if respawn_info['monster_id'] == monster_template_id and respawn_info['can_respawn']:
                    can_respawn_for_this_type += 1
            
            # Cria instâncias faltantes (apenas se pode respawnar ou se não há nenhuma)
            while existing_count < required_count:
                # Verifica se pode criar nova instância (não há respawn pendente ou já pode respawnar)
                if existing_count == 0 or can_respawn_for_this_type > 0:
                    monster_template = self.game_data.monsters.get(world_id, {}).get(monster_template_id)
                    if monster_template:
                        # Determina o nível do monstro baseado na sala
                        monster_level = None
                        # Se está em dungeon, verifica min_level/max_level da sala
                        if self.dungeon_manager and self.dungeon_manager.is_dungeon_room(world_id, room_id):
                            dungeon_room_data = self.dungeon_manager.get_room_data(world_id, room_id)
                            if dungeon_room_data:
                                min_level = dungeon_room_data.get('min_level', monster_template.level_min)
                                max_level = dungeon_room_data.get('max_level', monster_template.level_max)
                                import random
                                monster_level = random.randint(min_level, max_level)
                        # Se não está em dungeon, usa configuração da sala
                        else:
                            min_level, max_level = self.game_data.get_room_level_range(world_id, room_id)
                            if min_level and max_level:
                                import random
                                monster_level = random.randint(min_level, max_level)
                        
                        monster_instance = self.game_data.get_monster(world_id, monster_template_id, monster_level)
                        if monster_instance:
                            # Incrementa contador e atribui ID
                            self.monster_id_counter[world_id][room_id] += 1
                            instance_id = self.monster_id_counter[world_id][room_id]
                            
                            # Verifica se esta instância específica pode respawnar
                            can_create = True
                            for key, respawn_info in room_respawns.items():
                                if (respawn_info['monster_id'] == monster_template_id and 
                                    respawn_info['instance_id'] == instance_id and 
                                    not respawn_info['can_respawn']):
                                    can_create = False
                                    break
                            
                            if can_create:
                                self.monster_instances[world_id][room_id][instance_id] = monster_instance
                                existing_count += 1
                                # Remove registro de respawn se existir
                                self.database.cleanup_old_respawns(world_id, room_id)
                    else:
                        break  # Template não existe, para o loop
                else:
                    break  # Não pode criar mais, espera respawn
    
    async def _spawn_room_monsters(self, player: Player):
        """
        Spawna monstros em uma sala baseado na configuração (rooms_config.json).
        Respeita os níveis min/max da sala.
        """
        if not self.game_data.should_spawn_monsters_in_room(player.world_id, player.room_id):
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        monster_templates = self.game_data.get_room_monsters(player.world_id, player.room_id)
        min_level, max_level = self.game_data.get_room_level_range(player.world_id, player.room_id)
        
        # Verifica quantos monstros já existem
        existing_count = len([m for m in entities['monsters'] if m in monster_templates])
        required_count = len(monster_templates)
        
        # Spawna monstros faltantes
        if existing_count < required_count:
            import random
            for monster_id in monster_templates:
                if monster_id not in entities['monsters'] or entities['monsters'].count(monster_id) < monster_templates.count(monster_id):
                    # Adiciona à lista de monstros da sala
                    entities['monsters'].append(monster_id)
    
    async def _handle_aggressive_monsters(self, player: Player):
        """
        Verifica se há monstros agressivos na sala e os faz atacar automaticamente.
        Retorna True se o player foi atacado.
        """
        # Verifica se a sala tem monstros agressivos
        is_aggressive = self.game_data.is_room_aggressive(player.world_id, player.room_id)
        
        # Verifica também se está em uma dungeon com monstros agressivos
        if self.dungeon_manager and self.dungeon_manager.is_dungeon_room(player.world_id, player.room_id):
            dungeon_room_data = self.dungeon_manager.get_room_data(player.world_id, player.room_id)
            if dungeon_room_data and dungeon_room_data.get('aggressive_monsters', False):
                is_aggressive = True
        
        if not is_aggressive:
            return False
        
        # Garante que há instâncias de monstros
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        await self._ensure_monster_instances(player.world_id, player.room_id, entities['monsters'])
        
        monster_instances = self.monster_instances[player.world_id].get(player.room_id, {})
        
        if not monster_instances:
            return False
        
        # Pega um monstro aleatório vivo para atacar
        alive_monsters = [m for m in monster_instances.values() if m and m.is_alive()]
        if not alive_monsters:
            return False
        
        import random
        attacking_monster = random.choice(alive_monsters)
        
        # Monstro ataca o player
        await self.send_message(player, 
            f"{ANSI.BRIGHT_RED}⚠ {attacking_monster.name} te ataca sem aviso! ⚠{ANSI.RESET}\r\n")
        
        # Usa o sistema de combate para o monstro atacar
        from mud.systems.combat import CombatSystem
        monster_damage = attacking_monster.get_attack_damage()
        total_defense = player.get_total_defense(self.game_data)
        actual_damage = player.take_damage(monster_damage, total_defense)
        
        weapon_info = ""
        if attacking_monster.weapon:
            weapon_info = f" com {attacking_monster.weapon}"
        
        level_info = f" [Nível {attacking_monster.level}]" if attacking_monster.level > 1 else ""
        await self.send_message(player,
            f"{ANSI.RED}👹 {attacking_monster.name}{level_info} ataca você{weapon_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n")
        
        # Mostra barras de HP e Stamina do jogador
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
        player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
        await self.send_message(player, f"{player_hp_bar}\r\n")
        await self.send_message(player, f"{player_stamina_bar}\r\n")
        
        if not player.is_alive():
            await self._handle_player_death(player)
            return
        
        # Salva stats do player
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp
        }
        self.database.update_player_stats(player.name, stats)
        
        return True
    
    async def _spawn_random_slimes(self, player: Player):
        """
        Spawna slimes aleatoriamente em salas específicas.
        Slimes só aparecem em salas novas (pantano, ruinas, etc) e têm chance de spawnar.
        Slimes são passivos - só atacam quando são atacados primeiro.
        """
        # Salas onde slimes podem spawnar aleatoriamente
        slime_rooms = ['pantano', 'ruinas', 'bosque_elfico', 'templo_antigo', 'pico_montanha', 'caverna_profunda',
                       'pantano_profundo', 'ilha_pantano', 'catacumbas', 'sala_arcana', 'vale_escondido', 
                       'mirante_estrelas', 'torre_abandonada', 'topo_torre', 'lago_cristalino', 'cachoeira_oculta', 
                       'gruta_secreta']
        
        if player.room_id not in slime_rooms:
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Verifica se já tem slimes vivos nesta sala
        has_slime = False
        if (player.world_id in self.monster_instances and 
            player.room_id in self.monster_instances[player.world_id]):
            for instance in self.monster_instances[player.world_id][player.room_id].values():
                if instance.id == 'slime' and instance.is_alive():
                    has_slime = True
                    break
        
        # Se não tem slime, tem chance de spawnar (30%)
        if not has_slime:
            import random
            if random.random() < 0.3:  # 30% de chance
                if 'slime' not in entities['monsters']:
                    entities['monsters'].append('slime')
    
    async def _show_combat_menu(self, player: Player):
        """Mostra o menu de combate estilo Pokémon"""
        if player.name not in self.in_combat:
            return
        
        # Obtém informações do combate atual
        combat_key = self.in_combat[player.name]
        world_id, room_id, monster_instance_id = combat_key.split(':')
        monster_instance_id = int(monster_instance_id)
        
        monster_instances = self.monster_instances.get(world_id, {}).get(room_id, {})
        monster = monster_instances.get(monster_instance_id)
        
        if not monster or not monster.is_alive():
            # Monstro morreu, limpa combate
            if player.name in self.in_combat:
                del self.in_combat[player.name]
            if player.name in self.combat_state:
                del self.combat_state[player.name]
            return
        
        # Monta menu
        message = f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_RED}=== COMBATE ==={ANSI.RESET}\r\n\r\n"
        
        # Informações do monstro
        from mud.utils.visuals import format_monster_hp_bar
        level_info = f" [Nível {monster.level}]" if monster.level > 1 else ""
        message += f"{ANSI.BRIGHT_RED}Monstro:{ANSI.RESET} {monster.name}{level_info}\r\n"
        message += f"{format_monster_hp_bar(monster.current_hp, monster.max_hp, 'HP')}\r\n\r\n"
        
        # Informações do jogador
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        message += f"{ANSI.BRIGHT_GREEN}Você:{ANSI.RESET} {player.name}\r\n"
        message += f"{format_hp_bar(player.current_hp, player.max_hp)}\r\n"
        message += f"{format_stamina_bar(player.current_stamina, player.max_stamina)}\r\n\r\n"
        
        # Opções do menu
        message += f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}Escolha sua ação:{ANSI.RESET}\r\n"
        message += f"  {ANSI.BRIGHT_YELLOW}1{ANSI.RESET} - {ANSI.BRIGHT_GREEN}Ataque{ANSI.RESET}\r\n"
        
        # Magias equipadas
        menu_option = 2
        available_spells = []
        if player.equipped_spells:
            for spell_id in player.equipped_spells:
                spell = self.spell_system.get_spell(spell_id)
                if spell:
                    import time
                    # Verifica cooldown
                    cooldown_ok = True
                    if spell_id in player.spell_cooldowns:
                        cooldown_end = player.spell_cooldowns[spell_id]
                        if time.time() < cooldown_end:
                            cooldown_ok = False
                    
                    # Verifica stamina
                    spell_level = player.get_spell_level(spell_id)
                    cost = self.spell_system.calculate_spell_cost(spell, spell_level)
                    stamina_ok = player.has_stamina(cost)
                    
                    if cooldown_ok and stamina_ok:
                        available_spells.append((menu_option, spell_id, spell, cost))
                        message += f"  {ANSI.BRIGHT_YELLOW}{menu_option}{ANSI.RESET} - {ANSI.BRIGHT_MAGENTA}{spell.name}{ANSI.RESET} (Stamina: {cost})\r\n"
                        menu_option += 1
        
        # Itens consumíveis no inventário
        available_items = []
        for item_id in player.inventory:
            item = self.game_data.get_item(item_id)
            if item and item.type == 'consumable':
                available_items.append((menu_option, item_id, item))
                # Mostra efeito do item
                effects = []
                if 'hp' in item.stats:
                    effects.append(f"+{item.stats['hp']} HP")
                if 'stamina' in item.stats:
                    effects.append(f"+{item.stats['stamina']} Stamina")
                effects_str = ", ".join(effects) if effects else "Efeito"
                message += f"  {ANSI.BRIGHT_YELLOW}{menu_option}{ANSI.RESET} - {ANSI.BRIGHT_CYAN}{item.name}{ANSI.RESET} ({effects_str})\r\n"
                menu_option += 1
                if menu_option > 9:  # Limita a 9 opções
                    break
        
        message += f"\r\n{ANSI.BRIGHT_BLACK}Digite o número da ação (1-{menu_option-1}):{ANSI.RESET}\r\n"
        
        # Armazena estado do combate para processar escolhas
        self.combat_state[player.name] = {
            'monster_instance_id': monster_instance_id,
            'world_id': world_id,
            'room_id': room_id,
            'available_spells': available_spells,
            'available_items': available_items,
            'max_option': menu_option - 1
        }
        
        await self.send_message(player, message)
    
    async def _handle_combat_menu_choice(self, player: Player, choice: int):
        """Processa escolha do menu de combate"""
        if player.name not in self.in_combat or player.name not in self.combat_state:
            await self._show_combat_menu(player)
            return
        
        combat_info = self.combat_state[player.name]
        monster_instance_id = combat_info['monster_instance_id']
        world_id = combat_info['world_id']
        room_id = combat_info['room_id']
        
        if choice < 1 or choice > combat_info['max_option']:
            await self.send_message(player, f"{ANSI.RED}Opção inválida! Escolha entre 1 e {combat_info['max_option']}.{ANSI.RESET}")
            await self._show_combat_menu(player)
            return
        
        monster_instances = self.monster_instances.get(world_id, {}).get(room_id, {})
        monster = monster_instances.get(monster_instance_id)
        
        if not monster or not monster.is_alive():
            # Monstro morreu
            if player.name in self.in_combat:
                del self.in_combat[player.name]
            if player.name in self.combat_state:
                del self.combat_state[player.name]
            return
        
        # Opção 1 = Ataque básico
        if choice == 1:
            await self._execute_combat_attack(player, monster, monster_instance_id, world_id, room_id)
        else:
            # Verifica se é uma magia
            found_spell = None
            for opt_num, spell_id, spell, cost in combat_info['available_spells']:
                if opt_num == choice:
                    found_spell = (spell_id, spell, cost)
                    break
            
            if found_spell:
                spell_id, spell, cost = found_spell
                await self._execute_combat_spell(player, monster, monster_instance_id, world_id, room_id, spell_id, spell, cost)
            else:
                # Verifica se é um item
                found_item = None
                for opt_num, item_id, item in combat_info['available_items']:
                    if opt_num == choice:
                        found_item = (item_id, item)
                        break
                
                if found_item:
                    item_id, item = found_item
                    await self._execute_combat_item(player, monster, monster_instance_id, world_id, room_id, item_id, item)
                else:
                    await self.send_message(player, f"{ANSI.RED}Opção inválida!{ANSI.RESET}")
                    await self._show_combat_menu(player)
    
    async def _execute_combat_attack(self, player: Player, monster: Monster, monster_instance_id: int, world_id: str, room_id: str):
        """Executa ataque básico no combate"""
        # Ataque do jogador
        result = await CombatSystem.attack_monster(
            player, monster,
            lambda msg: self.send_message(player, msg),
            self.game_data
        )
        
        # Verifica se o jogador morreu
        if result == "player_died" or not player.is_alive():
            await self._handle_player_death(player)
            return
        
        # Se o monstro morreu, processa morte e verifica próximo monstro
        if result:
            await self._handle_monster_death(player, monster, monster_instance_id, world_id, room_id)
        else:
            # Monstro ainda vivo, mostra menu novamente
            await self._show_combat_menu(player)
    
    async def _execute_combat_spell(self, player: Player, monster: Monster, monster_instance_id: int, world_id: str, room_id: str, spell_id: str, spell, cost: int):
        """Executa magia no combate"""
        import time
        
        # Verifica stamina novamente
        if not player.has_stamina(cost):
            await self.send_message(player, f"{ANSI.RED}Stamina insuficiente!{ANSI.RESET}")
            await self._show_combat_menu(player)
            return
        
        # Gasta stamina
        player.use_stamina(cost)
        
        # Aplica cooldown
        player.spell_cooldowns[spell_id] = time.time() + spell.cooldown
        
        # Animação de magia
        from mud.utils.visuals import get_spell_animation, get_heal_animation
        import asyncio
        
        if spell.damage_type == 'heal':
            animation = get_heal_animation()
            for frame in animation:
                await self.send_message(player, f"\r{ANSI.BRIGHT_MAGENTA}{frame}{ANSI.RESET}")
                await asyncio.sleep(0.1)
            
            # Cura
            spell_level = player.get_spell_level(spell_id)
            from mud.systems.classes import ClassSystem
            class_system = ClassSystem()
            race = class_system.get_race(player.race_id) if player.race_id else None
            race_bonus = 1.0
            
            heal_amount = self.spell_system.calculate_spell_damage(
                spell, player.level, player.attack, spell_level, race_bonus
            )
            player.heal(heal_amount)
            from mud.utils.visuals import format_hp_bar
            await self.send_message(player, f"\r{ANSI.BRIGHT_GREEN}✨ Você lança {spell.name} e se cura {heal_amount} de HP! ✨{ANSI.RESET}\r\n")
            await self.send_message(player, f"{format_hp_bar(player.current_hp, player.max_hp)}\r\n")
            
            # Após usar item/magia, monstros atacam
            await self._monsters_turn(player, monster, monster_instance_id, world_id, room_id)
        else:
            # Magia de dano
            animation = get_spell_animation()
            for frame in animation:
                await self.send_message(player, f"\r{ANSI.BRIGHT_MAGENTA}{frame}{ANSI.RESET}")
                await asyncio.sleep(0.1)
            
            # Chance de falha
            import random
            spell_level = player.get_spell_level(spell_id)
            fail_chance = max(0.05, 0.15 - (spell_level * 0.02))
            if random.random() < fail_chance:
                await self.send_message(player, f"\r{ANSI.RED}❌ Sua magia {spell.name} falhou! ❌{ANSI.RESET}\r\n")
                await self._monsters_turn(player, monster, monster_instance_id, world_id, room_id)
                return
            
            # Calcula dano
            spell_level = player.get_spell_level(spell_id)
            from mud.systems.classes import ClassSystem
            class_system = ClassSystem()
            race = class_system.get_race(player.race_id) if player.race_id else None
            race_bonus = 1.0
            
            damage = self.spell_system.calculate_spell_damage(
                spell, player.level, player.attack, spell_level, race_bonus
            )
            
            # Aplica dano
            actual_damage = monster.take_damage(damage, spell.damage_type)
            
            damage_icon = "🔥" if spell.damage_type == "fire" else "❄" if spell.damage_type == "ice" else "⚡" if spell.damage_type == "lightning" else "✨"
            await self.send_message(player, f"\r{ANSI.BRIGHT_GREEN}{damage_icon} Você lança {spell.name} em {monster.name} causando {actual_damage} de dano! {damage_icon}{ANSI.RESET}\r\n")
            
            from mud.utils.visuals import format_monster_hp_bar, get_hp_color
            hp_color = get_hp_color(monster.current_hp, monster.max_hp)
            monster_hp_display = f"{hp_color}{monster.name} HP:{ANSI.RESET} {format_monster_hp_bar(monster.current_hp, monster.max_hp)}"
            await self.send_message(player, f"{monster_hp_display}\r\n")
            
            # Verifica se o monstro morreu
            if not monster.is_alive():
                await self._handle_monster_death(player, monster, monster_instance_id, world_id, room_id)
            else:
                # Monstro ainda vivo, monstros atacam
                await self._monsters_turn(player, monster, monster_instance_id, world_id, room_id)
    
    async def _execute_combat_item(self, player: Player, monster: Monster, monster_instance_id: int, world_id: str, room_id: str, item_id: str, item):
        """Executa uso de item no combate"""
        # Aplica efeitos do item
        effects_applied = []
        hp_healed = 0
        stamina_restored = 0
        
        if 'hp' in item.stats:
            old_hp = player.current_hp
            player.heal(item.stats['hp'])
            hp_healed = player.current_hp - old_hp
            if hp_healed > 0:
                effects_applied.append(f"{hp_healed} de HP")
        
        if 'stamina' in item.stats:
            old_stamina = player.current_stamina
            player.restore_stamina(item.stats['stamina'])
            stamina_restored = player.current_stamina - old_stamina
            if stamina_restored > 0:
                effects_applied.append(f"{stamina_restored} de stamina")
        
        if not effects_applied:
            await self.send_message(player, f"{ANSI.YELLOW}{item.name} não teve efeito.{ANSI.RESET}")
            await self._show_combat_menu(player)
            return
        
        # Remove item do inventário
        player.remove_item(item_id)
        
        # Mensagem de sucesso
        effects_text = ", ".join(effects_applied)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você usou {item.name} e recuperou {effects_text}!{ANSI.RESET}\r\n")
        
        # Mostra barras atualizadas
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        if hp_healed > 0:
            await self.send_message(player, f"{format_hp_bar(player.current_hp, player.max_hp)}\r\n")
        if stamina_restored > 0:
            await self.send_message(player, f"{format_stamina_bar(player.current_stamina, player.max_stamina)}\r\n")
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns
        }
        self.database.update_player_stats(player.name, stats)
        
        # Após usar item, monstros atacam
        await self._monsters_turn(player, monster, monster_instance_id, world_id, room_id)
    
    async def _monsters_turn(self, player: Player, monster: Monster, monster_instance_id: int, world_id: str, room_id: str):
        """Executa turno dos monstros (após jogador usar item ou magia)"""
        import asyncio
        await asyncio.sleep(0.3)
        
        if not monster.is_alive():
            await self._handle_monster_death(player, monster, monster_instance_id, world_id, room_id)
            return
        
        # Monstro ataca
        monster_damage = monster.get_attack_damage()
        total_defense = player.get_total_defense(self.game_data)
        actual_damage = player.take_damage(monster_damage, total_defense)
        
        level_info = f" [Nível {monster.level}]" if monster.level > 1 else ""
        weapon_info = ""
        if monster.weapon:
            weapon_info = f" com {monster.weapon}"
        
        await self.send_message(player, f"{ANSI.RED}👹 {monster.name}{level_info} ataca você{weapon_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n")
        
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
        player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
        await self.send_message(player, f"{player_hp_bar}\r\n")
        await self.send_message(player, f"{player_stamina_bar}\r\n")
        
        if not player.is_alive():
            await self._handle_player_death(player)
            return
        
        # Mostra menu novamente
        await self._show_combat_menu(player)
    
    async def _handle_monster_death(self, player: Player, monster: Monster, monster_instance_id: int, world_id: str, room_id: str):
        """Processa morte do monstro e verifica se há mais monstros para combater"""
            # Remove instância do monstro
        if monster_instance_id in self.monster_instances.get(world_id, {}).get(room_id, {}):
            del self.monster_instances[world_id][room_id][monster_instance_id]
            
            # Remove template da lista de entidades da sala
        self.game_data.remove_monster_from_room(world_id, room_id, monster.id)
        
        # Limpa estado de combate
        if player.name in self.in_combat:
            del self.in_combat[player.name]
        if player.name in self.combat_state:
            del self.combat_state[player.name]
            
        # Registra morte do monstro para sistema de respawn (5 minutos mínimo)
            import random
            if self.dungeon_manager:
                respawn_config = self.dungeon_manager.get_room_respawn_time(
                world_id, room_id, monster.id
                )
            # Garante mínimo de 5 minutos (300 segundos)
            if respawn_config['min'] < 300:
                respawn_config['min'] = 300
            if respawn_config['max'] < 300:
                respawn_config['max'] = 300
        else:
            respawn_config = {'min': 300, 'max': 600}  # 5-10 minutos
        
        respawn_time = random.randint(respawn_config['min'], respawn_config['max'])
        self.database.register_monster_death(
            world_id, room_id, monster.id, monster_instance_id, respawn_time
        )
        
        # Experiência
        exp_gained = CombatSystem.calculate_experience(monster)
        player.experience += exp_gained
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você ganhou {exp_gained} de experiência!{ANSI.RESET}\r\n")
        
        # Verifica level up
        await self._check_level_up(player)
        
        # Salva experiência e nível
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns,
            'unspent_points': player.unspent_points
        }
        self.database.update_player_stats(player.name, stats)
        
        # Ouro
        gold_gained = CombatSystem.drop_gold(monster)
        if gold_gained > 0:
            player.add_gold(gold_gained)
            await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Você recebeu {gold_gained} moedas!{ANSI.RESET}\r\n")
        
        # Loot
        loot_item = CombatSystem.drop_loot(monster)
        if loot_item:
            entities = self.game_data.get_room_entities(world_id, room_id)
            entities['items'].append(loot_item)
            item = self.game_data.get_item(loot_item)
            if item:
                await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}{monster.name} dropou: {item.name}!{ANSI.RESET}\r\n")
                await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Use 'get {item.name}' para pegar.{ANSI.RESET}\r\n")
        
        # Verifica se há mais monstros na sala para combater automaticamente
        await self._check_and_start_next_combat(player, world_id, room_id)
    
    async def _check_and_start_next_combat(self, player: Player, world_id: str, room_id: str):
        """Verifica se há mais monstros na sala e inicia combate automático"""
        import asyncio
        entities = self.game_data.get_room_entities(world_id, room_id)
        
        # Garante que há instâncias de monstros
        await self._ensure_monster_instances(world_id, room_id, entities['monsters'])
        
        monster_instances = self.monster_instances.get(world_id, {}).get(room_id, {})
        
        # Procura primeiro monstro vivo
        for instance_id, monster in monster_instances.items():
            if monster and monster.is_alive():
                # Inicia combate automático com este monstro
                await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}✨ {monster.name} aparece! ✨{ANSI.RESET}\r\n")
                await asyncio.sleep(0.5)
                
                # Inicia combate
                self.in_combat[player.name] = f"{world_id}:{room_id}:{instance_id}"
                await self._show_combat_menu(player)
            return
        
        # Não há mais monstros
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você derrotou todos os monstros da sala!{ANSI.RESET}\r\n")
    
    async def cmd_attack(self, player: Player, target: str):
        """Comando attack - ataca um monstro por ID ou nome (estilo MUD)"""
        if not target:
            await self.send_message(player, f"{ANSI.YELLOW}Atacar quem? Use: attack <número> ou attack <nome>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Garante que há instâncias de monstros
        await self._ensure_monster_instances(player.world_id, player.room_id, entities['monsters'])
        
        monster_instances = self.monster_instances[player.world_id].get(player.room_id, {})
        
        if not monster_instances:
            await self.send_message(player, f"{ANSI.RED}Não há monstros aqui para atacar.{ANSI.RESET}")
            return
        
        # Tenta encontrar por ID primeiro (número)
        monster_found = None
        monster_instance_id = None
        
        try:
            target_id = int(target)
            if target_id in monster_instances:
                monster_found = monster_instances[target_id]
                monster_instance_id = target_id
        except ValueError:
            # Não é um número, tenta por nome
            pass
        
        # Se não encontrou por ID, tenta por nome
        if not monster_found:
            target_lower = target.lower()
            for instance_id, monster in monster_instances.items():
                if monster.is_alive() and target_lower in monster.name.lower():
                    monster_found = monster
                    monster_instance_id = instance_id
                    break
        
        if not monster_found or not monster_found.is_alive():
            await self.send_message(player, f"{ANSI.RED}Monstro '{target}' não encontrado aqui.{ANSI.RESET}")
            return
        
        # Verifica se já está em combate
        if player.name in self.in_combat:
            await self.send_message(player, f"{ANSI.YELLOW}Você já está em combate! Use o menu de combate.{ANSI.RESET}")
            await self._show_combat_menu(player)
            return
        
        # Inicia combate estilo Pokémon (mostra menu)
        self.in_combat[player.name] = f"{player.world_id}:{player.room_id}:{monster_instance_id}"
        await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}✨ Você inicia combate com {monster_found.name}! ✨{ANSI.RESET}\r\n")
        await self._show_combat_menu(player)
    
    async def cmd_stats(self, player: Player):
        """Comando stats - mostra estatísticas do jogador"""
        from mud.systems.classes import ClassSystem
        from mud.utils.ascii_players import get_player_ascii
        
        class_system = ClassSystem()
        
        message = f"\r\n{ANSI.BOLD}=== Estatísticas de {player.name} ==={ANSI.RESET}\r\n\r\n"
        
        # Mostra ASCII art do player
        player_ascii = get_player_ascii(player.class_id, player.race_id)
        message += f"{ANSI.BRIGHT_CYAN}{player_ascii}{ANSI.RESET}\r\n"
        
        # Classe, Raça e Gênero
        if player.class_id:
            cls = class_system.get_class(player.class_id)
            if cls:
                message += f"{cls.icon} {ANSI.BRIGHT_GREEN}Classe:{ANSI.RESET} {cls.name}\r\n"
        if player.race_id:
            race = class_system.get_race(player.race_id)
            if race:
                message += f"{race.icon} {ANSI.BRIGHT_GREEN}Raça:{ANSI.RESET} {race.name}\r\n"
        if player.gender_id:
            gender = class_system.get_gender(player.gender_id)
            if gender:
                message += f"{gender.icon} {ANSI.BRIGHT_GREEN}Gênero:{ANSI.RESET} {gender.name}\r\n"
        
        message += f"\r\n{ANSI.BOLD}Atributos:{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_GREEN}Nível:{ANSI.RESET} {player.level}/30\r\n"
        if player.unspent_points > 0:
            message += f"{ANSI.BRIGHT_YELLOW}Pontos não distribuídos: {player.unspent_points} (use 'pontos' para distribuir){ANSI.RESET}\r\n"
        
        # Barras visuais
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        message += f"{format_hp_bar(player.current_hp, player.max_hp)}\r\n"
        message += f"{format_stamina_bar(player.current_stamina, player.max_stamina)}\r\n"
        
        message += f"{ANSI.BRIGHT_YELLOW}Experiência:{ANSI.RESET} {player.experience}\r\n"
        
        # Stats com equipamento
        total_attack = player.get_total_attack(self.game_data)
        total_defense = player.get_total_defense(self.game_data)
        
        if total_attack > player.attack or total_defense > player.defense:
            # Mostra stats base e total
            attack_bonus = total_attack - player.attack
            defense_bonus = total_defense - player.defense
            message += f"{ANSI.BRIGHT_CYAN}Ataque:{ANSI.RESET} {player.attack}"
            if attack_bonus > 0:
                message += f" {ANSI.BRIGHT_GREEN}(+{attack_bonus} equipamento) = {total_attack}{ANSI.RESET}\r\n"
            else:
                message += "\r\n"
            
            message += f"{ANSI.BRIGHT_BLUE}Defesa:{ANSI.RESET} {player.defense}"
            if defense_bonus > 0:
                message += f" {ANSI.BRIGHT_GREEN}(+{defense_bonus} equipamento) = {total_defense}{ANSI.RESET}\r\n"
            else:
                message += "\r\n"
        else:
            message += f"{ANSI.BRIGHT_CYAN}Ataque:{ANSI.RESET} {total_attack}\r\n"
            message += f"{ANSI.BRIGHT_BLUE}Defesa:{ANSI.RESET} {total_defense}\r\n"
        
        # Mostra equipamento
        if player.equipment:
            message += f"\r\n{ANSI.BOLD}Equipamento:{ANSI.RESET}\r\n"
            for slot, item_id in player.equipment.items():
                if item_id:
                    item = self.game_data.get_item(item_id)
                    if item:
                        message += f"  {ANSI.BRIGHT_CYAN}{slot.capitalize()}:{ANSI.RESET} {item.name}\r\n"
                    else:
                        message += f"  {ANSI.BRIGHT_CYAN}{slot.capitalize()}:{ANSI.RESET} [Item não encontrado]\r\n"
        
        message += f"{ANSI.BRIGHT_MAGENTA}Ouro:{ANSI.RESET} {player.gold}\r\n"
        await self.send_message(player, message)
    
    @staticmethod
    def _normalize_text_for_map(text: Optional[str]) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize('NFKD', text)
        return ''.join(ch for ch in normalized.lower() if not unicodedata.combining(ch))

    def _detect_room_environment(self, room: Room) -> str:
        if not room:
            return 'neutral'
        full_text = ' '.join(filter(None, [room.id, room.name, room.description]))
        normalized = self._normalize_text_for_map(full_text)
        for env, keywords in self._MAP_ENV_KEYWORDS:
            if any(keyword in normalized for keyword in keywords):
                return env
        return 'neutral'

    def _clone_tile_template(self, env: str) -> List[List[tuple[str, str]]]:
        template = self._MAP_TILE_TEMPLATES.get(env, self._MAP_TILE_TEMPLATES['neutral'])
        return [[(char, color) for char, color in row] for row in template]

    def _calculate_room_connectors(self, room_id: str, room_positions: Dict[str, tuple[int, int]], relevant_rooms: Dict[str, Room]) -> set:
        connectors = set()
        position = room_positions.get(room_id)
        if not position:
            return connectors
        x, y = position
        room = relevant_rooms[room_id]
        neighbor_vectors = {
            (0, -1): 'north',
            (0, 1): 'south',
            (1, 0): 'east',
            (-1, 0): 'west',
        }
        for other_id, (ox, oy) in room_positions.items():
            if other_id == room_id:
                continue
            dx = ox - x
            dy = oy - y
            direction = neighbor_vectors.get((dx, dy))
            if not direction:
                continue
            other_room = relevant_rooms[other_id]
            has_path = any(target == other_id for target in room.exits.values())
            if not has_path:
                has_path = any(target == room_id for target in other_room.exits.values())
            if has_path:
                connectors.add(direction)
        return connectors

    def _apply_connector_to_tile(self, tile: List[List[tuple[str, str]]], direction: str) -> None:
        height = len(tile)
        width = len(tile[0]) if height > 0 else 0
        path_color = self._MAP_PATH_COLOR
        if not height or not width:
            return
        mid_x = width // 2
        mid_y = height // 2
        if direction == 'north':
            for row_idx in range(0, min(2, height)):
                tile[row_idx][mid_x] = ('│', path_color)
        elif direction == 'south':
            for row_idx in range(max(height - 2, 0), height):
                tile[row_idx][mid_x] = ('│', path_color)
        elif direction == 'east':
            for col_idx in range(max(width - 2, 0), width):
                tile[mid_y][col_idx] = ('─', path_color)
        elif direction == 'west':
            for col_idx in range(0, min(2, width)):
                tile[mid_y][col_idx] = ('─', path_color)

    def _place_current_marker(self, tile: List[List[tuple[str, str]]]) -> None:
        height = len(tile)
        width = len(tile[0]) if height > 0 else 0
        if not height or not width:
            return
        tile[height // 2][width // 2] = ('★', ANSI.BRIGHT_YELLOW)

    def _place_environment_symbol(self, tile: List[List[tuple[str, str]]], env: str) -> None:
        height = len(tile)
        width = len(tile[0]) if height > 0 else 0
        if not height or not width:
            return
        symbol_char, symbol_color = self._MAP_ENV_SYMBOLS.get(env, self._MAP_ENV_SYMBOLS['neutral'])
        tile[height // 2][width // 2] = (symbol_char, symbol_color)

    def _tile_to_strings(self, tile: List[List[tuple[str, str]]]) -> List[str]:
        lines = []
        for row in tile:
            line_parts = []
            for char, color in row:
                line_parts.append(f"{color}{char}{ANSI.RESET}")
            lines.append(''.join(line_parts) + ANSI.RESET)
        return lines

    def _build_room_tile_lines(
        self,
        room_id: str,
        room_positions: Dict[str, tuple[int, int]],
        relevant_rooms: Dict[str, Room],
        current_room_id: str,
    ) -> List[str]:
        room = relevant_rooms[room_id]
        env = self._detect_room_environment(room)
        tile = self._clone_tile_template(env)
        for connector in self._calculate_room_connectors(room_id, room_positions, relevant_rooms):
            self._apply_connector_to_tile(tile, connector)
        if room_id == current_room_id:
            self._place_current_marker(tile)
        else:
            self._place_environment_symbol(tile, env)
        return self._tile_to_strings(tile)

    def _build_empty_tile_lines(self) -> List[str]:
        return self._tile_to_strings(self._clone_tile_template('empty'))

    def _get_direction_label_for_map(self, current_room: Room, target_room_id: str, world) -> Optional[str]:
        direction_to_room = None
        for direction, target in current_room.exits.items():
            if target == target_room_id:
                direction_to_room = direction
                break
        if not direction_to_room:
            target_room = world.rooms.get(target_room_id) if world else None
            if target_room:
                for direction, dest in target_room.exits.items():
                    if dest == current_room.id:
                        direction_to_room = self._MAP_OPPOSITE_DIRECTIONS.get(direction, direction)
                        break
        if direction_to_room:
            return direction_to_room.capitalize()
        return None
    
    async def cmd_mapa(self, player: Player):
        """Comando mapa - mostra um mapa minimalista: sala atual, anterior e próximas"""
        world = self.world_manager.get_world(player.world_id)
        if not world:
            await self.send_message(player, f"{ANSI.RED}Mundo não encontrado.{ANSI.RESET}")
            return
        
        current_room_id = player.room_id
        if current_room_id not in world.rooms:
            await self.send_message(player, f"{ANSI.RED}Sala atual não encontrada.{ANSI.RESET}")
            return
        
        current_room = world.rooms[current_room_id]
        
        # Coleta salas: atual + salas que levam à atual + salas que a atual leva
        relevant_rooms = {current_room_id: current_room}
        
        # Salas que a atual leva (próximas)
        for direction, target_room_id in current_room.exits.items():
            if target_room_id in world.rooms:
                relevant_rooms[target_room_id] = world.rooms[target_room_id]
        
        # Salas que levam à atual (anteriores)
        for other_room_id, other_room in world.rooms.items():
            if other_room_id != current_room_id:
                for direction, target_room_id in other_room.exits.items():
                    if target_room_id == current_room_id:
                        relevant_rooms[other_room_id] = other_room
                        break
        
        # Mapeia direções para posições simples
        direction_positions = {
            'norte': (1, 0),      # Centro superior
            'nordeste': (2, 0),
            'leste': (2, 1),     # Direita
            'sudeste': (2, 2),
            'sul': (1, 2),       # Centro inferior
            'sudoeste': (0, 2),
            'oeste': (0, 1),     # Esquerda
            'noroeste': (0, 0),
            'cima': (1, 0),
            'baixo': (1, 2),
        }
        
        # Posiciona salas: atual no centro (1,1), outras ao redor
        room_positions = {current_room_id: (1, 1)}  # Sala atual no centro
        used_positions = {(1, 1)}
        
        # Posiciona salas que a atual leva (próximas)
        for direction, target_room_id in current_room.exits.items():
            if target_room_id in relevant_rooms and target_room_id not in room_positions:
                pos = direction_positions.get(direction, None)
                if pos and pos not in used_positions:
                    room_positions[target_room_id] = pos
                    used_positions.add(pos)
                else:
                    # Se a posição já está ocupada, coloca em posição alternativa
                    alt_positions = [(0, 0), (2, 0), (0, 2), (2, 2), (1, 0), (1, 2), (0, 1), (2, 1)]
                    for alt_pos in alt_positions:
                        if alt_pos not in used_positions:
                            room_positions[target_room_id] = alt_pos
                            used_positions.add(alt_pos)
                            break
        
        # Posiciona salas que levam à atual (anteriores)
        for other_room_id, other_room in world.rooms.items():
            if other_room_id in relevant_rooms and other_room_id not in room_positions:
                # Procura direção que leva à sala atual
                for direction, target_room_id in other_room.exits.items():
                    if target_room_id == current_room_id:
                        # Posiciona na direção oposta
                        opposite_directions = {
                            'norte': 'sul', 'sul': 'norte',
                            'leste': 'oeste', 'oeste': 'leste',
                            'nordeste': 'sudoeste', 'sudoeste': 'nordeste',
                            'sudeste': 'noroeste', 'noroeste': 'sudeste',
                        }
                        opposite = opposite_directions.get(direction, 'sul')
                        pos = direction_positions.get(opposite, (1, 0))
                        if pos not in used_positions:
                            room_positions[other_room_id] = pos
                            used_positions.add(pos)
                        else:
                            # Posição alternativa
                            alt_positions = [(0, 0), (2, 0), (0, 2), (2, 2), (1, 0), (1, 2), (0, 1), (2, 1)]
                            for alt_pos in alt_positions:
                                if alt_pos not in used_positions:
                                    room_positions[other_room_id] = alt_pos
                                    used_positions.add(alt_pos)
                                    break
                        break
        
        position_to_room = {pos: room_id for room_id, pos in room_positions.items()}
        tile_cache = {
            room_id: self._build_room_tile_lines(room_id, room_positions, relevant_rooms, current_room_id)
            for room_id in room_positions
        }
        empty_tile = self._build_empty_tile_lines()
        grid_size = 3
        map_lines = []
        for y in range(grid_size):
            for tile_row in range(self._MAP_TILE_HEIGHT):
                row_segments = []
                for x in range(grid_size):
                    room_id = position_to_room.get((x, y))
                    tile_lines = tile_cache.get(room_id, empty_tile)
                    row_segments.append(tile_lines[tile_row])
                map_lines.append(' '.join(row_segments) + ANSI.RESET)

        sorted_rooms = sorted(position_to_room.items(), key=lambda item: (item[0][1], item[0][0]))
        neighbors_info = []
        for _pos, room_id in sorted_rooms:
            if room_id == current_room_id:
                continue
            room = relevant_rooms[room_id]
            env = self._detect_room_environment(room)
            symbol_char, symbol_color = self._MAP_ENV_SYMBOLS.get(env, self._MAP_ENV_SYMBOLS['neutral'])
            direction_label = self._get_direction_label_for_map(current_room, room_id, world)
            if direction_label:
                info_label = f"[{direction_label}] {room.name}"
            else:
                info_label = room.name
            neighbors_info.append((symbol_char, symbol_color, info_label))

        envs_in_map = {
            self._detect_room_environment(relevant_rooms[room_id])
            for room_id in relevant_rooms
        }

        message = f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}=== Mapa Local ==={ANSI.RESET}\r\n\r\n"
        message += f"{ANSI.BRIGHT_YELLOW}Legenda:{ANSI.RESET}\r\n"
        message += f"  {ANSI.BRIGHT_YELLOW}★{ANSI.RESET} = Sua localização atual\r\n"
        message += f"  {self._MAP_PATH_COLOR}─│{ANSI.RESET} = Caminhos\r\n"
        for env, description in self._MAP_LEGEND_DESCRIPTIONS.items():
            if env in envs_in_map:
                symbol_char, symbol_color = self._MAP_ENV_SYMBOLS.get(env, self._MAP_ENV_SYMBOLS['neutral'])
                message += f"  {symbol_color}{symbol_char}{ANSI.RESET} = {description}\r\n"
        message += "\r\n"

        for line in map_lines:
            message += f"{line}\r\n"

        if neighbors_info:
            message += f"\r\n{ANSI.BRIGHT_CYAN}Conexões próximas:{ANSI.RESET}\r\n"
            for symbol_char, symbol_color, info_label in neighbors_info:
                message += f"  {symbol_color}{symbol_char}{ANSI.RESET} {info_label}\r\n"
        
        message += f"\r\n{ANSI.BRIGHT_BLACK}Mostrando sala atual e conexões diretas{ANSI.RESET}\r\n"
        
        await self.send_message(player, message)
    
    def _paginate_list(self, items: List, items_per_page: int = 10) -> List[List]:
        """Divide uma lista em páginas"""
        pages = []
        for i in range(0, len(items), items_per_page):
            pages.append(items[i:i + items_per_page])
        return pages if pages else [[]]
    
    async def cmd_inventory(self, player: Player, args: str = ""):
        """Comando inventory - mostra menu de categorias primeiro, depois itens da categoria escolhida"""
        from collections import Counter
        import re
        
        # Se não há argumentos, mostra menu de categorias
        if not args or args.strip() == "":
            await self._show_inventory_categories(player)
            return
        
        # Parse argumentos: categoria [busca] [página] ou número [página]
        parts = args.split()
        
        # Verifica se primeiro argumento é um número (escolha de categoria)
        category_choice = None
        search_term = ""
        page_num = 1
        
        if parts[0].isdigit():
            # É um número, escolha de categoria
            category_choice = int(parts[0])
            # Resto são busca e/ou página
            if len(parts) > 1:
                if parts[-1].isdigit():
                    page_num = int(parts[-1])
                    search_term = " ".join(parts[1:-1])
                else:
                    search_term = " ".join(parts[1:])
        else:
            # Primeiro argumento pode ser nome de categoria ou busca
            category_map = {
                'weapon': 'weapon', 'arma': 'weapon', 'armas': 'weapon',
                'armor': 'armor', 'armadura': 'armor', 'armaduras': 'armor',
                'consumable': 'consumable', 'consumivel': 'consumable', 'consumíveis': 'consumable', 'consumiveis': 'consumable',
                'misc': 'misc', 'miscelanea': 'misc', 'miscelânea': 'misc',
                'all': 'all', 'todos': 'all', 'tudo': 'all'
            }
            
            first_arg = parts[0].lower()
            if first_arg in category_map:
                category_choice = category_map[first_arg]
                # Resto são busca e/ou página
                if len(parts) > 1:
                    if parts[-1].isdigit():
                        page_num = int(parts[-1])
                        search_term = " ".join(parts[1:-1])
                    else:
                        search_term = " ".join(parts[1:])
            else:
                # É uma busca geral (sem categoria)
                category_choice = 'all'
                if parts[-1].isdigit():
                    page_num = int(parts[-1])
                    search_term = " ".join(parts[:-1])
                else:
                    search_term = args
        
        # Agrupa itens por ID
        item_counts = Counter(player.inventory)
        
        # Mapeia escolha numérica para categoria
        if isinstance(category_choice, int):
            categories = ['weapon', 'armor', 'consumable', 'misc', 'all']
            if 1 <= category_choice <= len(categories):
                category_choice = categories[category_choice - 1]
            else:
                await self.send_message(player, f"{Colors.ERROR}Opção inválida!{Colors.RESET}")
                await self._show_inventory_categories(player)
                return
        
        # Filtra por categoria e busca
        filtered_items = []
        for item_id, count in sorted(item_counts.items()):
            item = self.game_data.get_item(item_id)
            if item:
                # Filtra por categoria
                if category_choice != 'all' and item.type != category_choice:
                    continue
                
                # Busca no nome, descrição ou tipo
                if not search_term or (
                    search_term.lower() in item.name.lower() or
                    search_term.lower() in item.description.lower() or
                    search_term.lower() in item.type.lower() or
                    search_term.lower() in item.rarity.lower()
                ):
                    filtered_items.append((item_id, count, item))
            else:
                # Item não encontrado
                if category_choice == 'all' or category_choice == 'misc':
                    if not search_term or search_term.lower() in item_id.lower():
                        filtered_items.append((item_id, count, None))
        
        if not filtered_items:
            category_name = {
                'weapon': 'Armas',
                'armor': 'Armaduras',
                'consumable': 'Consumíveis',
                'misc': 'Miscelânea',
                'all': 'todas as categorias'
            }.get(category_choice, category_choice)
            
            if search_term:
                await self.send_message(player, 
                    f"{Colors.WARNING}Nenhum item encontrado em {category_name} com '{search_term}'.{Colors.RESET}\r\n"
                    f"{Colors.COMMAND}Use: inventory para ver categorias{Colors.RESET}")
            else:
                await self.send_message(player, f"{Colors.WARNING}Nenhum item em {category_name}.{Colors.RESET}")
            return
        
        # Paginação
        items_per_page = 8
        pages = self._paginate_list(filtered_items, items_per_page)
        total_pages = len(pages)
        
        # Valida página
        if page_num < 1:
            page_num = 1
        elif page_num > total_pages:
            page_num = total_pages
        
        current_page = pages[page_num - 1]
        
        # Monta mensagem (versão compacta e resumida)
        category_name = {
            'weapon': '⚔ Armas',
            'armor': '🛡 Armaduras',
            'consumable': '🧪 Consumíveis',
            'misc': '📦 Miscelânea',
            'all': '📋 Todos os Itens'
        }.get(category_choice, category_choice.capitalize())
        
        message = f"\r\n{Colors.TITLE}=== Inventário: {category_name} ==={Colors.RESET}\r\n"
        
        if search_term:
            message += f"{Colors.LABEL}Busca: '{search_term}'{Colors.RESET}\r\n"
        
        total_items = sum(count for _, count, _ in filtered_items)
        message += f"{Colors.HINT}Página {page_num}/{total_pages} | {len(filtered_items)} tipos | {total_items} itens totais{Colors.RESET}\r\n\r\n"
        
        # Mostra itens da categoria (já filtrados)
        for item_id, count, item in current_page:
            if item:
                # Versão compacta: nome, quantidade, raridade, stats resumidos
                count_text = f"{Colors.VALUE}x{count}{Colors.RESET}" if count > 1 else ""
                rarity_color = item.get_rarity_color()
                rarity_text = f" {Colors.HINT}[{item.rarity.upper()}]{Colors.RESET}" if item.rarity != "common" else ""
                
                # Verifica se está equipado
                is_equipped = player.is_item_equipped(item_id)
                equipped_text = f" {Colors.SUCCESS}[E]{Colors.RESET}" if is_equipped else ""
                
                # Stats resumidos em uma linha
                stats_parts = []
                if item.type in ['weapon', 'armor'] and item.stats:
                    if item.stats.get('attack', 0) > 0:
                        stats_parts.append(f"{Colors.INFO}+{item.stats['attack']}⚔{Colors.RESET}")
                    if item.stats.get('defense', 0) > 0:
                        stats_parts.append(f"{Colors.INFO}+{item.stats['defense']}🛡{Colors.RESET}")
                
                stats_text = f" {' '.join(stats_parts)}" if stats_parts else ""
                
                # Linha compacta: nome, quantidade, raridade, stats, equipado
                message += f"  {rarity_color}{item.name}{Colors.RESET} {count_text}{rarity_text}{stats_text}{equipped_text}\r\n"
            else:
                message += f"  {Colors.WARNING}[Item não encontrado: {item_id}]{Colors.RESET} {Colors.VALUE}x{count}{Colors.RESET}\r\n"
        
        message += "\r\n"
        
        # Resumo total
        message += f"{Colors.INFO}Total: {total_items} itens em {len(filtered_items)} tipos diferentes{Colors.RESET}\r\n"
        
        if total_pages > 1:
            message += f"\r\n{Colors.LABEL}Navegação:{Colors.RESET}\r\n"
            if page_num > 1:
                nav_cmd = f"inventory {category_choice} {search_term} {page_num - 1}".strip() if search_term else f"inventory {category_choice} {page_num - 1}".strip()
                message += f"  {Colors.COMMAND}{nav_cmd}{Colors.RESET} - Página anterior\r\n"
            if page_num < total_pages:
                nav_cmd = f"inventory {category_choice} {search_term} {page_num + 1}".strip() if search_term else f"inventory {category_choice} {page_num + 1}".strip()
                message += f"  {Colors.COMMAND}{nav_cmd}{Colors.RESET} - Próxima página\r\n"
        
        message += f"\r\n{Colors.HINT}Use: {Colors.COMMAND}inventory{Colors.RESET} para ver categorias\r\n"
        if search_term:
            message += f"{Colors.HINT}Use: {Colors.COMMAND}inventory {category_choice}{Colors.RESET} para ver todos os itens desta categoria\r\n"
        
        await self.send_message(player, message)
    
    async def _show_inventory_categories(self, player: Player):
        """Mostra menu de categorias do inventário"""
        from collections import Counter
        
        if not player.inventory:
            await self.send_message(player, f"{Colors.WARNING}Seu inventário está vazio.{Colors.RESET}")
            return
        
        # Conta itens por categoria
        item_counts = Counter(player.inventory)
        category_counts = {
            'weapon': 0,
            'armor': 0,
            'consumable': 0,
            'misc': 0
        }
        
        for item_id, count in item_counts.items():
            item = self.game_data.get_item(item_id)
            if item and item.type in category_counts:
                category_counts[item.type] += count
        
        # Monta menu
        message = f"\r\n{Colors.TITLE}=== Inventário - Escolha uma Categoria ==={Colors.RESET}\r\n\r\n"
        
        categories = [
            ('weapon', '⚔ Armas', category_counts['weapon']),
            ('armor', '🛡 Armaduras', category_counts['armor']),
            ('consumable', '🧪 Consumíveis', category_counts['consumable']),
            ('misc', '📦 Miscelânea', category_counts['misc']),
            ('all', '📋 Todos os Itens', len(player.inventory))
        ]
        
        for i, (cat_id, cat_name, count) in enumerate(categories, 1):
            if count > 0 or cat_id == 'all':
                message += f"  {Colors.VALUE}{i}{Colors.RESET} - {Colors.CATEGORY}{cat_name}{Colors.RESET} ({Colors.NUMBER}{count}{Colors.RESET} itens)\r\n"
        
        message += f"\r\n{Colors.HINT}Digite o número da categoria ou: {Colors.COMMAND}inventory <categoria> [busca] [página]{Colors.RESET}\r\n"
        message += f"{Colors.HINT}Exemplos:{Colors.RESET}\r\n"
        message += f"  {Colors.COMMAND}inventory 1{Colors.RESET} - Ver armas\r\n"
        message += f"  {Colors.COMMAND}inventory consumable{Colors.RESET} - Ver consumíveis\r\n"
        message += f"  {Colors.COMMAND}inventory 2 poção{Colors.RESET} - Buscar 'poção' em armaduras\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_get(self, player: Player, item_name: str):
        """Comando get - pega item do chão"""
        if not item_name:
            await self.send_message(player, f"{ANSI.YELLOW}Pegar o quê? Use: get <nome>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Procura item
        for item_id in entities['items']:
            item = self.game_data.get_item(item_id)
            if item and item_name.lower() in item.name.lower():
                player.add_item(item_id)
                entities['items'].remove(item_id)
                await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você pegou: {item.name}!{ANSI.RESET}")
                
                # Atualiza progresso de quests de coleta
                await self._update_collect_quests(player, item_id)
                return
        
        await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não encontrado aqui.{ANSI.RESET}")
    
    async def _update_collect_quests(self, player: Player, item_id: str):
        """Atualiza progresso de quests de coleta"""
        for quest_id in player.active_quests:
            quest = self.quest_manager.get_quest(player.world_id, quest_id)
            if quest:
                for objective in quest.objectives:
                    if objective.get('type') == 'collect':
                        target = objective.get('target', '').lower()
                        if target in item_id.lower() or item_id.lower() in target:
                            progress_key = f"collect_{objective.get('target')}"
                            if quest_id not in player.quest_progress:
                                player.quest_progress[quest_id] = {}
                            player.quest_progress[quest_id][progress_key] = \
                                player.quest_progress[quest_id].get(progress_key, 0) + 1
                            
                            # Salva progresso no banco
                            stats = {
                                'hp': player.current_hp,
                                'max_hp': player.max_hp,
                                'level': player.level,
                                'experience': player.experience,
                                'attack': player.attack,
                                'defense': player.defense,
                                'gold': player.gold,
                                'inventory': player.inventory,
                                'equipment': player.equipment,
                                'active_quests': player.active_quests,
                                'quest_progress': player.quest_progress,
                                'completed_quests': player.completed_quests
                            }
                            self.database.update_player_stats(player.name, stats)
                            
                            # Verifica se completou
                            if self.quest_manager.check_quest_completion(quest, player.quest_progress[quest_id]):
                                await self.send_message(player, 
                                    f"{ANSI.BRIGHT_GREEN}Quest '{quest.name}' pode ser completada!{ANSI.RESET}")
    
    async def cmd_drop(self, player: Player, item_name: str):
        """Comando drop - larga item"""
        if not item_name:
            await self.send_message(player, f"{ANSI.YELLOW}Largar o quê? Use: drop <nome>{ANSI.RESET}")
            return
        
        # Procura item no inventário
        for item_id in player.inventory:
            item = self.game_data.get_item(item_id)
            if item and item_name.lower() in item.name.lower():
                player.remove_item(item_id)
                entities = self.game_data.get_room_entities(player.world_id, player.room_id)
                entities['items'].append(item_id)
                await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Você largou: {item.name}.{ANSI.RESET}")
                return
        
        await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está no seu inventário.{ANSI.RESET}")
    
    async def cmd_talk(self, player: Player, npc_name: str):
        """Comando talk - fala com NPC"""
        if not npc_name:
            await self.send_message(player, f"{ANSI.YELLOW}Falar com quem? Use: talk <nome>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Procura NPC
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and npc_name.lower() in npc.name.lower():
                message = f"\r\n{ANSI.BRIGHT_CYAN}{npc.name}{ANSI.RESET} diz:\r\n"
                if npc.dialogue:
                    import random
                    message += f"{ANSI.WHITE}{random.choice(npc.dialogue)}{ANSI.RESET}\r\n"
                if npc.lore:
                    message += f"\r\n{ANSI.BRIGHT_MAGENTA}{npc.lore}{ANSI.RESET}\r\n"
                
                # Se o NPC é um quest_giver, menciona as quests disponíveis
                if npc.npc_type == 'quest_giver' or npc.quests:
                    quests = self.quest_manager.get_quests_by_npc(player.world_id, npc_id)
                    if quests:
                        available_quests = [q for q in quests if q.id not in player.completed_quests]
                        if available_quests:
                            message += f"\r\n{ANSI.BRIGHT_YELLOW}{npc.name} tem quests disponíveis!{ANSI.RESET}\r\n"
                            message += f"{ANSI.BRIGHT_GREEN}Use: quest {npc.name} para ver as quests{ANSI.RESET}\r\n"
                
                await self.send_message(player, message)
                return
        
        await self.send_message(player, f"{ANSI.RED}NPC '{npc_name}' não encontrado aqui.{ANSI.RESET}")
    
    async def cmd_read(self, player: Player, target: str):
        """Comando read - lê lore de monstro ou NPC"""
        if not target:
            await self.send_message(player, f"{ANSI.YELLOW}Ler o quê? Use: read <nome>{ANSI.RESET}")
            return
        
        # Procura monstro
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        for monster_id in entities['monsters']:
            monster_template = self.game_data.monsters.get(player.world_id, {}).get(monster_id)
            if monster_template and target.lower() in monster_template.name.lower():
                if monster_template.lore:
                    await self.send_message(player, f"\r\n{ANSI.BRIGHT_MAGENTA}{monster_template.lore}{ANSI.RESET}\r\n")
                else:
                    await self.send_message(player, f"{ANSI.YELLOW}Não há lore sobre {monster_template.name}.{ANSI.RESET}")
                return
        
        # Procura NPC
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and target.lower() in npc.name.lower():
                if npc.lore:
                    await self.send_message(player, f"\r\n{ANSI.BRIGHT_MAGENTA}{npc.lore}{ANSI.RESET}\r\n")
                else:
                    await self.send_message(player, f"{ANSI.YELLOW}Não há lore sobre {npc.name}.{ANSI.RESET}")
                return
        
        await self.send_message(player, f"{ANSI.RED}Não encontrado: {target}{ANSI.RESET}")
    
    async def cmd_use(self, player: Player, item_name: str):
        """Comando use - usa um item (pode ser usado durante combate)"""
        if not item_name:
            await self.send_message(player, f"{ANSI.YELLOW}Usar o quê? Use: use <nome>{ANSI.RESET}")
            return
        
        # Procura item no inventário
        item_found = None
        item_id_found = None
        
        for item_id in player.inventory:
            item = self.game_data.get_item(item_id)
            if item and item_name.lower() in item.name.lower():
                item_found = item
                item_id_found = item_id
                break
        
        if not item_found:
            await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está no seu inventário.{ANSI.RESET}")
            return
        
        if item_found.type != 'consumable':
            await self.send_message(player, f"{ANSI.YELLOW}Este item não pode ser usado.{ANSI.RESET}")
            return
        
        # Aplica efeitos
        effects_applied = []
        hp_healed = 0
        stamina_restored = 0
        
        if 'hp' in item_found.stats:
            old_hp = player.current_hp
            player.heal(item_found.stats['hp'])
            hp_healed = player.current_hp - old_hp
            if hp_healed > 0:
                effects_applied.append(f"{hp_healed} de HP")
        
        if 'stamina' in item_found.stats:
            old_stamina = player.current_stamina
            player.restore_stamina(item_found.stats['stamina'])
            stamina_restored = player.current_stamina - old_stamina
            if stamina_restored > 0:
                effects_applied.append(f"{stamina_restored} de stamina")
        
        if 'mana' in item_found.stats:
            # TODO: Implementar sistema de mana quando necessário
            effects_applied.append(f"{item_found.stats['mana']} de mana (sistema em desenvolvimento)")
        
        if not effects_applied:
            await self.send_message(player, f"{ANSI.YELLOW}{item_found.name} não teve efeito.{ANSI.RESET}")
            return
        
        # Remove item do inventário
        player.remove_item(item_id_found)
        
        # Mensagem de sucesso
        effects_text = ", ".join(effects_applied)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você usou {item_found.name} e recuperou {effects_text}!{ANSI.RESET}")
        
        # Mostra barras de HP e/ou Stamina quando recuperados
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        
        if hp_healed > 0:
            player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
            await self.send_message(player, f"{player_hp_bar}\r\n")
        
        if stamina_restored > 0:
            player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
            await self.send_message(player, f"{player_stamina_bar}\r\n")
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_equip(self, player: Player, item_name: str):
        """Comando equip - equipa um item (weapon ou armor)"""
        if not item_name:
            await self.send_message(player, f"{ANSI.YELLOW}Equipar o quê? Use: equip <nome do item>{ANSI.RESET}")
            return
        
        # Procura item no inventário
        item_found = None
        item_id_found = None
        
        for item_id in player.inventory:
            item = self.game_data.get_item(item_id)
            if item and item_name.lower() in item.name.lower():
                item_found = item
                item_id_found = item_id
                break
        
        if not item_found:
            await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está no seu inventário.{ANSI.RESET}")
            return
        
        # Verifica se é um item equipável
        if item_found.type not in ['weapon', 'armor']:
            await self.send_message(player, f"{ANSI.YELLOW}Este item não pode ser equipado. Apenas armas e armaduras podem ser equipadas.{ANSI.RESET}")
            return
        
        # Equipa o item
        success, message = player.equip_item(item_id_found, self.game_data)
        if success:
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{message}{ANSI.RESET}\r\n")
            
            # Mostra stats atualizados
            total_attack = player.get_total_attack(self.game_data)
            total_defense = player.get_total_defense(self.game_data)
            await self.send_message(player, 
                f"{ANSI.BRIGHT_CYAN}Ataque: {total_attack} | Defesa: {total_defense}{ANSI.RESET}\r\n")
            
            # Salva no banco
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns
            }
            self.database.update_player_stats(player.name, stats)
        else:
            await self.send_message(player, f"{ANSI.RED}{message}{ANSI.RESET}")
    
    async def cmd_unequip(self, player: Player, item_name: str):
        """Comando unequip - desequipa um item"""
        if not item_name:
            await self.send_message(player, f"{ANSI.YELLOW}Desequipar o quê? Use: unequip <nome do item> ou unequip <slot>{ANSI.RESET}")
            return
        
        # Verifica se é um slot
        slot_map = {
            'weapon': 'weapon',
            'arma': 'weapon',
            'armor': 'armor',
            'armadura': 'armor'
        }
        
        slot = slot_map.get(item_name.lower())
        if slot:
            # Desequipa por slot
            success, message = player.unequip_item(slot)
            if success:
                await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{message}{ANSI.RESET}\r\n")
                
                # Mostra stats atualizados
                total_attack = player.get_total_attack(self.game_data)
                total_defense = player.get_total_defense(self.game_data)
                await self.send_message(player, 
                    f"{ANSI.BRIGHT_CYAN}Ataque: {total_attack} | Defesa: {total_defense}{ANSI.RESET}\r\n")
                
                # Salva no banco
                stats = {
                    'hp': player.current_hp,
                    'max_hp': player.max_hp,
                    'current_stamina': player.current_stamina,
                    'max_stamina': player.max_stamina,
                    'level': player.level,
                    'experience': player.experience,
                    'attack': player.attack,
                    'defense': player.defense,
                    'gold': player.gold,
                    'inventory': player.inventory,
                    'equipment': player.equipment,
                    'active_quests': player.active_quests,
                    'quest_progress': player.quest_progress,
                    'completed_quests': player.completed_quests,
                    'known_spells': player.known_spells,
                    'equipped_spells': player.equipped_spells,
                    'active_perks': player.active_perks,
                    'spell_cooldowns': player.spell_cooldowns
                }
                self.database.update_player_stats(player.name, stats)
            else:
                await self.send_message(player, f"{ANSI.RED}{message}{ANSI.RESET}")
            return
        
        # Procura item equipado
        item_found = None
        item_id_found = None
        slot_found = None
        
        for slot, item_id in player.equipment.items():
            if item_id:
                item = self.game_data.get_item(item_id)
                if item and item_name.lower() in item.name.lower():
                    item_found = item
                    item_id_found = item_id
                    slot_found = slot
                    break
        
        if not item_found:
            await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está equipado.{ANSI.RESET}")
            return
        
        # Desequipa o item
        success, message = player.unequip_item(slot_found)
        if success:
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{message}{ANSI.RESET}\r\n")
            
            # Mostra stats atualizados
            total_attack = player.get_total_attack(self.game_data)
            total_defense = player.get_total_defense(self.game_data)
            await self.send_message(player, 
                f"{ANSI.BRIGHT_CYAN}Ataque: {total_attack} | Defesa: {total_defense}{ANSI.RESET}\r\n")
            
            # Salva no banco
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns
            }
            self.database.update_player_stats(player.name, stats)
        else:
            await self.send_message(player, f"{ANSI.RED}{message}{ANSI.RESET}")
    
    async def cmd_spells(self, player: Player):
        """Comando spells - mostra magias conhecidas e equipadas"""
        if not player.class_id:
            await self.send_message(player, f"{ANSI.YELLOW}Você não tem uma classe ainda.{ANSI.RESET}")
            return
        
        message = f"\r\n{ANSI.BOLD}=== Suas Magias ==={ANSI.RESET}\r\n\r\n"
        
        # Magias equipadas
        if player.equipped_spells:
            message += f"{ANSI.BRIGHT_GREEN}Magias Equipadas (max 3):{ANSI.RESET}\r\n"
            for i, spell_id in enumerate(player.equipped_spells, 1):
                spell = self.spell_system.get_spell(spell_id)
                if spell:
                    spell_level = player.get_spell_level(spell_id)
                    message += f"  {i}. {spell.icon} {ANSI.BRIGHT_CYAN}{spell.name}{ANSI.RESET} [Nível {spell_level}]\r\n"
            message += "\r\n"
        else:
            message += f"{ANSI.YELLOW}Nenhuma magia equipada. Use 'equipar <magia>' para equipar.{ANSI.RESET}\r\n\r\n"
        
        # Magias conhecidas
        if player.known_spells:
            message += f"{ANSI.BOLD}Magias Conhecidas:{ANSI.RESET}\r\n"
            from mud.systems.classes import ClassSystem
            class_system = ClassSystem()
            race = class_system.get_race(player.race_id) if player.race_id else None
            race_bonus = 1.0
            
            for spell_id, spell_level in player.known_spells.items():
                spell = self.spell_system.get_spell(spell_id)
                if spell:
                    cost = self.spell_system.calculate_spell_cost(spell, spell_level)
                    damage = self.spell_system.calculate_spell_damage(
                        spell, player.level, player.attack, spell_level, race_bonus
                    )
                    # Máximo nível é o nível do jogador (até 30)
                    max_allowed = min(player.level, 30)
                    max_level_text = f"/{max_allowed}" if max_allowed > 1 else ""
                    equipped_mark = " ✓" if spell_id in player.equipped_spells else ""
                    message += f"{spell.icon} {ANSI.BRIGHT_CYAN}{spell.name}{ANSI.RESET}{equipped_mark} [Nível {spell_level}{max_level_text}]\r\n"
                    message += f"  {spell.description}\r\n"
                    if spell.damage_type != 'heal' and spell.damage_type != 'buff':
                        message += f"  {ANSI.BRIGHT_RED}Dano: {damage}{ANSI.RESET} ({spell.damage_type})\r\n"
                    message += f"  {ANSI.BRIGHT_YELLOW}Custo: {cost} stamina{ANSI.RESET} | Cooldown: {spell.cooldown}s\r\n"
                    message += "\r\n"
        
        # Magias disponíveis para aprender
        available_spells = self.spell_system.get_spells_for_class(player.class_id)
        learnable = []
        for spell in available_spells:
            if spell.id not in player.known_spells:
                if self.spell_system.can_learn_spell(spell, player.level, list(player.known_spells.keys())):
                    learnable.append(spell)
        
        if learnable:
            message += f"\r\n{ANSI.BOLD}=== Magias Disponíveis para Aprender ==={ANSI.RESET}\r\n"
            for spell in learnable:
                message += f"{spell.icon} {ANSI.BRIGHT_GREEN}{spell.name}{ANSI.RESET} [Requer Nível {spell.level_required}]\r\n"
                message += f"  {spell.description}\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_equip_spell(self, player: Player, args: str):
        """Comando equip_spell - equipa uma magia (max 3)"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Equipar qual magia? Use: equipar <nome da magia>{ANSI.RESET}")
            return
        
        if len(player.equipped_spells) >= 3:
            await self.send_message(player, f"{ANSI.RED}Você já tem 3 magias equipadas! Use 'desequipar <magia>' para desequipar uma.{ANSI.RESET}")
            return
        
        # Procura a magia
        spell_found = None
        spell_id = None
        
        for sid, level in player.known_spells.items():
            spell = self.spell_system.get_spell(sid)
            if spell and args.lower() in spell.name.lower():
                spell_found = spell
                spell_id = sid
                break
        
        if not spell_found:
            await self.send_message(player, f"{ANSI.RED}Magia '{args}' não encontrada.{ANSI.RESET}")
            return
        
        if spell_id in player.equipped_spells:
            await self.send_message(player, f"{ANSI.YELLOW}{spell_found.name} já está equipada.{ANSI.RESET}")
            return
        
        if player.equip_spell(spell_id):
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{spell_found.name} equipada!{ANSI.RESET}")
            # Salva no banco
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns
            }
            self.database.update_player_stats(player.name, stats)
        else:
            await self.send_message(player, f"{ANSI.RED}Erro ao equipar magia.{ANSI.RESET}")
    
    async def cmd_unequip_spell(self, player: Player, args: str):
        """Comando unequip_spell - desequipa uma magia"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Desequipar qual magia? Use: desequipar <nome da magia>{ANSI.RESET}")
            return
        
        # Procura a magia equipada
        spell_found = None
        spell_id = None
        
        for sid in player.equipped_spells:
            spell = self.spell_system.get_spell(sid)
            if spell and args.lower() in spell.name.lower():
                spell_found = spell
                spell_id = sid
                break
        
        if not spell_found:
            await self.send_message(player, f"{ANSI.RED}Magia '{args}' não está equipada.{ANSI.RESET}")
            return
        
        player.unequip_spell(spell_id)
        await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}{spell_found.name} desequipada.{ANSI.RESET}")
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_cast(self, player: Player, args: str):
        """Comando cast - lança uma magia (só se estiver equipada)"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Lançar qual magia? Use: cast <nome da magia> [alvo]{ANSI.RESET}")
            return
        
        # Regenera stamina (1 a cada 3 segundos)
        import time
        current_time = time.time()
        if hasattr(player, '_last_stamina_regen'):
            time_passed = current_time - player._last_stamina_regen
            if time_passed >= 3.0:
                regen_amount = int(time_passed / 3.0)  # 1 ponto a cada 3 segundos
                player.restore_stamina(regen_amount)
        player._last_stamina_regen = current_time
        
        # Procura a magia equipada - precisa separar nome da magia do alvo
        spell_found = None
        spell_id = None
        target_name = None
        args_lower = args.lower()
        
        # Primeiro, tenta encontrar a magia equipada que melhor corresponde
        best_match = None
        best_match_length = 0
        
        for sid in player.equipped_spells:
            spell = self.spell_system.get_spell(sid)
            if spell:
                spell_name_lower = spell.name.lower()
                # Verifica se o nome completo da magia está no início dos argumentos
                if args_lower.startswith(spell_name_lower):
                    match_length = len(spell_name_lower)
                    if match_length > best_match_length:
                        best_match = (spell, sid)
                        best_match_length = match_length
                # Também verifica se o nome da magia está contido nos argumentos (fallback)
                elif spell_name_lower in args_lower:
                    match_length = len(spell_name_lower)
                    if match_length > best_match_length:
                        best_match = (spell, sid)
                        best_match_length = match_length
        
        if best_match:
            spell_found, spell_id = best_match
            # Extrai o nome do alvo (tudo após o nome da magia)
            spell_name_lower = spell_found.name.lower()
            if args_lower.startswith(spell_name_lower):
                remaining = args[len(spell_found.name):].strip()
                if remaining:
                    target_name = remaining
            elif spell_name_lower in args_lower:
                # Se o nome da magia está no meio, tenta extrair o que vem depois
                idx = args_lower.find(spell_name_lower)
                if idx >= 0:
                    remaining = args[idx + len(spell_found.name):].strip()
                    if remaining:
                        target_name = remaining
        
        if not spell_found:
            await self.send_message(player, f"{ANSI.RED}Magia não encontrada ou não está equipada. Use 'spells' para ver suas magias e 'equipar <magia>' para equipar.{ANSI.RESET}")
            return
        
        # Verifica cooldown
        if spell_id in player.spell_cooldowns:
            cooldown_end = player.spell_cooldowns[spell_id]
            if time.time() < cooldown_end:
                remaining = int(cooldown_end - time.time()) + 1
                await self.send_message(player, f"{ANSI.YELLOW}{spell_found.name} está em cooldown. Aguarde {remaining}s.{ANSI.RESET}")
                return
        
        # Verifica stamina
        spell_level = player.get_spell_level(spell_id)
        cost = self.spell_system.calculate_spell_cost(spell_found, spell_level)
        
        if not player.has_stamina(cost):
            await self.send_message(player, f"{ANSI.RED}Stamina insuficiente! Você precisa de {cost}, mas tem apenas {player.current_stamina}.{ANSI.RESET}")
            return
        
        # Gasta stamina
        player.use_stamina(cost)
        
        # Aplica cooldown
        player.spell_cooldowns[spell_id] = time.time() + spell_found.cooldown
        
        # Animação de magia
        from mud.utils.visuals import get_spell_animation, get_heal_animation
        import asyncio
        
        if spell_found.damage_type == 'heal':
            animation = get_heal_animation()
        else:
            animation = get_spell_animation()
        
        for frame in animation:
            await self.send_message(player, f"\r{ANSI.BRIGHT_MAGENTA}{frame}{ANSI.RESET}")
            await asyncio.sleep(0.1)
        
        # Processa a magia
        if spell_found.damage_type == 'heal':
            # Magia de cura
            from mud.systems.classes import ClassSystem
            class_system = ClassSystem()
            race = class_system.get_race(player.race_id) if player.race_id else None
            race_bonus = 1.0
            
            heal_amount = self.spell_system.calculate_spell_damage(
                spell_found, player.level, player.attack, spell_level, race_bonus
            )
            player.heal(heal_amount)
            from mud.utils.visuals import format_hp_bar
            await self.send_message(player, f"\r{ANSI.BRIGHT_GREEN}✨ Você lança {spell_found.name} e se cura {heal_amount} de HP! ✨{ANSI.RESET}\r\n")
            await self.send_message(player, f"{format_hp_bar(player.current_hp, player.max_hp)}\r\n")
        elif spell_found.damage_type in ['physical', 'fire', 'ice', 'lightning', 'arcane', 'nature']:
            # Magia de dano - precisa de alvo
            if not target_name:
                await self.send_message(player, f"{ANSI.YELLOW}Você lança {spell_found.name}, mas precisa de um alvo!{ANSI.RESET}")
                await self.send_message(player, f"{ANSI.YELLOW}Use: cast {spell_found.name.lower()} <alvo>{ANSI.RESET}")
                return
            
            # Procura o monstro alvo
            entities = self.game_data.get_room_entities(player.world_id, player.room_id)
            monster_found = None
            monster_instance_id = None
            
            # Procura por ID numérico primeiro
            if target_name.isdigit():
                target_id = int(target_name)
                if (player.world_id in self.monster_instances and 
                    player.room_id in self.monster_instances[player.world_id] and
                    target_id in self.monster_instances[player.world_id][player.room_id]):
                    monster_found = self.monster_instances[player.world_id][player.room_id][target_id]
                    monster_instance_id = target_id
            else:
                # Procura por nome
                for instance_id, monster in self.monster_instances.get(player.world_id, {}).get(player.room_id, {}).items():
                    if monster and monster.is_alive() and target_name.lower() in monster.name.lower():
                        monster_found = monster
                        monster_instance_id = instance_id
                        break
            
            if not monster_found or not monster_found.is_alive():
                await self.send_message(player, f"{ANSI.RED}Alvo '{target_name}' não encontrado ou já está morto.{ANSI.RESET}")
                return
            
            # Chance de falha da magia (15% base, reduzido com nível do spell)
            import random
            fail_chance = max(0.05, 0.15 - (spell_level * 0.02))  # 15% no nível 1, 5% no nível 5
            if random.random() < fail_chance:
                await self.send_message(player, f"\r{ANSI.RED}❌ Sua magia {spell_found.name} falhou! O alvo desviou ou a magia não funcionou! ❌{ANSI.RESET}\r\n")
                # Monstro ainda pode revidar mesmo se a magia falhar
                await asyncio.sleep(0.3)
                monster_damage = monster_found.get_attack_damage()
                total_defense = player.get_total_defense(self.game_data)
                actual_damage = player.take_damage(monster_damage, total_defense)
                level_info = f" [Nível {monster_found.level}]" if monster_found.level > 1 else ""
                weapon_info = ""
                if monster_found.weapon:
                    weapon_info = f" com {monster_found.weapon}"
                await self.send_message(player, f"{ANSI.RED}👹 {monster_found.name}{level_info} ataca você{weapon_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n")
                from mud.utils.visuals import format_hp_bar, format_stamina_bar
                player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
                player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
                await self.send_message(player, f"{player_hp_bar}\r\n")
                await self.send_message(player, f"{player_stamina_bar}\r\n")
                if not player.is_alive():
                    await self._handle_player_death(player)
                    return
                return
            
            # Calcula dano da magia
            from mud.systems.classes import ClassSystem
            class_system = ClassSystem()
            race = class_system.get_race(player.race_id) if player.race_id else None
            race_bonus = 1.0  # TODO: Implementar bônus de raça para magias se necessário
            
            damage = self.spell_system.calculate_spell_damage(
                spell_found, player.level, player.attack, spell_level, race_bonus
            )
            
            # Aplica dano ao monstro (considerando resistências/fraquezas)
            actual_damage = monster_found.take_damage(damage, spell_found.damage_type)
            
            damage_icon = "🔥" if spell_found.damage_type == "fire" else "❄" if spell_found.damage_type == "ice" else "⚡" if spell_found.damage_type == "lightning" else "✨"
            await self.send_message(player, f"\r{ANSI.BRIGHT_GREEN}{damage_icon} Você lança {spell_found.name} em {monster_found.name} causando {actual_damage} de dano! {damage_icon}{ANSI.RESET}\r\n")
            
            # Mostra barra de HP do monstro
            from mud.utils.visuals import format_monster_hp_bar, get_hp_color
            hp_color = get_hp_color(monster_found.current_hp, monster_found.max_hp)
            monster_hp_display = f"{hp_color}{monster_found.name} HP:{ANSI.RESET} {format_monster_hp_bar(monster_found.current_hp, monster_found.max_hp)}"
            await self.send_message(player, f"{monster_hp_display}\r\n")
            
            # Monstro revida imediatamente após ser atacado com magia
            if monster_found.is_alive():
                await asyncio.sleep(0.3)
                monster_damage = monster_found.get_attack_damage()
                total_defense = player.get_total_defense(self.game_data)
                actual_damage = player.take_damage(monster_damage, total_defense)
                level_info = f" [Nível {monster_found.level}]" if monster_found.level > 1 else ""
                weapon_info = ""
                if monster_found.weapon:
                    weapon_info = f" com {monster_found.weapon}"
                await self.send_message(player, f"{ANSI.RED}👹 {monster_found.name}{level_info} revida e ataca você{weapon_info} causando {actual_damage} de dano! 💥{ANSI.RESET}\r\n")
                from mud.utils.visuals import format_stamina_bar
                player_hp_bar = format_hp_bar(player.current_hp, player.max_hp)
                player_stamina_bar = format_stamina_bar(player.current_stamina, player.max_stamina)
                await self.send_message(player, f"{player_hp_bar}\r\n")
                await self.send_message(player, f"{player_stamina_bar}\r\n")
                if not player.is_alive():
                    await self._handle_player_death(player)
                    return
            
            # Verifica se o monstro morreu
            if not monster_found.is_alive():
                await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}✨ {monster_found.name} foi derrotado! ✨{ANSI.RESET}\r\n")
                
                # Remove instância do monstro
                if monster_instance_id in self.monster_instances.get(player.world_id, {}).get(player.room_id, {}):
                    del self.monster_instances[player.world_id][player.room_id][monster_instance_id]
                
                # Remove template da lista de entidades da sala
                self.game_data.remove_monster_from_room(player.world_id, player.room_id, monster_found.id)
                
                if player.name in self.in_combat:
                    del self.in_combat[player.name]
                
                # Registra morte do monstro para sistema de respawn
                import random
                if self.dungeon_manager:
                    respawn_config = self.dungeon_manager.get_room_respawn_time(
                        player.world_id, player.room_id, monster_found.id
                    )
                else:
                    respawn_config = {'min': 300, 'max': 600}
                
                respawn_time = random.randint(respawn_config['min'], respawn_config['max'])
                self.database.register_monster_death(
                    player.world_id, player.room_id, monster_found.id, monster_instance_id, respawn_time
                )
                
                # Experiência
                exp_gained = CombatSystem.calculate_experience(monster_found)
                player.experience += exp_gained
                await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você ganhou {exp_gained} de experiência!{ANSI.RESET}")
                
                # Verifica level up
                await self._check_level_up(player)
                
                # Salva experiência e nível (mesmo se não subiu de nível)
                stats = {
                    'hp': player.current_hp,
                    'max_hp': player.max_hp,
                    'current_stamina': player.current_stamina,
                    'max_stamina': player.max_stamina,
                    'level': player.level,
                    'experience': player.experience,
                    'attack': player.attack,
                    'defense': player.defense,
                    'gold': player.gold,
                    'inventory': player.inventory,
                    'equipment': player.equipment,
                    'active_quests': player.active_quests,
                    'quest_progress': player.quest_progress,
                    'completed_quests': player.completed_quests,
                    'known_spells': player.known_spells,
                    'equipped_spells': player.equipped_spells,
                    'active_perks': player.active_perks,
                    'spell_cooldowns': player.spell_cooldowns,
                    'unspent_points': player.unspent_points
                }
                self.database.update_player_stats(player.name, stats)
                
                # Ouro
                gold_gained = CombatSystem.drop_gold(monster_found)
                if gold_gained > 0:
                    player.add_gold(gold_gained)
                    await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Você recebeu {gold_gained} moedas!{ANSI.RESET}")
                
                # Loot - dropa no chão
                loot_item = CombatSystem.drop_loot(monster_found)
                if loot_item:
                    entities = self.game_data.get_room_entities(player.world_id, player.room_id)
                    entities['items'].append(loot_item)
                    item = self.game_data.get_item(loot_item)
                    if item:
                        await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}{monster_found.name} dropou: {item.name}!{ANSI.RESET}")
                        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Use 'get {item.name}' para pegar.{ANSI.RESET}")
                
                # Atualiza quests de kill
                await self._update_kill_quests(player, target_name)
            else:
                # Monstro ainda vivo, pode contra-atacar (mas não é obrigatório para magias)
                await asyncio.sleep(0.3)
        else:
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você lança {spell_found.name}!{ANSI.RESET}")
        
        # Salva stats
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_improve_spell(self, player: Player, args: str):
        """Comando improve - melhora uma magia"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Melhorar qual magia? Use: melhorar <nome da magia>{ANSI.RESET}")
            return
        
        # Procura a magia
        spell_found = None
        spell_id = None
        
        for sid, level in player.known_spells.items():
            spell = self.spell_system.get_spell(sid)
            if spell and args.lower() in spell.name.lower():
                spell_found = spell
                spell_id = sid
                break
        
        if not spell_found:
            await self.send_message(player, f"{ANSI.RED}Magia '{args}' não encontrada.{ANSI.RESET}")
            return
        
        current_level = player.get_spell_level(spell_id)
        if current_level >= spell_found.max_level:
            await self.send_message(player, f"{ANSI.YELLOW}{spell_found.name} já está no nível máximo ({spell_found.max_level}).{ANSI.RESET}")
            return
        
        # Custo de melhoria (baseado no level)
        improvement_cost = current_level * 100  # 100, 200, 300, etc
        
        if player.gold < improvement_cost:
            await self.send_message(player, f"{ANSI.RED}Você precisa de {improvement_cost} moedas para melhorar esta magia. Você tem {player.gold}.{ANSI.RESET}")
            return
        
        if player.spend_gold(improvement_cost):
            player.improve_spell(spell_id)
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{spell_found.name} melhorada para nível {player.get_spell_level(spell_id)}!{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Custo pago: {improvement_cost} moedas.{ANSI.RESET}")
            
            # Salva no banco
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns
            }
            self.database.update_player_stats(player.name, stats)
        else:
            await self.send_message(player, f"{ANSI.RED}Erro ao melhorar magia.{ANSI.RESET}")
    
    async def cmd_learn_spell(self, player: Player, args: str):
        """Comando learn - aprende uma nova magia"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Aprender qual magia? Use: aprender <nome da magia>{ANSI.RESET}")
            return
        
        # Procura magia disponível
        available_spells = self.spell_system.get_spells_for_class(player.class_id)
        spell_found = None
        
        for spell in available_spells:
            if args.lower() in spell.name.lower():
                spell_found = spell
                break
        
        if not spell_found:
            await self.send_message(player, f"{ANSI.RED}Magia '{args}' não encontrada ou não disponível para sua classe.{ANSI.RESET}")
            return
        
        if spell_found.id in player.known_spells:
            await self.send_message(player, f"{ANSI.YELLOW}Você já conhece {spell_found.name}.{ANSI.RESET}")
            return
        
        if not self.spell_system.can_learn_spell(spell_found, player.level, list(player.known_spells.keys())):
            if player.level < spell_found.level_required:
                await self.send_message(player, f"{ANSI.RED}Você precisa estar no nível {spell_found.level_required} para aprender {spell_found.name}.{ANSI.RESET}")
            else:
                await self.send_message(player, f"{ANSI.RED}Você ainda não cumpriu os requisitos para aprender {spell_found.name}.{ANSI.RESET}")
            return
        
        # Aprende a magia
        player.learn_spell(spell_found.id, 1)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você aprendeu {spell_found.name}!{ANSI.RESET}")
        await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Use 'equipar {spell_found.name}' para equipá-la.{ANSI.RESET}")
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_perks(self, player: Player):
        """Comando perks - mostra perks disponíveis e ativos"""
        if not player.class_id:
            await self.send_message(player, f"{ANSI.YELLOW}Você não tem uma classe ainda.{ANSI.RESET}")
            return
        
        message = f"\r\n{ANSI.BOLD}=== Perks ==={ANSI.RESET}\r\n\r\n"
        
        # Perks ativos
        if player.active_perks:
            message += f"{ANSI.BRIGHT_GREEN}Perks Ativos:{ANSI.RESET}\r\n"
            for perk_id in player.active_perks:
                perk = self.spell_system.get_perk(perk_id)
                if perk:
                    message += f"  {perk.icon} {ANSI.BRIGHT_CYAN}{perk.name}{ANSI.RESET}\r\n"
                    message += f"    {perk.description}\r\n"
            message += "\r\n"
        else:
            message += f"{ANSI.YELLOW}Nenhum perk ativo.{ANSI.RESET}\r\n\r\n"
        
        # Perks disponíveis
        available_perks = self.spell_system.get_perks_for_class(player.class_id)
        available = [p for p in available_perks if p.id not in player.active_perks and player.level >= p.level_required]
        
        if available:
            message += f"{ANSI.BOLD}Perks Disponíveis:{ANSI.RESET}\r\n"
            for perk in available:
                message += f"{perk.icon} {ANSI.BRIGHT_GREEN}{perk.name}{ANSI.RESET} [Requer Nível {perk.level_required}]\r\n"
                message += f"  {perk.description}\r\n"
        
        await self.send_message(player, message)
    
    def _calculate_exp_for_level(self, level: int) -> int:
        """Calcula experiência necessária para um nível (máximo 30)"""
        MAX_LEVEL = 30
        if level >= MAX_LEVEL:
            return float('inf')
        # Fórmula: 100 * level^1.5 (arredondado)
        import math
        return int(100 * (level ** 1.5))
    
    async def _check_level_up(self, player: Player):
        """Verifica se o jogador subiu de nível e dá pontos"""
        MAX_LEVEL = 30
        if player.level >= MAX_LEVEL:
            return
        
        exp_needed = self._calculate_exp_for_level(player.level)
        
        while player.experience >= exp_needed and player.level < MAX_LEVEL:
            player.experience -= exp_needed
            old_level = player.level
            player.level += 1
            
            # Aumenta stats base
            player.max_hp += 10
            player.current_hp = player.max_hp  # Cura totalmente ao subir de nível
            player.max_stamina += 5
            player.current_stamina = player.max_stamina
            player.attack += 2
            player.defense += 1
            
            # Dá 1 ponto para distribuir
            player.unspent_points += 1
            
            # Mensagem de level up
            await self.send_message(player, f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_GREEN}{'='*50}{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}🎉 LEVEL UP! 🎉{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você subiu do nível {old_level} para o nível {player.level}!{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Você recebeu 1 ponto para distribuir em magias ou perks!{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use 'pontos' para distribuir seus pontos.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}{'='*50}{ANSI.RESET}\r\n")
            
            # Salva no banco
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns,
                'unspent_points': player.unspent_points
            }
            self.database.update_player_stats(player.name, stats)
            
            # Verifica se pode subir mais um nível
            exp_needed = self._calculate_exp_for_level(player.level)
    
    async def cmd_distribute_points(self, player: Player, args: str = ""):
        """Comando points - distribui pontos em magias ou perks"""
        if player.unspent_points <= 0:
            await self.send_message(player, f"{ANSI.YELLOW}Você não tem pontos para distribuir.{ANSI.RESET}")
            return
        
        if not args:
            message = f"\r\n{ANSI.BOLD}=== Distribuir Pontos ==={ANSI.RESET}\r\n\r\n"
            message += f"{ANSI.BRIGHT_YELLOW}Pontos disponíveis: {player.unspent_points}{ANSI.RESET}\r\n\r\n"
            message += f"{ANSI.BRIGHT_GREEN}Use:{ANSI.RESET}\r\n"
            message += f"  {ANSI.BRIGHT_CYAN}pontos magia <nome>{ANSI.RESET} - Distribui 1 ponto em uma magia conhecida\r\n"
            message += f"  {ANSI.BRIGHT_CYAN}pontos perk <nome>{ANSI.RESET} - Distribui 1 ponto para desbloquear/ativar um perk\r\n\r\n"
            
            # Lista magias conhecidas que podem ser melhoradas
            if player.known_spells:
                message += f"{ANSI.BOLD}Magias que podem ser melhoradas:{ANSI.RESET}\r\n"
                for spell_id, spell_level in player.known_spells.items():
                    spell = self.spell_system.get_spell(spell_id)
                    if spell:
                        # Máximo nível é o nível do jogador (até 30)
                        max_allowed = min(player.level, 30)
                        if spell_level < max_allowed:
                            message += f"  {spell.icon} {ANSI.BRIGHT_CYAN}{spell.name}{ANSI.RESET} [Nível {spell_level}/{max_allowed}]\r\n"
                message += "\r\n"
            
            # Lista perks disponíveis
            if player.class_id:
                available_perks = self.spell_system.get_perks_for_class(player.class_id)
                available = [p for p in available_perks if p.id not in player.active_perks and player.level >= p.level_required]
                
                if available:
                    message += f"{ANSI.BOLD}Perks disponíveis para desbloquear:{ANSI.RESET}\r\n"
                    for perk in available:
                        message += f"  {perk.icon} {ANSI.BRIGHT_GREEN}{perk.name}{ANSI.RESET} [Requer Nível {perk.level_required}]\r\n"
            
            await self.send_message(player, message)
            return
        
        # Processa distribuição
        parts = args.lower().split(maxsplit=1)
        if len(parts) < 2:
            await self.send_message(player, f"{ANSI.YELLOW}Use: pontos magia <nome> ou pontos perk <nome>{ANSI.RESET}")
            return
        
        point_type = parts[0]
        target_name = parts[1]
        
        if point_type == 'magia' or point_type == 'magic' or point_type == 'spell':
            # Distribui em magia
            spell_found = None
            spell_id = None
            
            for sid, level in player.known_spells.items():
                spell = self.spell_system.get_spell(sid)
                if spell and target_name.lower() in spell.name.lower():
                    spell_found = spell
                    spell_id = sid
                    break
            
            if not spell_found:
                await self.send_message(player, f"{ANSI.RED}Magia '{target_name}' não encontrada.{ANSI.RESET}")
                return
            
            current_level = player.get_spell_level(spell_id)
            max_allowed = min(player.level, 30)
            
            if current_level >= max_allowed:
                await self.send_message(player, f"{ANSI.YELLOW}{spell_found.name} já está no nível máximo permitido ({max_allowed}) para seu nível atual ({player.level}).{ANSI.RESET}")
                return
            
            player.improve_spell(spell_id)
            player.unspent_points -= 1
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}{spell_found.name} melhorada para nível {player.get_spell_level(spell_id)}!{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Pontos restantes: {player.unspent_points}{ANSI.RESET}")
            
        elif point_type == 'perk':
            # Distribui em perk
            if not player.class_id:
                await self.send_message(player, f"{ANSI.YELLOW}Você não tem uma classe ainda.{ANSI.RESET}")
                return
            
            available_perks = self.spell_system.get_perks_for_class(player.class_id)
            perk_found = None
            
            for perk in available_perks:
                if perk.id not in player.active_perks and target_name.lower() in perk.name.lower():
                    if player.level >= perk.level_required:
                        perk_found = perk
                        break
            
            if not perk_found:
                await self.send_message(player, f"{ANSI.RED}Perk '{target_name}' não encontrado ou você não tem nível suficiente.{ANSI.RESET}")
                return
            
            player.activate_perk(perk_found.id)
            player.unspent_points -= 1
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Perk '{perk_found.name}' desbloqueado e ativado!{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_YELLOW}Pontos restantes: {player.unspent_points}{ANSI.RESET}")
        else:
            await self.send_message(player, f"{ANSI.YELLOW}Use: pontos magia <nome> ou pontos perk <nome>{ANSI.RESET}")
            return
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'equipped_spells': player.equipped_spells,
            'active_perks': player.active_perks,
            'spell_cooldowns': player.spell_cooldowns,
            'unspent_points': player.unspent_points
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_say(self, player: Player, message: str):
        """Comando say - fala algo na sala (local)"""
        if not message:
            await self.send_message(player, f"{ANSI.YELLOW}Diga o quê? Use: say <mensagem>{ANSI.RESET}")
            return
        
        broadcast_msg = f"{ANSI.BRIGHT_CYAN}{player.name}{ANSI.RESET} diz: {message}"
        await self.game.broadcast_to_room(player.world_id, player.room_id, broadcast_msg)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você diz:{ANSI.RESET} {message}")
    
    async def cmd_shout(self, player: Player, message: str):
        """Comando shout - fala globalmente para todos os jogadores no canal global"""
        if not message:
            await self.send_message(player, f"{ANSI.YELLOW}Gritar o quê? Use: shout <mensagem>{ANSI.RESET}")
            return
        
        # Verifica se o jogador está no canal global
        if "global" not in player.channels:
            await self.send_message(player, f"{ANSI.YELLOW}Você precisa estar no canal global para usar shout.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use: join global{ANSI.RESET}")
            return
        
        broadcast_msg = f"{ANSI.BRIGHT_MAGENTA}[GLOBAL]{ANSI.RESET} {ANSI.BRIGHT_CYAN}{player.name}{ANSI.RESET} grita: {message}"
        await self.game.broadcast_global(broadcast_msg)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você grita:{ANSI.RESET} {message}")
    
    async def cmd_join(self, player: Player, channel_name: str):
        """Comando join - entra em um canal"""
        if not channel_name:
            await self.send_message(player, f"{ANSI.YELLOW}Entrar em qual canal? Use: join <canal>{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Canais disponíveis: global{ANSI.RESET}")
            return
        
        channel_name = channel_name.lower().strip()
        
        # Canais disponíveis
        available_channels = ["global"]
        
        if channel_name not in available_channels:
            await self.send_message(player, f"{ANSI.RED}Canal '{channel_name}' não existe.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Canais disponíveis: {', '.join(available_channels)}{ANSI.RESET}")
            return
        
        # Canal local sempre está ativo, não pode fazer join
        if channel_name == "local":
            await self.send_message(player, f"{ANSI.YELLOW}O canal 'local' sempre está ativo. Você já está nele!{ANSI.RESET}")
            return
        
        # Verifica se já está no canal
        if channel_name in player.channels:
            await self.send_message(player, f"{ANSI.YELLOW}Você já está no canal '{channel_name}'.{ANSI.RESET}")
            return
        
        # Adiciona ao canal
        player.channels.append(channel_name)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você entrou no canal '{channel_name}'.{ANSI.RESET}")
        
        # Conta quantos jogadores estão no canal global
        if channel_name == "global":
            global_count = sum(1 for p in self.game.players.values() if "global" in p.channels)
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Jogadores no canal global: {global_count}{ANSI.RESET}")
    
    async def cmd_leave(self, player: Player, channel_name: str):
        """Comando leave - sai de um canal"""
        if not channel_name:
            await self.send_message(player, f"{ANSI.YELLOW}Sair de qual canal? Use: leave <canal>{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Você está nos canais: {', '.join(player.channels)}{ANSI.RESET}")
            return
        
        channel_name = channel_name.lower().strip()
        
        # Não pode sair do canal local
        if channel_name == "local":
            await self.send_message(player, f"{ANSI.YELLOW}Você não pode sair do canal 'local'. Ele sempre está ativo.{ANSI.RESET}")
            return
        
        # Verifica se está no canal
        if channel_name not in player.channels:
            await self.send_message(player, f"{ANSI.YELLOW}Você não está no canal '{channel_name}'.{ANSI.RESET}")
            return
        
        # Remove do canal
        player.channels.remove(channel_name)
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você saiu do canal '{channel_name}'.{ANSI.RESET}")
    
    async def cmd_channels(self, player: Player):
        """Comando channels - lista canais disponíveis e canais que o jogador está inscrito"""
        available_channels = {
            "local": "Canal padrão - sempre ativo. Mensagens da sua sala atual.",
            "global": "Canal global - precisa fazer join. Mensagens de todos os jogadores online."
        }
        
        message = f"\r\n{ANSI.BOLD}=== Canais de Chat ==={ANSI.RESET}\r\n\r\n"
        
        # Lista canais disponíveis
        message += f"{ANSI.BRIGHT_CYAN}Canais Disponíveis:{ANSI.RESET}\r\n"
        for channel_id, description in available_channels.items():
            status = ""
            if channel_id in player.channels:
                status = f" {ANSI.BRIGHT_GREEN}[INSCRITO]{ANSI.RESET}"
            elif channel_id == "local":
                status = f" {ANSI.BRIGHT_GREEN}[ATIVO]{ANSI.RESET}"
            
            message += f"  {ANSI.BRIGHT_YELLOW}{channel_id.upper()}{ANSI.RESET}{status}\r\n"
            message += f"    {ANSI.BRIGHT_BLACK}→{ANSI.RESET} {description}\r\n\r\n"
        
        # Lista canais que o jogador está inscrito
        message += f"{ANSI.BRIGHT_GREEN}Seus Canais Ativos:{ANSI.RESET}\r\n"
        for channel in player.channels:
            message += f"  {ANSI.BRIGHT_CYAN}•{ANSI.RESET} {channel.upper()}\r\n"
        
        message += f"\r\n{ANSI.BRIGHT_YELLOW}Comandos:{ANSI.RESET}\r\n"
        message += f"  {ANSI.BRIGHT_CYAN}join <canal>{ANSI.RESET} - Entra em um canal\r\n"
        message += f"  {ANSI.BRIGHT_CYAN}leave <canal>{ANSI.RESET} - Sai de um canal\r\n"
        message += f"  {ANSI.BRIGHT_CYAN}say <mensagem>{ANSI.RESET} - Fala no canal local\r\n"
        message += f"  {ANSI.BRIGHT_CYAN}shout <mensagem>{ANSI.RESET} - Fala no canal global (requer join)\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_inspect(self, player: Player, target_name: str):
        """Comando inspect - visualiza equipamentos e estatísticas de outro jogador"""
        if not target_name:
            await self.send_message(player, f"{ANSI.YELLOW}Inspecionar quem? Use: inspect <nome do jogador>{ANSI.RESET}")
            return
        
        target_name = target_name.strip()
        
        # Verifica se é o próprio jogador
        if target_name.lower() == player.name.lower():
            await self.send_message(player, f"{ANSI.YELLOW}Use 'stats' para ver suas próprias estatísticas.{ANSI.RESET}")
            return
        
        # Busca jogadores na mesma sala
        players_in_room = self.game.get_players_in_room(player.world_id, player.room_id)
        target_player = None
        
        for p in players_in_room:
            if p.name.lower() == target_name.lower():
                target_player = p
                break
        
        if not target_player:
            await self.send_message(player, f"{ANSI.RED}Jogador '{target_name}' não está nesta sala.{ANSI.RESET}")
            return
        
        # Cria mensagem de inspeção
        from mud.systems.classes import ClassSystem
        class_system = ClassSystem()
        
        message = f"\r\n{ANSI.BOLD}=== Inspeção de {target_player.name} ==={ANSI.RESET}\r\n\r\n"
        
        # Classe, Raça e Gênero
        if target_player.class_id:
            cls = class_system.get_class(target_player.class_id)
            if cls:
                message += f"{cls.icon} {ANSI.BRIGHT_GREEN}Classe:{ANSI.RESET} {cls.name}\r\n"
        if target_player.race_id:
            race = class_system.get_race(target_player.race_id)
            if race:
                message += f"{race.icon} {ANSI.BRIGHT_GREEN}Raça:{ANSI.RESET} {race.name}\r\n"
        if target_player.gender_id:
            gender = class_system.get_gender(target_player.gender_id)
            if gender:
                message += f"{gender.icon} {ANSI.BRIGHT_GREEN}Gênero:{ANSI.RESET} {gender.name}\r\n"
        
        message += f"\r\n{ANSI.BOLD}Atributos:{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_GREEN}Nível:{ANSI.RESET} {target_player.level}/30\r\n"
        
        # Barras visuais
        from mud.utils.visuals import format_hp_bar, format_stamina_bar
        message += f"{format_hp_bar(target_player.current_hp, target_player.max_hp)}\r\n"
        message += f"{format_stamina_bar(target_player.current_stamina, target_player.max_stamina)}\r\n"
        
        # Stats com equipamento
        total_attack = target_player.get_total_attack(self.game_data)
        total_defense = target_player.get_total_defense(self.game_data)
        
        if total_attack > target_player.attack or total_defense > target_player.defense:
            # Mostra stats base e total
            attack_bonus = total_attack - target_player.attack
            defense_bonus = total_defense - target_player.defense
            message += f"{ANSI.BRIGHT_CYAN}Ataque:{ANSI.RESET} {target_player.attack}"
            if attack_bonus > 0:
                message += f" {ANSI.BRIGHT_GREEN}(+{attack_bonus} equipamento) = {total_attack}{ANSI.RESET}\r\n"
            else:
                message += "\r\n"
            
            message += f"{ANSI.BRIGHT_BLUE}Defesa:{ANSI.RESET} {target_player.defense}"
            if defense_bonus > 0:
                message += f" {ANSI.BRIGHT_GREEN}(+{defense_bonus} equipamento) = {total_defense}{ANSI.RESET}\r\n"
            else:
                message += "\r\n"
        else:
            message += f"{ANSI.BRIGHT_CYAN}Ataque:{ANSI.RESET} {total_attack}\r\n"
            message += f"{ANSI.BRIGHT_BLUE}Defesa:{ANSI.RESET} {total_defense}\r\n"
        
        # Mostra equipamento
        if target_player.equipment:
            message += f"\r\n{ANSI.BOLD}Equipamento:{ANSI.RESET}\r\n"
            for slot, item_id in target_player.equipment.items():
                if item_id:
                    item = self.game_data.get_item(item_id)
                    if item:
                        rarity_color = item.get_rarity_color()
                        message += f"  {ANSI.BRIGHT_CYAN}{slot.capitalize()}:{ANSI.RESET} {rarity_color}{item.name}{ANSI.RESET}"
                        # Mostra stats do item se tiver
                        if item.stats:
                            stats_str = []
                            if item.stats.get('attack', 0) > 0:
                                stats_str.append(f"+{item.stats['attack']} ATK")
                            if item.stats.get('defense', 0) > 0:
                                stats_str.append(f"+{item.stats['defense']} DEF")
                            if item.stats.get('hp', 0) > 0:
                                stats_str.append(f"+{item.stats['hp']} HP")
                            if stats_str:
                                message += f" {ANSI.BRIGHT_BLACK}({', '.join(stats_str)}){ANSI.RESET}"
                        message += "\r\n"
                    else:
                        message += f"  {ANSI.BRIGHT_CYAN}{slot.capitalize()}:{ANSI.RESET} [Item não encontrado]\r\n"
        else:
            message += f"\r\n{ANSI.YELLOW}Nenhum equipamento.{ANSI.RESET}\r\n"
        
        # Status de combate
        if target_player.name in self.in_combat:
            message += f"\r\n{ANSI.RED}⚔️ [EM COMBATE]{ANSI.RESET}\r\n"
        
        # Status AFK
        if hasattr(target_player, 'is_afk') and target_player.is_afk:
            afk_msg = getattr(target_player, 'afk_message', 'AFK')
            message += f"\r\n{ANSI.BRIGHT_BLACK}💤 [AFK: {afk_msg}]{ANSI.RESET}\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_who(self, player: Player):
        """Comando who - lista jogadores online com detalhes"""
        online_players = list(self.game.players.values())
        if not online_players:
            await self.send_message(player, f"{ANSI.YELLOW}Nenhum jogador online.{ANSI.RESET}")
            return
        
        message = f"\r\n{ANSI.BOLD}=== Jogadores Online ({len(online_players)}) ==={ANSI.RESET}\r\n\r\n"
        
        for p in online_players:
            world = self.world_manager.get_world(p.world_id)
            world_name = world.name if world else "Desconhecido"
            
            # Tenta buscar sala (pode ser dungeon)
            room = self.world_manager.get_room(p.world_id, p.room_id, self.dungeon_manager)
            room_name = room.name if room else "Desconhecido"
            
            # Status de combate
            combat_status = ""
            if p.name in self.in_combat:
                combat_status = f" {ANSI.RED}[EM COMBATE]{ANSI.RESET}"
            
            # Status AFK
            afk_status = ""
            if hasattr(p, 'is_afk') and p.is_afk:
                afk_msg = getattr(p, 'afk_message', 'AFK')
                afk_status = f" {ANSI.BRIGHT_BLACK}[AFK: {afk_msg}]{ANSI.RESET}"
            
            # Informações do jogador
            level_info = f"{ANSI.BRIGHT_YELLOW}Nível {p.level}{ANSI.RESET}"
            hp_info = f"{ANSI.BRIGHT_RED}HP: {p.current_hp}/{p.max_hp}{ANSI.RESET}"
            
            # Indica se é o próprio jogador
            is_self = " (você)" if p.name == player.name else ""
            
            message += f"{ANSI.BRIGHT_CYAN}{p.name}{is_self}{ANSI.RESET} {level_info} {hp_info}{combat_status}{afk_status}\r\n"
            message += f"  {ANSI.BRIGHT_BLACK}→{ANSI.RESET} {ANSI.BRIGHT_YELLOW}{world_name}{ANSI.RESET} / {ANSI.BRIGHT_YELLOW}{room_name}{ANSI.RESET}\r\n"
        
        message += f"\r\n{ANSI.BRIGHT_GREEN}Total: {len(online_players)} jogador(es) online{ANSI.RESET}\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_shop(self, player: Player, npc_name: str):
        """Comando shop - lista itens à venda de um NPC"""
        if not npc_name:
            await self.send_message(player, f"{ANSI.YELLOW}Ver loja de quem? Use: shop <nome do NPC>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and npc_name.lower() in npc.name.lower():
                if npc.npc_type == 'shopkeeper' and npc.shop_items:
                    message = f"\r\n{Colors.TITLE}=== Loja de {npc.name} ==={Colors.RESET}\r\n\r\n"
                    
                    # Agrupa itens por tipo para melhor organização
                    potions = []
                    equipment = []
                    other = []
                    
                    for shop_item in npc.shop_items:
                        item_id = shop_item.get('item_id') if isinstance(shop_item, dict) else shop_item
                        price = shop_item.get('price', 0) if isinstance(shop_item, dict) else 0
                        item = self.game_data.get_item(item_id)
                        if item:
                            item_data = (item, price)
                            item_name_lower = item.name.lower()
                            if 'poção' in item_name_lower or 'pocao' in item_name_lower:
                                potions.append(item_data)
                            elif any(x in item_name_lower for x in ['espada', 'armadura', 'escudo', 'arma', 'armor']):
                                equipment.append(item_data)
                            else:
                                other.append(item_data)
                    
                    # Mostra poções primeiro
                    if potions:
                        message += f"{Colors.CATEGORY}Poções:{Colors.RESET}\r\n"
                        for item, price in potions:
                            message += f"  {Colors.ITEM}{item.name}{Colors.RESET} - {Colors.VALUE}{price} moedas{Colors.RESET}\r\n"
                            if item.description:
                                message += f"    {Colors.DESCRIPTION}{item.description}{Colors.RESET}\r\n"
                        message += "\r\n"
                    
                    # Mostra equipamentos
                    if equipment:
                        message += f"{Colors.CATEGORY}Equipamentos:{Colors.RESET}\r\n"
                        for item, price in equipment:
                            message += f"  {Colors.ITEM}{item.name}{Colors.RESET} - {Colors.VALUE}{price} moedas{Colors.RESET}\r\n"
                            if item.description:
                                message += f"    {Colors.DESCRIPTION}{item.description}{Colors.RESET}\r\n"
                        message += "\r\n"
                    
                    # Mostra outros itens
                    if other:
                        message += f"{Colors.CATEGORY}Outros:{Colors.RESET}\r\n"
                        for item, price in other:
                            message += f"  {Colors.ITEM}{item.name}{Colors.RESET} - {Colors.VALUE}{price} moedas{Colors.RESET}\r\n"
                            if item.description:
                                message += f"    {Colors.DESCRIPTION}{item.description}{Colors.RESET}\r\n"
                        message += "\r\n"
                    
                    message += f"{Colors.ACTION}Use: buy <item> <npc> para comprar{Colors.RESET}\r\n"
                    await self.send_message(player, message)
                    return
                elif npc.npc_type == 'trader':
                    await self.send_message(player, f"{ANSI.YELLOW}{npc.name} é um negociante, não um vendedor.{ANSI.RESET}")
                    await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use: trade {npc.name} para ver opções de troca{ANSI.RESET}")
                    return
                else:
                    await self.send_message(player, f"{ANSI.YELLOW}{npc.name} não tem uma loja.{ANSI.RESET}")
                    return
        
        await self.send_message(player, f"{ANSI.RED}NPC '{npc_name}' não encontrado aqui.{ANSI.RESET}")
    
    async def cmd_buy(self, player: Player, args: str):
        """Comando buy - compra item de um NPC"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Use: buy <item> <npc>{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use 'shop <npc>' para ver itens à venda.{ANSI.RESET}")
            return
        
        parts = args.split()
        if len(parts) < 2:
            await self.send_message(player, f"{ANSI.YELLOW}Use: buy <item> <npc>{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Exemplo: buy 'Poção de Vida Pequena' 'Vendedor Amigável'{ANSI.RESET}")
            return
        
        # Tenta encontrar o NPC primeiro (pode estar no início ou fim)
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        npc_found = None
        npc_name = None
        item_name = None
        
        # Primeiro, tenta encontrar o NPC pelo último termo
        possible_npc_name = parts[-1]
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and possible_npc_name.lower() in npc.name.lower():
                npc_found = npc
                npc_name = possible_npc_name
                item_name = ' '.join(parts[:-1])
                break
        
        # Se não encontrou, tenta pelo primeiro termo
        if not npc_found:
            possible_npc_name = parts[0]
            for npc_id in entities['npcs']:
                npc = self.game_data.get_npc(player.world_id, npc_id)
                if npc and possible_npc_name.lower() in npc.name.lower():
                    npc_found = npc
                    npc_name = possible_npc_name
                    item_name = ' '.join(parts[1:])
                    break
        
        if not npc_found:
            await self.send_message(player, f"{ANSI.RED}NPC não encontrado aqui.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use 'look' para ver NPCs disponíveis.{ANSI.RESET}")
            return
        
        if npc_found.npc_type != 'shopkeeper':
            await self.send_message(player, f"{ANSI.YELLOW}{npc_found.name} não vende itens.{ANSI.RESET}")
            return
        
        if not npc_found.shop_items:
            await self.send_message(player, f"{ANSI.YELLOW}{npc_found.name} não tem itens à venda no momento.{ANSI.RESET}")
            return
        
        # Busca o item
        item_found = None
        item_id = None
        price = 0
        
        item_name_lower = item_name.lower().strip()
        
        for shop_item in npc_found.shop_items:
            current_item_id = shop_item.get('item_id') if isinstance(shop_item, dict) else shop_item
            current_price = shop_item.get('price', 0) if isinstance(shop_item, dict) else 0
            current_item = self.game_data.get_item(current_item_id)
            
            if current_item:
                # Tenta múltiplas formas de correspondência
                item_name_lower_clean = item_name_lower
                item_name_db_lower = current_item.name.lower()
                
                # Verifica se o nome buscado está no nome do item ou vice-versa
                if (item_name_lower_clean in item_name_db_lower or 
                    item_name_db_lower in item_name_lower_clean or
                    item_name_lower_clean == item_name_db_lower):
                    # Se houver múltiplas correspondências, prefere a mais exata
                    if not item_found or len(current_item.name) < len(item_found.name):
                        item_found = current_item
                        item_id = current_item_id
                        price = current_price
        
        if not item_found:
            # Lista itens disponíveis para ajudar o usuário
            await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está à venda.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.BRIGHT_CYAN}Use 'shop {npc_found.name}' para ver todos os itens disponíveis.{ANSI.RESET}")
            return
        
        # Tenta comprar
        if player.spend_gold(price):
            player.add_item(item_id)
            await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você comprou {item_found.name} por {price} moedas!{ANSI.RESET}")
            
            # Salva inventário e ouro
            stats = {
                'hp': player.current_hp,
                'max_hp': player.max_hp,
                'current_stamina': player.current_stamina,
                'max_stamina': player.max_stamina,
                'level': player.level,
                'experience': player.experience,
                'attack': player.attack,
                'defense': player.defense,
                'gold': player.gold,
                'inventory': player.inventory,
                'equipment': player.equipment,
                'active_quests': player.active_quests,
                'quest_progress': player.quest_progress,
                'completed_quests': player.completed_quests,
                'known_spells': player.known_spells,
                'equipped_spells': player.equipped_spells,
                'active_perks': player.active_perks,
                'spell_cooldowns': player.spell_cooldowns,
                'unspent_points': player.unspent_points
            }
            self.database.update_player_stats(player.name, stats)
        else:
            await self.send_message(player, f"{ANSI.RED}Você não tem ouro suficiente! Precisa de {price} moedas. Você tem {player.gold}.{ANSI.RESET}")
    
    async def cmd_sell(self, player: Player, args: str):
        """Comando sell - vende item para um NPC"""
        parts = args.split()
        if len(parts) < 2:
            await self.send_message(player, f"{ANSI.YELLOW}Use: sell <item> <npc>{ANSI.RESET}")
            return
        
        item_name = ' '.join(parts[:-1])
        npc_name = parts[-1]
        
        # Procura item no inventário
        for item_id in player.inventory:
            item = self.game_data.get_item(item_id)
            if item and item_name.lower() in item.name.lower():
                # NPCs geralmente compram por 50% do valor
                sell_price = max(1, item.value // 2)
                player.remove_item(item_id)
                player.add_gold(sell_price)
                await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Você vendeu {item.name} por {sell_price} moedas!{ANSI.RESET}")
                return
        
        await self.send_message(player, f"{ANSI.RED}Item '{item_name}' não está no seu inventário.{ANSI.RESET}")
    
    async def cmd_trade(self, player: Player, npc_name: str):
        """Comando trade - troca itens com NPC"""
        if not npc_name:
            await self.send_message(player, f"{ANSI.YELLOW}Trocar com quem? Use: trade <nome do NPC>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and npc_name.lower() in npc.name.lower():
                if npc.npc_type == 'trader' and npc.trade_items:
                    give_items = npc.trade_items.get('give', [])
                    receive_items = npc.trade_items.get('receive', [])
                    
                    message = f"\r\n{ANSI.BOLD}=== Troca com {npc.name} ==={ANSI.RESET}\r\n\r\n"
                    
                    # Mostra o que o NPC quer receber
                    message += f"{ANSI.BRIGHT_YELLOW}Você precisa dar:{ANSI.RESET}\r\n"
                    give_items_list = []
                    for item_id in give_items:
                        item = self.game_data.get_item(item_id)
                        if item:
                            player_has = player.get_item_count(item_id)
                            has_mark = f"{ANSI.BRIGHT_GREEN}✓{ANSI.RESET}" if player_has > 0 else f"{ANSI.RED}✗{ANSI.RESET}"
                            message += f"  {has_mark} {item.name}"
                            if player_has > 0:
                                message += f" {ANSI.BRIGHT_CYAN}(você tem {player_has}){ANSI.RESET}"
                            message += f" - {item.description}\r\n"
                            give_items_list.append((item_id, item))
                    
                    message += f"\r\n{ANSI.BRIGHT_GREEN}Você recebe:{ANSI.RESET}\r\n"
                    receive_items_list = []
                    for item_id in receive_items:
                        item = self.game_data.get_item(item_id)
                        if item:
                            message += f"  {item.name} - {item.description}\r\n"
                            receive_items_list.append((item_id, item))
                    
                    # Verifica se jogador tem os itens necessários
                    can_trade = True
                    missing_items = []
                    for item_id, item in give_items_list:
                        if not player.has_item(item_id):
                            can_trade = False
                            missing_items.append(item.name)
                    
                    if can_trade:
                        # Faz a troca
                        for item_id in give_items:
                            player.remove_item(item_id)
                        for item_id in receive_items:
                            player.add_item(item_id)
                        
                        message += f"\r\n{ANSI.BRIGHT_GREEN}✨ Troca realizada com sucesso! ✨{ANSI.RESET}\r\n"
                        message += f"{ANSI.BRIGHT_YELLOW}Você entregou:{ANSI.RESET} "
                        for item_id, item in give_items_list:
                            message += f"{item.name}, "
                        message = message.rstrip(", ") + "\r\n"
                        message += f"{ANSI.BRIGHT_GREEN}Você recebeu:{ANSI.RESET} "
                        for item_id, item in receive_items_list:
                            message += f"{item.name}, "
                        message = message.rstrip(", ") + "\r\n"
                        
                        # Salva inventário
                        stats = {
                            'hp': player.current_hp,
                            'max_hp': player.max_hp,
                            'current_stamina': player.current_stamina,
                            'max_stamina': player.max_stamina,
                            'level': player.level,
                            'experience': player.experience,
                            'attack': player.attack,
                            'defense': player.defense,
                            'gold': player.gold,
                            'inventory': player.inventory,
                            'equipment': player.equipment,
                            'active_quests': player.active_quests,
                            'quest_progress': player.quest_progress,
                            'completed_quests': player.completed_quests,
                            'known_spells': player.known_spells,
                            'equipped_spells': player.equipped_spells,
                            'active_perks': player.active_perks,
                            'spell_cooldowns': player.spell_cooldowns,
                            'unspent_points': player.unspent_points
                        }
                        self.database.update_player_stats(player.name, stats)
                    else:
                        message += f"\r\n{ANSI.RED}Você não tem os itens necessários para esta troca.{ANSI.RESET}\r\n"
                        if missing_items:
                            message += f"{ANSI.YELLOW}Faltam: {', '.join(missing_items)}{ANSI.RESET}\r\n"
                    
                    await self.send_message(player, message)
                    return
                else:
                    await self.send_message(player, f"{ANSI.YELLOW}{npc.name} não faz trocas.{ANSI.RESET}")
                    return
        
        await self.send_message(player, f"{ANSI.RED}NPC '{npc_name}' não encontrado aqui.{ANSI.RESET}")
    
    async def cmd_quest(self, player: Player, npc_name: str):
        """Comando quest - lista quests disponíveis de um NPC"""
        if not npc_name:
            # Lista todas as quests ativas do jogador
            if player.active_quests:
                message = f"\r\n{ANSI.BOLD}=== Suas Quests Ativas ==={ANSI.RESET}\r\n"
                for quest_id in player.active_quests:
                    quest = self.quest_manager.get_quest(player.world_id, quest_id)
                    if quest:
                        progress = player.quest_progress.get(quest_id, {})
                        message += f"{ANSI.BRIGHT_CYAN}{quest.name}{ANSI.RESET}\r\n"
                        message += f"  {quest.description}\r\n"
                        # Mostra progresso
                        for obj in quest.objectives:
                            obj_type = obj.get('type')
                            target = obj.get('target')
                            amount = obj.get('amount', 1)
                            progress_key = f"{obj_type}_{target}"
                            current = progress.get(progress_key, 0)
                            message += f"  {ANSI.YELLOW}Progresso: {current}/{amount}{ANSI.RESET}\r\n"
                await self.send_message(player, message)
            else:
                await self.send_message(player, f"{ANSI.YELLOW}Você não tem quests ativas.{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc and npc_name.lower() in npc.name.lower():
                if npc.npc_type == 'quest_giver' or npc.quests:
                    quests = self.quest_manager.get_quests_by_npc(player.world_id, npc_id)
                    
                    if not quests:
                        # Tenta gerar uma quest dinamicamente (com IA se disponível)
                        context = {
                            'world_id': player.world_id,
                            'room_id': player.room_id
                        }
                        
                        # Tenta primeiro com IA
                        quest = await self.quest_manager.generate_quest_with_ai(
                            player.world_id, npc_id, npc.name, npc.lore, context
                        )
                        
                        # Se IA falhar, usa template
                        if not quest:
                            quest = self.quest_manager.generate_quest(player.world_id, npc_id, npc.name, context)
                        
                        if quest:
                            quests = [quest]
                    
                    if quests:
                        message = f"\r\n{ANSI.BOLD}=== Quests de {npc.name} ==={ANSI.RESET}\r\n"
                        for quest in quests:
                            if quest.id not in player.completed_quests:
                                status = "Ativa" if quest.id in player.active_quests else "Disponível"
                                message += f"{ANSI.BRIGHT_CYAN}{quest.name}{ANSI.RESET} [{status}]\r\n"
                                message += f"  {quest.description}\r\n"
                                if quest.lore:
                                    message += f"  {ANSI.BRIGHT_MAGENTA}{quest.lore}{ANSI.RESET}\r\n"
                                message += f"  {ANSI.BRIGHT_YELLOW}Recompensas:{ANSI.RESET} "
                                if quest.rewards.get('gold'):
                                    message += f"{quest.rewards['gold']} moedas, "
                                if quest.rewards.get('experience'):
                                    message += f"{quest.rewards['experience']} XP, "
                                message = message.rstrip(", ") + "\r\n\r\n"
                        message += f"{ANSI.BRIGHT_GREEN}Use: accept <nome da quest> <npc> para aceitar{ANSI.RESET}\r\n"
                        await self.send_message(player, message)
                        return
                    else:
                        await self.send_message(player, f"{ANSI.YELLOW}{npc.name} não tem quests disponíveis.{ANSI.RESET}")
                        return
                else:
                    await self.send_message(player, f"{ANSI.YELLOW}{npc.name} não oferece quests.{ANSI.RESET}")
                    return
        
        await self.send_message(player, f"{ANSI.RED}NPC '{npc_name}' não encontrado aqui.{ANSI.RESET}")
    
    async def cmd_accept_quest(self, player: Player, args: str):
        """Comando accept - aceita uma quest"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Use: accept <nome da quest> <npc>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Primeiro, tenta encontrar o NPC na sala
        # Procura pelo NPC mais longo que corresponde ao final da string
        found_npc = None
        found_npc_id = None
        npc_match_length = 0
        
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc:
                # Tenta encontrar o nome do NPC no final da string
                npc_name_lower = npc.name.lower()
                args_lower = args.lower()
                
                # Verifica se o nome do NPC está no final da string
                if args_lower.endswith(npc_name_lower):
                    # Verifica se é um match completo (precedido por espaço ou início da string)
                    start_pos = args_lower.rfind(npc_name_lower)
                    if start_pos > 0:
                        # Verifica se há espaço antes ou é o início
                        if args_lower[start_pos - 1] == ' ' or start_pos == 0:
                            # Se encontrou um NPC mais longo, usa este
                            if len(npc_name_lower) > npc_match_length:
                                found_npc = npc
                                found_npc_id = npc_id
                                npc_match_length = len(npc_name_lower)
                    elif start_pos == 0:
                        # NPC está no início (caso raro, mas possível)
                        if len(npc_name_lower) > npc_match_length:
                            found_npc = npc
                            found_npc_id = npc_id
                            npc_match_length = len(npc_name_lower)
        
        if not found_npc:
            # Se não encontrou pelo nome completo, tenta busca parcial
            parts = args.split()
            if len(parts) < 2:
                await self.send_message(player, f"{ANSI.YELLOW}Use: accept <nome da quest> <npc>{ANSI.RESET}")
                return
            
            # Tenta com a última palavra como NPC
            npc_name = parts[-1]
            for npc_id in entities['npcs']:
                npc = self.game_data.get_npc(player.world_id, npc_id)
                if npc and npc_name.lower() in npc.name.lower():
                    found_npc = npc
                    found_npc_id = npc_id
                    quest_name = ' '.join(parts[:-1])
                    break
            
            if not found_npc:
                await self.send_message(player, f"{ANSI.RED}NPC não encontrado aqui.{ANSI.RESET}")
                return
        else:
            # Extrai o nome da quest removendo o nome do NPC do final
            quest_name = args[:len(args) - len(found_npc.name) - 1].strip() if len(args) > len(found_npc.name) else args
        
        # Agora procura a quest
        quests = self.quest_manager.get_quests_by_npc(player.world_id, found_npc_id)
        
        if not quests:
            await self.send_message(player, f"{ANSI.YELLOW}{found_npc.name} não tem quests disponíveis.{ANSI.RESET}")
            return
        
        # Procura a quest pelo nome
        matched_quest = None
        quest_name_lower = quest_name.lower()
        
        for quest in quests:
            # Verifica se o nome da quest está contido no nome completo
            if quest_name_lower in quest.name.lower() or quest.name.lower().startswith(quest_name_lower):
                matched_quest = quest
                break
        
        if not matched_quest:
            # Lista quests disponíveis para ajudar
            message = f"{ANSI.RED}Quest '{quest_name}' não encontrada.{ANSI.RESET}\r\n"
            message += f"{ANSI.BRIGHT_YELLOW}Quests disponíveis de {found_npc.name}:{ANSI.RESET}\r\n"
            for quest in quests:
                if quest.id not in player.completed_quests and quest.id not in player.active_quests:
                    message += f"  - {quest.name}\r\n"
            await self.send_message(player, message)
            return
        
        quest = matched_quest
        
        # Verifica se já completou
        if quest.id in player.completed_quests:
            await self.send_message(player, f"{ANSI.YELLOW}Você já completou esta quest.{ANSI.RESET}")
            return
        
        # Verifica se já tem ativa
        if quest.id in player.active_quests:
            await self.send_message(player, f"{ANSI.YELLOW}Você já tem esta quest ativa.{ANSI.RESET}")
            return
        
        # Aceita quest
        player.active_quests.append(quest.id)
        player.quest_progress[quest.id] = {}
        
        # Salva progresso no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests
        }
        self.database.update_player_stats(player.name, stats)
        
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Quest '{quest.name}' aceita!{ANSI.RESET}")
        await self.send_message(player, f"{quest.description}\r\n")
    
    async def cmd_complete_quest(self, player: Player, args: str):
        """Comando complete - completa uma quest"""
        if not args:
            await self.send_message(player, f"{ANSI.YELLOW}Completar qual quest? Use: complete <nome da quest> <npc>{ANSI.RESET}")
            return
        
        entities = self.game_data.get_room_entities(player.world_id, player.room_id)
        
        # Mesmo parsing inteligente do cmd_accept_quest
        found_npc = None
        found_npc_id = None
        npc_match_length = 0
        
        for npc_id in entities['npcs']:
            npc = self.game_data.get_npc(player.world_id, npc_id)
            if npc:
                npc_name_lower = npc.name.lower()
                args_lower = args.lower()
                
                if args_lower.endswith(npc_name_lower):
                    start_pos = args_lower.rfind(npc_name_lower)
                    if start_pos > 0:
                        if args_lower[start_pos - 1] == ' ' or start_pos == 0:
                            if len(npc_name_lower) > npc_match_length:
                                found_npc = npc
                                found_npc_id = npc_id
                                npc_match_length = len(npc_name_lower)
                    elif start_pos == 0:
                        if len(npc_name_lower) > npc_match_length:
                            found_npc = npc
                            found_npc_id = npc_id
                            npc_match_length = len(npc_name_lower)
        
        if not found_npc:
            parts = args.split()
            if len(parts) < 2:
                await self.send_message(player, f"{ANSI.YELLOW}Use: complete <nome da quest> <npc>{ANSI.RESET}")
                return
            
            npc_name = parts[-1]
            for npc_id in entities['npcs']:
                npc = self.game_data.get_npc(player.world_id, npc_id)
                if npc and npc_name.lower() in npc.name.lower():
                    found_npc = npc
                    found_npc_id = npc_id
                    quest_name = ' '.join(parts[:-1])
                    break
            
            if not found_npc:
                await self.send_message(player, f"{ANSI.RED}NPC não encontrado aqui.{ANSI.RESET}")
                return
        else:
            quest_name = args[:len(args) - len(found_npc.name) - 1].strip() if len(args) > len(found_npc.name) else args
        
        quests = self.quest_manager.get_quests_by_npc(player.world_id, found_npc_id)
        
        matched_quest = None
        quest_name_lower = quest_name.lower()
        
        for quest in quests:
            if quest_name_lower in quest.name.lower() or quest.name.lower().startswith(quest_name_lower):
                matched_quest = quest
                break
        
        if not matched_quest:
            await self.send_message(player, f"{ANSI.RED}Quest '{quest_name}' não encontrada.{ANSI.RESET}")
            return
        
        quest = matched_quest
        
        if quest.id not in player.active_quests:
            await self.send_message(player, f"{ANSI.YELLOW}Você não tem esta quest ativa.{ANSI.RESET}")
            return
        
        # Verifica progresso e objetivos especiais (como sacrifício)
        progress = player.quest_progress.get(quest.id, {})
        
        # Verifica se tem objetivos de sacrifício que precisam ser resolvidos
        sacrifice_objectives = [obj for obj in quest.objectives if obj.get('type') == 'sacrifice_ability']
        
        if sacrifice_objectives:
            # Quest requer sacrifício - tenta extrair nome da habilidade dos argumentos
            # Formato: complete <quest> <npc> [habilidade]
            parts = args.split()
            sacrifice_name = None
            
            # Tenta encontrar o nome da habilidade (pode estar no final)
            # Primeiro, verifica se o último termo não é o nome do NPC
            if len(parts) > 2:
                # Pode ter: complete "Mapa do Tesouro" Pirata "Nome da Magia"
                # Ou: complete Mapa Pirata Magia
                # Remove quest name e npc name, o resto pode ser a habilidade
                remaining = ' '.join(parts[2:]) if len(parts) > 2 else None
                if remaining and remaining.lower() not in found_npc.name.lower():
                    sacrifice_name = remaining
            
            # Quest requer sacrifício - precisa lidar com isso antes de completar
            sacrifice_completed = await self._handle_quest_sacrifice(player, quest, sacrifice_objectives, progress, sacrifice_name)
            if not sacrifice_completed:
                return  # O jogador precisa especificar qual habilidade sacrificar
        
        # Verifica se todos os objetivos coletáveis/kill foram completados
        collectable_objectives = [obj for obj in quest.objectives if obj.get('type') in ['collect', 'kill']]
        all_collectables_done = True
        for obj in collectable_objectives:
            obj_type = obj.get('type')
            target = obj.get('target')
            amount = obj.get('amount', 1)
            progress_key = f"{obj_type}_{target}"
            if progress.get(progress_key, 0) < amount:
                all_collectables_done = False
                break
        
        if not all_collectables_done:
            await self.send_message(player, f"{ANSI.RED}Você ainda não completou todos os objetivos desta quest.{ANSI.RESET}")
            # Mostra progresso
            for obj in quest.objectives:
                obj_type = obj.get('type')
                if obj_type in ['collect', 'kill']:
                    target = obj.get('target')
                    amount = obj.get('amount', 1)
                    progress_key = f"{obj_type}_{target}"
                    current = progress.get(progress_key, 0)
                    await self.send_message(player, f"  {target}: {current}/{amount}")
            return
        
        # Verifica se tem itens coletáveis no inventário
        for obj in quest.objectives:
            if obj.get('type') == 'collect':
                item_id = obj.get('target')
                amount = obj.get('amount', 1)
                if not player.has_item(item_id, amount):
                    await self.send_message(player, f"{ANSI.RED}Você precisa ter {amount}x {item_id} no inventário para completar esta quest.{ANSI.RESET}")
                    return
                # Remove item do inventário
                for _ in range(amount):
                    player.remove_item(item_id)
        
        # Completa quest
        rewards = self.quest_manager.complete_quest(quest, player)
        
        # Salva progresso atualizado no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests,
            'known_spells': player.known_spells,
            'active_perks': player.active_perks
        }
        self.database.update_player_stats(player.name, stats)
        
        message = f"\r\n{ANSI.BRIGHT_GREEN}Quest '{quest.name}' completada!{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_YELLOW}Recompensas:{ANSI.RESET}\r\n"
        if rewards.get('gold'):
            message += f"  {rewards['gold']} moedas\r\n"
        if rewards.get('experience'):
            message += f"  {rewards['experience']} experiência\r\n"
        if rewards.get('items'):
            for item_id in rewards['items']:
                item = self.game_data.get_item(item_id)
                if item:
                    message += f"  {item.name}\r\n"
        await self.send_message(player, message)
    
    async def _handle_quest_sacrifice(self, player: Player, quest, sacrifice_objectives: List, progress: Dict, sacrifice_name: str = None) -> bool:
        """
        Função modularizada para lidar com sacrifício de habilidades em quests.
        Retorna True se o sacrifício foi completado, False caso contrário.
        Pode ser reutilizada para outras quests que requerem sacrifício.
        
        Args:
            player: O jogador
            quest: A quest que requer sacrifício
            sacrifice_objectives: Lista de objetivos de sacrifício
            progress: Progresso atual da quest
            sacrifice_name: Nome da habilidade a ser sacrificada (opcional, se None mostra lista)
        """
        for sacrifice_obj in sacrifice_objectives:
            target = sacrifice_obj.get('target', 'any')  # 'any', 'spell', 'perk', ou ID específico
            amount = sacrifice_obj.get('amount', 1)
            description = sacrifice_obj.get('description', 'Sacrificar uma habilidade')
            
            # Verifica se já foi sacrificado
            progress_key = f"sacrifice_{target}"
            if progress.get(progress_key, 0) >= amount:
                continue  # Já foi sacrificado
            
            # Lista habilidades disponíveis para sacrificar
            available_to_sacrifice = []
            
            # Verifica perks ativos
            if target == 'any' or target == 'perk':
                for perk_id in player.active_perks:
                    perk = self.spell_system.get_perk(perk_id)
                    if perk:
                        available_to_sacrifice.append(('perk', perk_id, perk.name, perk.icon))
            
            # Verifica magias conhecidas
            if target == 'any' or target == 'spell':
                for spell_id, spell_level in player.known_spells.items():
                    # Não permite sacrificar magias iniciais ou equipadas
                    starting_spells = self.spell_system.get_starting_spells(player.class_id)
                    if spell_id not in starting_spells and spell_id not in player.equipped_spells:
                        spell = self.spell_system.get_spell(spell_id)
                        if spell:
                            available_to_sacrifice.append(('spell', spell_id, spell.name, spell.icon))
            
            if not available_to_sacrifice:
                await self.send_message(player, 
                    f"{ANSI.RED}Você não tem habilidades para sacrificar!{ANSI.RESET}\r\n"
                    f"{ANSI.YELLOW}Esta quest requer que você sacrifique {amount} habilidade(s).{ANSI.RESET}")
                return False
            
            # Se não foi especificado qual sacrificar, mostra lista
            if not sacrifice_name:
                message = f"\r\n{ANSI.BOLD}{ANSI.RED}⚠ SACRIFÍCIO REQUERIDO ⚠{ANSI.RESET}\r\n"
                message += f"{ANSI.YELLOW}{description}{ANSI.RESET}\r\n\r\n"
                message += f"{ANSI.BRIGHT_CYAN}Habilidades disponíveis para sacrificar:{ANSI.RESET}\r\n"
                
                for i, (ability_type, ability_id, ability_name, ability_icon) in enumerate(available_to_sacrifice, 1):
                    type_text = f"{ANSI.BRIGHT_MAGENTA}[PERK]{ANSI.RESET}" if ability_type == 'perk' else f"{ANSI.BRIGHT_BLUE}[MAGIA]{ANSI.RESET}"
                    message += f"  {i}. {ability_icon} {ability_name} {type_text}\r\n"
                
                message += f"\r\n{ANSI.BRIGHT_YELLOW}Esta quest requer sacrifício!{ANSI.RESET}\r\n"
                message += f"{ANSI.BRIGHT_CYAN}Use: complete <nome da quest> <npc> <nome da habilidade>{ANSI.RESET}\r\n"
                message += f"{ANSI.BRIGHT_CYAN}Exemplo: complete 'Mapa do Tesouro' Pirata 'Nome da Magia'{ANSI.RESET}\r\n"
                await self.send_message(player, message)
                return False
            
            # Procura a habilidade especificada
            sacrifice_name_lower = sacrifice_name.lower()
            found_ability = None
            
            for ability_type, ability_id, ability_name, ability_icon in available_to_sacrifice:
                if sacrifice_name_lower in ability_name.lower():
                    found_ability = (ability_type, ability_id, ability_name, ability_icon)
                    break
            
            if not found_ability:
                await self.send_message(player, 
                    f"{ANSI.RED}Habilidade '{sacrifice_name}' não encontrada ou não pode ser sacrificada.{ANSI.RESET}\r\n"
                    f"{ANSI.YELLOW}Use 'complete <quest> <npc>' sem especificar habilidade para ver opções.{ANSI.RESET}")
                return False
            
            # Realiza o sacrifício
            ability_type, ability_id, ability_name, ability_icon = found_ability
            
            if ability_type == 'perk':
                player.active_perks.remove(ability_id)
                await self.send_message(player, 
                    f"{ANSI.RED}💀 Você sacrificou o perk '{ability_name}'! 💀{ANSI.RESET}\r\n")
            elif ability_type == 'spell':
                del player.known_spells[ability_id]
                # Remove se estiver equipada
                if ability_id in player.equipped_spells:
                    player.equipped_spells.remove(ability_id)
                await self.send_message(player, 
                    f"{ANSI.RED}💀 Você sacrificou a magia '{ability_name}'! 💀{ANSI.RESET}\r\n")
            
            # Marca como sacrificado no progresso
            if quest.id not in player.quest_progress:
                player.quest_progress[quest.id] = {}
            player.quest_progress[quest.id][progress_key] = progress.get(progress_key, 0) + 1
            
            return True
        
        return True  # Todos os sacrifícios já foram feitos
    
    async def cmd_cancel_quest(self, player: Player, args: str):
        """Comando cancel/abandon - cancela uma quest ativa"""
        if not args:
            # Lista quests ativas para o jogador escolher
            if player.active_quests:
                message = f"\r\n{ANSI.BOLD}=== Suas Quests Ativas ==={ANSI.RESET}\r\n"
                message += f"{ANSI.YELLOW}Use: cancel <nome da quest> para cancelar uma quest{ANSI.RESET}\r\n\r\n"
                for quest_id in player.active_quests:
                    quest = self.quest_manager.get_quest(player.world_id, quest_id)
                    if quest:
                        message += f"  - {quest.name}\r\n"
                await self.send_message(player, message)
            else:
                await self.send_message(player, f"{ANSI.YELLOW}Você não tem quests ativas para cancelar.{ANSI.RESET}")
            return
        
        # Busca a quest pelo nome
        quest_name_lower = args.lower()
        matched_quest = None
        matched_quest_id = None
        
        for quest_id in player.active_quests:
            quest = self.quest_manager.get_quest(player.world_id, quest_id)
            if quest:
                if quest_name_lower in quest.name.lower() or quest.name.lower().startswith(quest_name_lower):
                    matched_quest = quest
                    matched_quest_id = quest_id
                    break
        
        if not matched_quest:
            await self.send_message(player, f"{ANSI.RED}Quest '{args}' não encontrada nas suas quests ativas.{ANSI.RESET}")
            await self.send_message(player, f"{ANSI.YELLOW}Use 'quests' para ver suas quests ativas.{ANSI.RESET}")
            return
        
        # Remove a quest das ativas
        if matched_quest_id in player.active_quests:
            player.active_quests.remove(matched_quest_id)
        
        # Remove o progresso da quest
        if matched_quest_id in player.quest_progress:
            del player.quest_progress[matched_quest_id]
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests
        }
        self.database.update_player_stats(player.name, stats)
        
        await self.send_message(player, f"{ANSI.YELLOW}Quest '{matched_quest.name}' foi cancelada.{ANSI.RESET}")
        await self.send_message(player, f"{ANSI.YELLOW}Você pode aceitá-la novamente no futuro.{ANSI.RESET}")
    
    async def cmd_world_lore(self, player: Player):
        """Comando lore/world/intro - mostra a lore do mundo"""
        if not self.world_lore_manager:
            await self.send_message(player, f"{ANSI.YELLOW}Lore do mundo não disponível.{ANSI.RESET}")
            return
        
        lore_text = self.world_lore_manager.format_world_lore(player.world_id)
        if lore_text:
            await self.send_message(player, lore_text)
        else:
            await self.send_message(player, f"{ANSI.YELLOW}Não há lore disponível para este mundo.{ANSI.RESET}")
    
    async def cmd_help(self, player: Player, args: str = ""):
        """Comando help - mostra ajuda paginada e organizada por categoria"""
        
        # Organiza comandos por categoria
        categories = {
            'movimento': {
                'name': 'Movimento e Exploração',
                'icon': '🚶',
                'commands': [
                    ('look, l', 'Olha ao redor'),
                    ('norte, n / sul, s / leste, e / oeste, o', 'Move nas direções'),
                    ('entrar <porta>', 'Entra em uma dungeon/porta'),
                    ('sair', 'Sai da dungeon atual'),
                ]
            },
            'comunicacao': {
                'name': 'Comunicação',
                'icon': '💬',
                'commands': [
                    ('say <mensagem>', 'Fala algo na sala (local)'),
                    ('shout <mensagem>', 'Fala globalmente para todos'),
                    ('talk <nome>', 'Fala com NPC'),
                ]
            },
            'combate': {
                'name': 'Combate',
                'icon': '⚔️',
                'commands': [
                    ('attack <nome/id>', 'Ataca um monstro'),
                    ('use <nome>', 'Usa um item (pode usar durante combate!)'),
                    ('cast <magia> [alvo]', 'Lança uma magia'),
                ]
            },
            'personagem': {
                'name': 'Personagem',
                'icon': '👤',
                'commands': [
                    ('stats', 'Mostra suas estatísticas'),
                    ('inventory, inv, i [busca] [página]', 'Mostra inventário (com busca e paginação)'),
                    ('who, players, online', 'Lista jogadores online'),
                ]
            },
            'magias': {
                'name': 'Magias e Perks',
                'icon': '✨',
                'commands': [
                    ('spells, magias', 'Mostra suas magias'),
                    ('equipar <magia>', 'Equipa uma magia (max 3)'),
                    ('desequipar <magia>', 'Desequipa uma magia'),
                    ('melhorar <magia>', 'Melhora uma magia'),
                    ('aprender <magia>', 'Aprende uma nova magia'),
                    ('perks', 'Mostra seus perks'),
                    ('pontos magia <nome>', 'Distribui ponto em magia'),
                    ('pontos perk <nome>', 'Distribui ponto em perk'),
                ]
            },
            'itens': {
                'name': 'Itens e Inventário',
                'icon': '🎒',
                'commands': [
                    ('get <nome>', 'Pega item do chão'),
                    ('drop <nome>', 'Larga item'),
                    ('use <nome>', 'Usa um item'),
                ]
            },
            'npc': {
                'name': 'NPCs e Comércio',
                'icon': '🏪',
                'commands': [
                    ('shop <npc>', 'Lista itens à venda'),
                    ('buy <item> <npc>', 'Compra item de NPC'),
                    ('sell <item> <npc>', 'Vende item para NPC'),
                    ('trade <npc>', 'Troca itens com NPC'),
                ]
            },
            'quests': {
                'name': 'Quests',
                'icon': '📜',
                'commands': [
                    ('quest <npc>', 'Lista quests disponíveis'),
                    ('accept <quest> <npc>', 'Aceita uma quest'),
                    ('complete <quest> <npc>', 'Completa uma quest'),
                    ('cancel <quest>', 'Cancela uma quest ativa'),
                ]
            },
            'informacao': {
                'name': 'Informação',
                'icon': '📖',
                'commands': [
                    ('read <nome>', 'Lê lore de monstro/NPC'),
                    ('lore, world, intro', 'Lê a lore/introdução do mundo'),
                ]
            },
            'lobby': {
                'name': 'Comandos do Lobby',
                'icon': '🏛️',
                'commands': [
                    ('afk [mensagem]', 'Marca como AFK (só no lobby)'),
                    ('voltar / back', 'Volta do AFK (só no lobby)'),
                    ('lobby', 'Volta ao Hall de Entrada de qualquer lugar'),
                    ('respawn', 'Regenera HP e Stamina (só no lobby)'),
                    ('server / status_server', 'Mostra status do servidor (só no lobby)'),
                ]
            },
            'sistema': {
                'name': 'Sistema',
                'icon': '⚙️',
                'commands': [
                    ('help, ? [página]', 'Mostra esta ajuda'),
                    ('quit, exit', 'Sai do jogo'),
                ]
            }
        }
        
        # Parse argumentos
        page_num = 1
        if args:
            try:
                page_num = int(args.strip())
            except ValueError:
                # Se não for número, busca categoria pelo nome
                category_match = None
                for cat_id, cat_data in categories.items():
                    if args.lower() in cat_id.lower() or args.lower() in cat_data['name'].lower():
                        category_match = cat_id
                        break
                
                if category_match:
                    # Mostra apenas essa categoria
                    cat = categories[category_match]
                    message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}{cat['icon']} {cat['name']}{ANSI.RESET}\r\n\r\n"
                    for cmd, desc in cat['commands']:
                        message += f"{ANSI.BRIGHT_GREEN}{cmd:<30}{ANSI.RESET} - {desc}\r\n"
                    message += f"\r\n{ANSI.BRIGHT_CYAN}Use: help [página] para ver todas as categorias{ANSI.RESET}\r\n"
                    await self.send_message(player, message)
                    return
                else:
                    page_num = 1
        
        # Paginação
        category_list = list(categories.items())
        items_per_page = 3
        pages = self._paginate_list(category_list, items_per_page)
        total_pages = len(pages)
        
        # Valida página
        if page_num < 1:
            page_num = 1
        elif page_num > total_pages:
            page_num = total_pages
        
        current_page = pages[page_num - 1]
        
        # Monta mensagem
        message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Comandos Disponíveis ==={ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_BLACK}Página {page_num}/{total_pages}{ANSI.RESET}\r\n\r\n"
        
        for cat_id, cat_data in current_page:
            message += f"{ANSI.BOLD}{cat_data['icon']} {cat_data['name']}{ANSI.RESET}\r\n"
            for cmd, desc in cat_data['commands']:
                message += f"  {ANSI.BRIGHT_GREEN}{cmd:<28}{ANSI.RESET} - {desc}\r\n"
            message += "\r\n"
        
        # Navegação
        if total_pages > 1:
            message += f"{ANSI.BRIGHT_CYAN}Navegação:{ANSI.RESET}\r\n"
            if page_num > 1:
                message += f"  {ANSI.BRIGHT_GREEN}help {page_num - 1}{ANSI.RESET} - Página anterior\r\n"
            if page_num < total_pages:
                message += f"  {ANSI.BRIGHT_GREEN}help {page_num + 1}{ANSI.RESET} - Próxima página\r\n"
            message += f"  {ANSI.BRIGHT_GREEN}help <categoria>{ANSI.RESET} - Ver categoria específica\r\n"
        
        message += f"\r\n{ANSI.BRIGHT_YELLOW}Dica: Use 'help <categoria>' para ver apenas uma categoria específica{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_YELLOW}Exemplo: help movimento, help combate, help magias{ANSI.RESET}\r\n"
        
        await self.send_message(player, message)
    
    def _is_lobby(self, player: Player) -> bool:
        """Verifica se o jogador está no lobby"""
        return player.room_id == "lobby"
    
    async def cmd_afk(self, player: Player, message: str = ""):
        """Comando afk - marca como AFK (disponível em qualquer lugar)"""
        afk_message = message.strip() if message else "Ausente"
        player.afk_message = afk_message
        player.is_afk = True
        
        # Inicializa timestamp do Pomodoro quando marca como AFK
        import time
        if not hasattr(player, '_last_pomodoro_time'):
            player._last_pomodoro_time = time.time()
        
        await self.send_message(player, 
            f"{ANSI.BRIGHT_YELLOW}Você está marcado como AFK: {afk_message}{ANSI.RESET}\r\n"
            f"{ANSI.BRIGHT_CYAN}Use 'voltar' ou 'back' para voltar.{ANSI.RESET}\r\n"
            f"{ANSI.BRIGHT_GREEN}🍅 Você ganhará experiência a cada 5 minutos enquanto estiver AFK!{ANSI.RESET}\r\n")
        
        await self.game.broadcast_to_room(
            player.world_id,
            player.room_id,
            f"{player.name} está AFK: {afk_message}",
            exclude_player=player.name
        )
    
    async def cmd_voltar(self, player: Player):
        """Comando voltar/back - volta do AFK (disponível em qualquer lugar)"""
        if hasattr(player, 'is_afk') and player.is_afk:
            player.is_afk = False
            player.afk_message = ""
            await self.send_message(player, 
                f"{ANSI.BRIGHT_GREEN}Você voltou! Bem-vindo de volta!{ANSI.RESET}")
            await self.game.broadcast_to_room(
                player.world_id,
                player.room_id,
                f"{player.name} voltou.",
                exclude_player=player.name
            )
        else:
            await self.send_message(player, 
                f"{ANSI.YELLOW}Você não está marcado como AFK.{ANSI.RESET}")
    
    async def cmd_lobby(self, player: Player):
        """Comando lobby - teletransporta para o Hall de Entrada"""
        if player.room_id == "lobby":
            await self.send_message(player, 
                f"{ANSI.YELLOW}Você já está no Hall de Entrada!{ANSI.RESET}")
            return
        
        # Verifica se o jogador está em combate
        if player.name in self.in_combat:
            await self.send_message(player, f"{ANSI.RED}Você está em combate! Não pode sair da sala até o combate acabar.{ANSI.RESET}")
            return
        
        old_room_id = player.room_id
        
        # Teletransporta para o lobby
        player.room_id = "lobby"
        
        # Restaura HP se estiver morto
        if not player.is_alive():
            player.current_hp = player.max_hp
            await self.send_message(player, 
                f"{ANSI.BRIGHT_GREEN}Você foi curado ao retornar ao Hall de Entrada!{ANSI.RESET}")
        
        # Salva no banco
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        
        # Notifica outras salas
        await self.game.broadcast_to_room(
            player.world_id,
            old_room_id,
            f"{player.name} teletransportou-se para o Hall de Entrada.",
            exclude_player=player.name
        )
        
        await self.game.broadcast_to_room(
            player.world_id,
            "lobby",
            f"{player.name} chegou ao Hall de Entrada.",
            exclude_player=player.name
        )
        
        # Mostra a sala do lobby
        await self.send_message(player, 
            f"{ANSI.BRIGHT_CYAN}Você foi teletransportado para o Hall de Entrada!{ANSI.RESET}")
        await self.cmd_look(player)
    
    async def cmd_respawn(self, player: Player):
        """Comando respawn - regenera HP/stamina/mana (exclusivo do lobby)"""
        if not self._is_lobby(player):
            await self.send_message(player, 
                f"{ANSI.YELLOW}Este comando só está disponível no Hall de Entrada (lobby).{ANSI.RESET}\r\n"
                f"{ANSI.BRIGHT_CYAN}Use 'lobby' para voltar ao Hall de Entrada.{ANSI.RESET}")
            return
        
        # Regenera tudo
        old_hp = player.current_hp
        old_stamina = player.current_stamina
        
        player.current_hp = player.max_hp
        player.current_stamina = player.max_stamina
        
        hp_restored = player.max_hp - old_hp
        stamina_restored = player.max_stamina - old_stamina
        
        message = f"{ANSI.BRIGHT_GREEN}Você foi completamente curado!{ANSI.RESET}\r\n"
        if hp_restored > 0:
            message += f"{ANSI.GREEN}HP restaurado: +{hp_restored}{ANSI.RESET}\r\n"
        if stamina_restored > 0:
            message += f"{ANSI.BLUE}Stamina restaurada: +{stamina_restored}{ANSI.RESET}\r\n"
        
        await self.send_message(player, message)
        
        # Salva no banco
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'current_stamina': player.current_stamina,
            'max_stamina': player.max_stamina
        }
        self.database.update_player_stats(player.name, stats)
    
    async def cmd_server_status(self, player: Player):
        """Comando server - mostra status do servidor (exclusivo do lobby)"""
        if not self._is_lobby(player):
            await self.send_message(player, 
                f"{ANSI.YELLOW}Este comando só está disponível no Hall de Entrada (lobby).{ANSI.RESET}\r\n"
                f"{ANSI.BRIGHT_CYAN}Use 'lobby' para voltar ao Hall de Entrada.{ANSI.RESET}")
            return
        
        # Conta jogadores online
        total_players = len(self.game.players)
        players_in_lobby = len([p for p in self.game.players.values() if p.room_id == "lobby"])
        
        # Calcula estatísticas gerais
        total_level = sum(p.level for p in self.game.players.values())
        avg_level = total_level / total_players if total_players > 0 else 0
        
        message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Status do Servidor ==={ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_GREEN}Jogadores Online: {total_players}{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_CYAN}Jogadores no Lobby: {players_in_lobby}{ANSI.RESET}\r\n"
        message += f"{ANSI.BRIGHT_YELLOW}Nível Médio: {avg_level:.1f}{ANSI.RESET}\r\n"
        
        # Lista jogadores online com status
        if total_players > 0:
            message += f"\r\n{ANSI.BOLD}Jogadores Online:{ANSI.RESET}\r\n"
            for p in sorted(self.game.players.values(), key=lambda x: x.level, reverse=True):
                afk_status = ""
                if hasattr(p, 'is_afk') and p.is_afk:
                    afk_msg = getattr(p, 'afk_message', 'AFK')
                    afk_status = f" {ANSI.BRIGHT_BLACK}[AFK: {afk_msg}]{ANSI.RESET}"
                
                location = "Lobby" if p.room_id == "lobby" else p.room_id
                message += f"  {ANSI.BRIGHT_GREEN}{p.name}{ANSI.RESET} - Nível {p.level} - {location}{afk_status}\r\n"
        
        message += f"\r\n{ANSI.BRIGHT_CYAN}Comandos do Lobby:{ANSI.RESET}\r\n"
        message += f"  {ANSI.BRIGHT_GREEN}afk [mensagem]{ANSI.RESET} - Marca como AFK\r\n"
        message += f"  {ANSI.BRIGHT_GREEN}voltar / back{ANSI.RESET} - Volta do AFK\r\n"
        message += f"  {ANSI.BRIGHT_GREEN}lobby{ANSI.RESET} - Volta ao Hall de Entrada\r\n"
        message += f"  {ANSI.BRIGHT_GREEN}respawn{ANSI.RESET} - Regenera HP e Stamina\r\n"
        message += f"  {ANSI.BRIGHT_GREEN}server / status_server{ANSI.RESET} - Mostra este status\r\n"
        
        await self.send_message(player, message)
    
    async def cmd_quit(self, player: Player):
        """Comando quit - sai do jogo"""
        await self.send_message(player, f"{ANSI.BRIGHT_GREEN}Até logo!{ANSI.RESET}")
        await self.game.broadcast_to_room(
            player.world_id,
            player.room_id,
            f"{player.name} deixou o jogo.",
            exclude_player=player.name
        )
        # Salva estado final (incluindo progresso de quests)
        self.database.update_player_location(player.name, player.world_id, player.room_id)
        stats = {
            'hp': player.current_hp,
            'max_hp': player.max_hp,
            'level': player.level,
            'experience': player.experience,
            'attack': player.attack,
            'defense': player.defense,
            'gold': player.gold,
            'inventory': player.inventory,
            'equipment': player.equipment,
            'active_quests': player.active_quests,
            'quest_progress': player.quest_progress,
            'completed_quests': player.completed_quests
        }
        self.database.update_player_stats(player.name, stats)
        self.game.remove_player(player.name)
        if player.name in self.in_combat:
            del self.in_combat[player.name]
        player.writer.close()
        await player.writer.wait_closed()
    
    async def _update_kill_quests(self, player: Player, monster_name: str):
        """Atualiza progresso de quests de kill"""
        for quest_id in player.active_quests:
            quest = self.quest_manager.get_quest(player.world_id, quest_id)
            if quest:
                for objective in quest.objectives:
                    if objective.get('type') == 'kill':
                        target = objective.get('target', '').lower()
                        if target in monster_name.lower():
                            progress_key = f"kill_{objective.get('target')}"
                            if quest_id not in player.quest_progress:
                                player.quest_progress[quest_id] = {}
                            player.quest_progress[quest_id][progress_key] = \
                                player.quest_progress[quest_id].get(progress_key, 0) + 1
                            
                            # Verifica se completou
                            # Salva progresso no banco
                            stats = {
                                'hp': player.current_hp,
                                'max_hp': player.max_hp,
                                'level': player.level,
                                'experience': player.experience,
                                'attack': player.attack,
                                'defense': player.defense,
                                'gold': player.gold,
                                'inventory': player.inventory,
                                'equipment': player.equipment,
                                'active_quests': player.active_quests,
                                'quest_progress': player.quest_progress,
                                'completed_quests': player.completed_quests
                            }
                            self.database.update_player_stats(player.name, stats)
                            
                            if self.quest_manager.check_quest_completion(quest, player.quest_progress[quest_id]):
                                await self.send_message(player, 
                                    f"{ANSI.BRIGHT_GREEN}Quest '{quest.name}' pode ser completada!{ANSI.RESET}")
    
    async def send_message(self, player: Player, message: str):
        """Envia mensagem para um jogador"""
        try:
            # Remove qualquer quebra de linha no final
            message = message.rstrip('\r\n')
            
            # Limpa a linha atual antes de enviar a mensagem
            # Isso evita que mensagens apareçam no meio da linha quando o jogador está digitando
            # Sequência ANSI: \r volta ao início da linha, \033[K limpa até o final da linha
            clear_line = "\r\033[K"
            player.writer.write(f"{clear_line}{message}\r\n".encode())
            await player.writer.drain()
        except:
            pass
