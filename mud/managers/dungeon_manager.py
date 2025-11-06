"""
Gerenciador de Dungeons e Portas
"""

import json
import random
from pathlib import Path
from typing import Dict, Optional, List
from mud.core.models import Room

class DungeonManager:
    """Gerencia dungeons e portas do jogo"""
    
    def __init__(self, worlds_dir: str = "worlds"):
        self.worlds_dir = Path(worlds_dir)
        self.dungeons: Dict[str, Dict] = {}  # world_id -> {dungeon_id -> dungeon_data}
        self.dungeon_rooms: Dict[str, Dict[str, Room]] = {}  # world_id -> {room_id -> Room}
        self._load_dungeons()
    
    def _load_dungeons(self):
        """Carrega todas as dungeons"""
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir() and world_dir.name == "default":
                world_id = world_dir.name
                dungeons_file = world_dir / "dungeons.json"
                
                if dungeons_file.exists():
                    try:
                        with open(dungeons_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.dungeons[world_id] = {}
                            self.dungeon_rooms[world_id] = {}
                            
                            for dungeon_data in data.get('dungeons', []):
                                dungeon_id = dungeon_data['id']
                                self.dungeons[world_id][dungeon_id] = dungeon_data
                                
                                # Carrega salas da dungeon
                                for room_data in dungeon_data.get('rooms', []):
                                    room = Room(
                                        id=room_data['id'],
                                        name=room_data['name'],
                                        description=room_data['description'],
                                        exits=room_data.get('exits', {})
                                    )
                                    self.dungeon_rooms[world_id][room.id] = room
                            
                            print(f"[DungeonManager] {len(self.dungeons.get(world_id, {}))} dungeon(s) carregada(s) para {world_id}")
                    except Exception as e:
                        print(f"[DungeonManager] Erro ao carregar dungeons de {world_id}: {e}")
    
    def get_dungeon_room(self, world_id: str, room_id: str) -> Optional[Room]:
        """Retorna uma sala de dungeon (Room object)"""
        return self.dungeon_rooms.get(world_id, {}).get(room_id)
    
    def get_room_data(self, world_id: str, room_id: str) -> Optional[Dict]:
        """Retorna dados completos de uma sala de dungeon (incluindo configurações)"""
        if world_id not in self.dungeons:
            return None
        
        for dungeon in self.dungeons[world_id].values():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    return room_data
        return None
    
    def get_dungeon_by_entry_room(self, world_id: str, entry_room_id: str) -> Optional[Dict]:
        """Retorna dungeon que tem entrada em uma sala específica"""
        if world_id not in self.dungeons:
            return None
        
        for dungeon in self.dungeons[world_id].values():
            if dungeon.get('entry_room') == entry_room_id:
                return dungeon
        return None
    
    def get_dungeon_entry_room(self, world_id: str, dungeon_id: str) -> Optional[str]:
        """Retorna a sala de entrada da dungeon"""
        dungeon = self.dungeons.get(world_id, {}).get(dungeon_id)
        if dungeon:
            rooms = dungeon.get('rooms', [])
            if rooms:
                # Primeira sala é sempre a entrada
                return rooms[0]['id']
        return None
    
    def is_dungeon_room(self, world_id: str, room_id: str) -> bool:
        """Verifica se uma sala é parte de uma dungeon"""
        return room_id in self.dungeon_rooms.get(world_id, {})
    
    def get_dungeon_for_room(self, world_id: str, room_id: str) -> Optional[str]:
        """Retorna o ID da dungeon de uma sala"""
        if world_id not in self.dungeons:
            return None
        
        for dungeon_id, dungeon in self.dungeons[world_id].items():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    return dungeon_id
        return None
    
    def get_room_monsters(self, world_id: str, room_id: str) -> List[str]:
        """Retorna lista de IDs de monstros que podem spawnar em uma sala de dungeon"""
        if world_id not in self.dungeons:
            return []
        
        for dungeon in self.dungeons[world_id].values():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    return room_data.get('monsters', [])
        return []
    
    def get_room_items(self, world_id: str, room_id: str) -> List[str]:
        """Retorna lista de IDs de itens que podem spawnar em uma sala de dungeon"""
        if world_id not in self.dungeons:
            return []
        
        for dungeon in self.dungeons[world_id].values():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    return room_data.get('items', [])
        return []
    
    def get_room_spawn_chance(self, world_id: str, room_id: str) -> float:
        """Retorna a chance de spawn de monstros em uma sala"""
        if world_id not in self.dungeons:
            return 0.0
        
        for dungeon in self.dungeons[world_id].values():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    return room_data.get('spawn_chance', 0.5)
        return 0.0
    
    def should_spawn_monsters(self, world_id: str, room_id: str) -> bool:
        """Verifica se deve spawnar monstros na sala"""
        chance = self.get_room_spawn_chance(world_id, room_id)
        return random.random() < chance
    
    def get_dungeon_info(self, world_id: str, dungeon_id: str) -> Optional[Dict]:
        """Retorna informações da dungeon"""
        return self.dungeons.get(world_id, {}).get(dungeon_id)
    
    def get_room_respawn_time(self, world_id: str, room_id: str, monster_id: str = None) -> Dict[str, int]:
        """
        Retorna o tempo de respawn configurado para uma sala.
        Se monster_id for fornecido, retorna o tempo específico para aquele monstro.
        Retorna um dicionário com 'min' e 'max' em segundos, ou None se não configurado.
        """
        if world_id not in self.dungeons:
            return {'min': 300, 'max': 600}  # Default: 5-10 minutos
        
        for dungeon in self.dungeons[world_id].values():
            for room_data in dungeon.get('rooms', []):
                if room_data['id'] == room_id:
                    # Verifica se há configuração específica por monstro
                    if monster_id:
                        monster_respawns = room_data.get('monster_respawns', {})
                        if monster_id in monster_respawns:
                            respawn_config = monster_respawns[monster_id]
                            if isinstance(respawn_config, dict):
                                return {
                                    'min': respawn_config.get('min', 300),
                                    'max': respawn_config.get('max', 600)
                                }
                            elif isinstance(respawn_config, int):
                                # Se for apenas um número, usa como tempo fixo
                                return {'min': respawn_config, 'max': respawn_config}
                    
                    # Configuração geral da sala
                    respawn_config = room_data.get('respawn_time', {})
                    if isinstance(respawn_config, dict):
                        return {
                            'min': respawn_config.get('min', 300),
                            'max': respawn_config.get('max', 600)
                        }
                    elif isinstance(respawn_config, int):
                        return {'min': respawn_config, 'max': respawn_config}
                    
                    # Default se não configurado
                    return {'min': 300, 'max': 600}
        
        return {'min': 300, 'max': 600}  # Default: 5-10 minutos

