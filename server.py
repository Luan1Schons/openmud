#!/usr/bin/env python3
"""
Servidor MUD - Multi-User Dungeon
Jogo multiplayer para terminal Linux
Compatível com TinTin++ e outros clientes MUD
"""

import asyncio
from typing import Dict, Set, Optional
from datetime import datetime

from mud.core.models import Player
from mud.managers.world_manager import WorldManager
from mud.core.database import Database
from mud.commands.commands import CommandHandler
from mud.auth.auth import authenticate
from mud.systems.character_creation import create_character
from mud.systems.classes import ClassSystem
from mud.utils.compatibility_test import run_compatibility_test
from mud.managers.world_lore_manager import WorldLoreManager
from mud.managers.dungeon_manager import DungeonManager
from mud.utils.ansi import ANSI

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 4000

class MUDGame:
    """Gerenciador principal do jogo MUD"""
    
    def __init__(self, world_manager: WorldManager, database: Database):
        self.players: Dict[str, Player] = {}
        self.world_manager = world_manager
        self.database = database
        self.player_connections: Set[asyncio.StreamWriter] = set()
    
    def get_players_in_room(self, world_id: str, room_id: str) -> list:
        """Retorna lista de jogadores em uma sala"""
        return [p for p in self.players.values() if p.world_id == world_id and p.room_id == room_id]
    
    def add_player(self, name: str, world_id: str, room_id: str, writer: asyncio.StreamWriter, 
                  reader: asyncio.StreamReader, class_id: str = "", race_id: str = "", 
                  gender_id: str = "", stats: Dict = None) -> Player:
        """Adiciona um novo jogador ao jogo"""
        if stats is None:
            stats = {}
        
        from mud.systems.spells import SpellSystem
        spell_system = SpellSystem()
        
        # Inicializa magias iniciais se não tiver
        known_spells = stats.get('known_spells', {})
        if not known_spells and class_id:
            starting_spells = spell_system.get_starting_spells(class_id)
            for spell_id in starting_spells:
                known_spells[spell_id] = 1
        
        player = Player(
            name=name,
            world_id=world_id,
            room_id=room_id,
            writer=writer,
            reader=reader,
            class_id=class_id,
            race_id=race_id,
            gender_id=gender_id,
            max_hp=stats.get('max_hp', 100),
            current_hp=stats.get('current_hp', stats.get('max_hp', 100)),
            max_stamina=stats.get('max_stamina', 100),
            current_stamina=stats.get('current_stamina', stats.get('max_stamina', 100)),
            level=stats.get('level', 1),
            experience=stats.get('experience', 0),
            attack=stats.get('attack', 10),
            defense=stats.get('defense', 5),
            gold=stats.get('gold', 0),
            inventory=stats.get('inventory', []),
            equipment=stats.get('equipment', {}),
            active_quests=stats.get('active_quests', []),
            quest_progress=stats.get('quest_progress', {}),
            completed_quests=stats.get('completed_quests', []),
            known_spells=known_spells,
            equipped_spells=stats.get('equipped_spells', []),
            active_perks=stats.get('active_perks', []),
            spell_cooldowns=stats.get('spell_cooldowns', {}),
            unspent_points=stats.get('unspent_points', 0)
        )
        self.players[name] = player
        self.player_connections.add(writer)
        return player
    
    def remove_player(self, name: str):
        """Remove um jogador do jogo"""
        if name in self.players:
            player = self.players[name]
            self.player_connections.discard(player.writer)
            del self.players[name]
    
    async def broadcast_to_room(self, world_id: str, room_id: str, message: str, exclude_player: Optional[str] = None):
        """Envia mensagem para todos os jogadores na sala"""
        players = self.get_players_in_room(world_id, room_id)
        for player in players:
            if exclude_player and player.name == exclude_player:
                continue
            try:
                player.writer.write(f"{message}\n".encode())
                await player.writer.drain()
            except:
                pass
    
    async def broadcast_global(self, message: str, exclude_player: Optional[str] = None):
        """Envia mensagem para todos os jogadores online (chat global)"""
        for player in self.players.values():
            if exclude_player and player.name == exclude_player:
                continue
            try:
                player.writer.write(f"{message}\n".encode())
                await player.writer.drain()
            except:
                pass

async def select_world(writer: asyncio.StreamWriter, reader: asyncio.StreamReader, world_manager: WorldManager) -> Optional[str]:
    """Permite ao jogador escolher um mundo"""
    worlds = world_manager.list_worlds()
    
    if not worlds:
        writer.write(f"{ANSI.RED}Erro: Nenhum mundo disponível.{ANSI.RESET}\n".encode())
        await writer.drain()
        return None
    
    # Mostra mundos disponíveis
    message = f"\r\n{ANSI.BOLD}{ANSI.CYAN}=== Escolha um Mundo ==={ANSI.RESET}\r\n\r\n"
    for i, world in enumerate(worlds, 1):
        message += f"{ANSI.BRIGHT_GREEN}{i}.{ANSI.RESET} {ANSI.BRIGHT_CYAN}{world['name']}{ANSI.RESET} ({world['id']})\r\n"
        message += f"   {world['description']}\r\n\r\n"
    
    message += f"{ANSI.BRIGHT_YELLOW}Digite o número ou ID do mundo:{ANSI.RESET} "
    writer.write(message.encode())
    await writer.drain()
    
    # Aguarda escolha
    try:
        choice_data = await asyncio.wait_for(reader.readline(), timeout=30.0)
        if not choice_data:
            return None
        
        choice = choice_data.decode().strip()
        
        # Tenta por número
        try:
            num = int(choice)
            if 1 <= num <= len(worlds):
                return worlds[num - 1]['id']
        except ValueError:
            pass
        
        # Tenta por ID
        for world in worlds:
            if world['id'].lower() == choice.lower():
                return world['id']
        
        # Se não encontrou, usa o padrão
        writer.write(f"{ANSI.YELLOW}Escolha inválida. Usando mundo padrão.{ANSI.RESET}\n".encode())
        await writer.drain()
        return worlds[0]['id'] if worlds else None
    
    except asyncio.TimeoutError:
        writer.write(f"{ANSI.RED}Tempo esgotado. Usando mundo padrão.{ANSI.RESET}\n".encode())
        await writer.drain()
        return worlds[0]['id'] if worlds else None

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, game: MUDGame, world_manager: WorldManager, database: Database, game_data, lore_manager, quest_manager, class_system: ClassSystem, world_lore_manager: WorldLoreManager, dungeon_manager: DungeonManager):
    """Gerencia conexão de um cliente"""
    addr = writer.get_extra_info('peername')
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Nova conexão de {addr}")
    
    try:
        # Autenticação (login/registro)
        auth_success, username = await authenticate(writer, reader, database)
        if not auth_success:
            writer.write(f"{ANSI.RED}Falha na autenticação. Desconectando...{ANSI.RESET}\r\n".encode())
            await writer.drain()
            writer.close()
            return
        
        player_name = username
        
        # Teste de compatibilidade visual (apenas uma vez)
        if not database.has_done_compatibility_test(username):
            test_completed = await run_compatibility_test(writer, reader, database, username)
            if not test_completed:
                writer.write(f"{ANSI.YELLOW}Teste não concluído. Você poderá continuar mesmo assim.{ANSI.RESET}\r\n".encode())
                await writer.drain()
                # Aguarda um pouco antes de continuar
                await asyncio.sleep(1)
        
        # Verifica se jogador existe no banco
        player_data = database.get_player(player_name)
        
        if player_data:
            # Jogador existente - verifica se tem classe/raça/gênero
            class_id = player_data.get('class_id', '')
            race_id = player_data.get('race_id', '')
            gender_id = player_data.get('gender_id', '')
            
            # Se não tem classe/raça/gênero, força criação
            if not class_id or not race_id or not gender_id:
                writer.write(f"{ANSI.YELLOW}Você precisa completar a criação do seu personagem.{ANSI.RESET}\r\n".encode())
                await writer.drain()
                
                class_id, race_id, gender_id = await create_character(writer, reader, class_system)
                if not class_id or not race_id or not gender_id:
                    writer.write(f"{ANSI.RED}Criação de personagem cancelada. Desconectando...{ANSI.RESET}\r\n".encode())
                    await writer.drain()
                    writer.close()
                    return
                
                # Atualiza no banco
                database.update_player_class_race_gender(player_name, class_id, race_id, gender_id)
            
            world_id = player_data['world_id']
            room_id = player_data['room_id']
            
            # Verifica se mundo ainda existe
            if not world_manager.get_world(world_id):
                writer.write(f"{ANSI.YELLOW}Seu mundo anterior não existe mais. Escolha um novo:{ANSI.RESET}\n".encode())
                await writer.drain()
                world_id = await select_world(writer, reader, world_manager)
                if not world_id:
                    writer.close()
                    return
                world = world_manager.get_world(world_id)
                room_id = world.start_room if world else None
                if not room_id:
                    writer.close()
                    return
            
            # Verifica se sala ainda existe
            if not world_manager.get_room(world_id, room_id):
                world = world_manager.get_world(world_id)
                room_id = world.start_room if world else None
                if not room_id:
                    writer.close()
                    return
            
            welcome_back = f"{ANSI.BRIGHT_GREEN}Bem-vindo de volta, {player_name}!{ANSI.RESET}\r\n"
            writer.write(welcome_back.encode())
            await writer.drain()
        else:
            # Novo jogador - escolhe mundo primeiro
            world_id = await select_world(writer, reader, world_manager)
            if not world_id:
                writer.close()
                return
            
            world = world_manager.get_world(world_id)
            room_id = world.start_room if world else None
            if not room_id:
                writer.close()
                return
            
            # Criação de personagem (classe, raça, gênero)
            class_id, race_id, gender_id = await create_character(writer, reader, class_system)
            if not class_id or not race_id or not gender_id:
                writer.write(f"{ANSI.RED}Criação de personagem cancelada. Desconectando...{ANSI.RESET}\r\n".encode())
                await writer.drain()
                writer.close()
                return
            
            # Cria jogador no banco com classe/raça/gênero
            database.create_player(player_name, world_id, room_id, class_id, race_id, gender_id)
        
        # Carrega dados do jogador do banco
        player_data = database.get_player(player_name)
        class_id = player_data.get('class_id', '') if player_data else ''
        race_id = player_data.get('race_id', '') if player_data else ''
        gender_id = player_data.get('gender_id', '') if player_data else ''
        
        # Aplica estatísticas da classe e raça
        stats = {}
        player_stats = {}
        if player_data:
            player_stats = player_data.get('stats', {})
        
        if class_id and race_id:
            cls = class_system.get_class(class_id)
            if cls:
                stats = class_system.apply_race_bonuses(cls.base_stats, race_id)
                # Adiciona itens iniciais
                if player_data:
                    if not player_stats.get('inventory'):
                        # Primeiro login, adiciona itens iniciais
                        stats['inventory'] = cls.starting_items.copy()
                        stats['gold'] = cls.starting_gold
                    else:
                        stats['inventory'] = player_stats.get('inventory', [])
                        stats['gold'] = player_stats.get('gold', 0)
        else:
            # Se não tem classe/raça ainda, carrega stats básicos do banco
            if player_data:
                stats['hp'] = player_stats.get('hp', 100)
                stats['max_hp'] = player_stats.get('max_hp', 100)
                stats['current_hp'] = player_stats.get('hp', player_stats.get('current_hp', 100))
                stats['level'] = player_stats.get('level', 1)
                stats['experience'] = player_stats.get('experience', 0)
                stats['attack'] = player_stats.get('attack', 10)
                stats['defense'] = player_stats.get('defense', 5)
                stats['inventory'] = player_stats.get('inventory', [])
                stats['gold'] = player_stats.get('gold', 0)
                stats['equipment'] = player_stats.get('equipment', {})
        
        # Preserva quests e progresso do banco (sempre)
        if player_data:
            stats['active_quests'] = player_stats.get('active_quests', [])
            stats['quest_progress'] = player_stats.get('quest_progress', {})
            stats['completed_quests'] = player_stats.get('completed_quests', [])
            
            # Preserva magias e perks
            stats['known_spells'] = player_stats.get('known_spells', {})
            stats['equipped_spells'] = player_stats.get('equipped_spells', [])
            stats['active_perks'] = player_stats.get('active_perks', [])
            stats['spell_cooldowns'] = player_stats.get('spell_cooldowns', {})
            stats['unspent_points'] = player_stats.get('unspent_points', 0)
            
            # Preserva stamina
            stats['current_stamina'] = player_stats.get('current_stamina', player_stats.get('max_stamina', 100))
            stats['max_stamina'] = player_stats.get('max_stamina', 100)
            
            # Preserva outros stats importantes
            if player_stats.get('hp') and 'current_hp' not in stats:
                stats['current_hp'] = player_stats.get('hp')
            if player_stats.get('max_hp') and 'max_hp' not in stats:
                stats['max_hp'] = player_stats.get('max_hp')
            if player_stats.get('level') and 'level' not in stats:
                stats['level'] = player_stats.get('level')
            if player_stats.get('experience') and 'experience' not in stats:
                stats['experience'] = player_stats.get('experience')
            if player_stats.get('attack') and 'attack' not in stats:
                stats['attack'] = player_stats.get('attack')
            if player_stats.get('defense') and 'defense' not in stats:
                stats['defense'] = player_stats.get('defense')
            if player_stats.get('equipment') and 'equipment' not in stats:
                stats['equipment'] = player_stats.get('equipment', {})
            if player_stats.get('has_seen_lore'):
                stats['has_seen_lore'] = player_stats.get('has_seen_lore', False)
        
        # Adiciona jogador ao jogo
        player = game.add_player(player_name, world_id, room_id, writer, reader, 
                                 class_id=class_id, race_id=race_id, gender_id=gender_id,
                                 stats=stats)
        
        # Notifica entrada do jogador
        await game.broadcast_to_room(
            player.world_id,
            player.room_id,
            f"{player_name} entrou no jogo.",
            exclude_player=player_name
        )
        
        # Cria handler de comandos
        handler = CommandHandler(game, world_manager, database, game_data, lore_manager, quest_manager, world_lore_manager, dungeon_manager)
        
        # Verifica se é novo jogador (primeira vez conectando) - APENAS se nunca viu a lore
        player_stats = player_data.get('stats', {}) if player_data else {}
        has_seen_lore = player_stats.get('has_seen_lore', False)
        is_new_player = not has_seen_lore
        
        # Mostra lore APENAS se for a primeira vez
        if is_new_player:
            lore_text = world_lore_manager.format_world_lore(player.world_id)
            if lore_text:
                await handler.send_message(player, lore_text)
                await handler.send_message(player, f"\r\n{ANSI.BRIGHT_YELLOW}Deseja ler esta introdução novamente? Use o comando 'lore' ou 'world'.{ANSI.RESET}\r\n")
                await handler.send_message(player, f"{ANSI.BRIGHT_GREEN}Pressione Enter para continuar...{ANSI.RESET}\r\n")
                
                # Aguarda Enter para continuar
                try:
                    await asyncio.wait_for(player.reader.readline(), timeout=60.0)
                except asyncio.TimeoutError:
                    pass
                
                # Marca como tendo visto a lore
                # Atualiza também no objeto player
                if player:
                    player.stats['has_seen_lore'] = True
                
                # Salva no banco de dados
                current_player_data = database.get_player(player_name)
                if current_player_data:
                    current_stats = current_player_data.get('stats', {}).copy()
                    current_stats['has_seen_lore'] = True
                    database.update_player_stats(player_name, current_stats)
                else:
                    # Se não existe ainda, cria stats básicos
                    new_stats = {'has_seen_lore': True}
                    database.update_player_stats(player_name, new_stats)
        
        # Mensagem de boas-vindas ao servidor
        # Conta players online (incluindo o que acabou de conectar)
        online_count = len(game.players)
        developers = ["Luan Schons Griebler"]
        
        # Calcula espaçamento para centralizar melhor
        title = "Bem-vindo ao OpenMud Dungeon Server!"
        greeting = f"Olá, {player_name}!"
        online_text = f"Jogadores Online: {online_count}"
        dev_text = ", ".join(developers)
        dev_line = f"Desenvolvido por: {dev_text}"
        
        max_width = 58
        title_pad = (max_width - len(title)) // 2
        greeting_pad = (max_width - len(greeting)) // 2
        online_pad = (max_width - len(online_text)) // 2
        dev_pad = (max_width - len(dev_line)) // 2
        
        welcome_banner = f"\r\n{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{'═' * 60}{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * 58}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * title_pad}{ANSI.BRIGHT_CYAN}{title}{ANSI.RESET}{' ' * (max_width - len(title) - title_pad)}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * 58}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * greeting_pad}{ANSI.BRIGHT_YELLOW}{greeting}{ANSI.RESET}{' ' * (max_width - len(greeting) - greeting_pad)}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * 58}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * online_pad}{ANSI.BRIGHT_WHITE}Jogadores Online: {ANSI.BRIGHT_GREEN}{online_count}{ANSI.RESET}{' ' * (max_width - len(online_text) - online_pad)}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * 58}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * dev_pad}{ANSI.BRIGHT_MAGENTA}{dev_line}{ANSI.RESET}{' ' * (max_width - len(dev_line) - dev_pad)}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}{' ' * 58}{ANSI.BOLD}{ANSI.BRIGHT_GREEN}║{ANSI.RESET}\r\n"
        welcome_banner += f"{ANSI.BOLD}{ANSI.BRIGHT_CYAN}{'═' * 60}{ANSI.RESET}\r\n\r\n"
        
        await handler.send_message(player, welcome_banner)
        await handler.cmd_look(player)
        help_hint = f"{ANSI.BRIGHT_YELLOW}Digite 'help' para ver os comandos disponíveis.{ANSI.RESET}\r\n"
        await handler.send_message(player, help_hint)
        
        # Loop principal de comandos
        while True:
            prompt = f"{ANSI.BRIGHT_GREEN}>{ANSI.RESET} "
            writer.write(prompt.encode())
            await writer.drain()
            
            data = await asyncio.wait_for(reader.readline(), timeout=300.0)
            if not data:
                break
            
            command = data.decode().strip()
            if command:
                await handler.handle_command(player, command)
    
    except asyncio.TimeoutError:
        writer.write(f"\n{ANSI.YELLOW}Tempo de inatividade excedido. Desconectando...{ANSI.RESET}\n".encode())
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro com {addr}: {e}")
    finally:
        player_name = locals().get('player_name', None) or addr
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {player_name} desconectou")
        if 'player' in locals() and player.name in game.players:
            await game.broadcast_to_room(
                player.world_id,
                player.room_id,
                f"{player.name} desconectou.",
                exclude_player=player.name
            )
            # Salva estado final
            database.update_player_location(player.name, player.world_id, player.room_id)
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
            database.update_player_stats(player.name, stats)
            game.remove_player(player.name)
        writer.close()
        await writer.wait_closed()

async def main():
    """Função principal do servidor"""
    print("=" * 50)
    print("Servidor MUD - Multi-User Dungeon")
    print("=" * 50)
    
    # Inicializa componentes
    print("Inicializando banco de dados...")
    database = Database()
    
    print("Carregando mundos...")
    world_manager = WorldManager()
    
    if not world_manager.worlds:
        print("ERRO: Nenhum mundo carregado!")
        return
    
    print(f"Mundos disponíveis: {len(world_manager.worlds)}")
    for world_id, world in world_manager.worlds.items():
        print(f"  - {world.name} ({world_id})")
    
    print("Carregando dados do jogo...")
    from mud.managers.game_data import GameDataManager
    from mud.managers.lore_manager import LoreManager
    from mud.managers.quest_manager import QuestManager
    game_data = GameDataManager()
    lore_manager = LoreManager()
    quest_manager = QuestManager(database=database)  # Passa database para persistência
    world_lore_manager = WorldLoreManager()
    dungeon_manager = DungeonManager()
    
    print("Inicializando sistema de classes...")
    class_system = ClassSystem()
    print(f"Classes disponíveis: {len(class_system.classes)}")
    print(f"Raças disponíveis: {len(class_system.races)}")
    
    game = MUDGame(world_manager, database)
    
    async def stamina_regeneration_task():
        """Task que regenera stamina de todos os players a cada 3 segundos"""
        import time
        while True:
            await asyncio.sleep(3.0)  # Espera 3 segundos
            current_time = time.time()
            
            for player_name, player in list(game.players.items()):
                # Inicializa timestamp se não existir
                if not hasattr(player, '_last_stamina_regen'):
                    player._last_stamina_regen = current_time
                
                # Calcula tempo passado
                time_passed = current_time - player._last_stamina_regen
                
                # Regenera 1 ponto a cada 3 segundos
                if time_passed >= 3.0:
                    regen_amount = int(time_passed / 3.0)
                    if regen_amount > 0:
                        old_stamina = player.current_stamina
                        player.restore_stamina(regen_amount)
                        # Atualiza timestamp
                        player._last_stamina_regen = current_time - (time_passed % 3.0)
                        
                        # Nota: Stamina será salva quando o player se desconectar ou fizer ações importantes
                        # Não precisamos salvar a cada regeneração para evitar sobrecarga no banco
    
    # Inicia task de regeneração de stamina
    asyncio.create_task(stamina_regeneration_task())
    
    print(f"\nServidor iniciado em {HOST}:{PORT}")
    print(f"Aguardando conexões...")
    print(f"Sistema de regeneração de stamina ativo (1 ponto a cada 3 segundos)")
    print("Pressione Ctrl+C para encerrar")
    print("=" * 50)
    
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, game, world_manager, database, game_data, lore_manager, quest_manager, class_system, world_lore_manager, dungeon_manager),
        HOST,
        PORT
    )
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServidor encerrado.")
