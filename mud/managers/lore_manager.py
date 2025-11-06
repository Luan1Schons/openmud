"""
Gerenciador de lore modularizado por mundo
"""

import json
from pathlib import Path
from typing import Dict, Optional

class LoreManager:
    """Gerencia carregamento de lore de salas, monstros e NPCs"""
    
    def __init__(self, worlds_dir: str = "worlds"):
        self.worlds_dir = Path(worlds_dir)
        self.lore_cache: Dict[str, Dict] = {}
        self._load_all_lore()
    
    def _load_all_lore(self):
        """Carrega toda a lore de todos os mundos"""
        for world_dir in self.worlds_dir.iterdir():
            if world_dir.is_dir() and (world_dir / "lore").exists():
                world_id = world_dir.name
                self.lore_cache[world_id] = self._load_world_lore(world_id)
    
    def _load_world_lore(self, world_id: str) -> Dict:
        """Carrega lore de um mundo específico"""
        world_lore_dir = self.worlds_dir / world_id / "lore"
        
        if not world_lore_dir.exists():
            return {
                'rooms': {},
                'monsters': {},
                'npcs': {}
            }
        
        lore = {
            'rooms': {},
            'monsters': {},
            'npcs': {}
        }
        
        # Carrega lore de salas
        rooms_dir = world_lore_dir / "rooms"
        if rooms_dir.exists():
            for room_file in rooms_dir.glob("*.json"):
                room_id = room_file.stem
                try:
                    with open(room_file, 'r', encoding='utf-8') as f:
                        lore['rooms'][room_id] = json.load(f)
                except Exception as e:
                    print(f"Erro ao carregar lore da sala {room_id}: {e}")
        
        # Carrega lore de monstros
        monsters_dir = world_lore_dir / "monsters"
        if monsters_dir.exists():
            for monster_file in monsters_dir.glob("*.json"):
                monster_id = monster_file.stem
                try:
                    with open(monster_file, 'r', encoding='utf-8') as f:
                        lore['monsters'][monster_id] = json.load(f)
                except Exception as e:
                    print(f"Erro ao carregar lore do monstro {monster_id}: {e}")
        
        # Carrega lore de NPCs
        npcs_dir = world_lore_dir / "npcs"
        if npcs_dir.exists():
            for npc_file in npcs_dir.glob("*.json"):
                npc_id = npc_file.stem
                try:
                    with open(npc_file, 'r', encoding='utf-8') as f:
                        lore['npcs'][npc_id] = json.load(f)
                except Exception as e:
                    print(f"Erro ao carregar lore do NPC {npc_id}: {e}")
        
        return lore
    
    def get_room_lore(self, world_id: str, room_id: str) -> Optional[Dict]:
        """Retorna lore de uma sala"""
        if world_id in self.lore_cache:
            return self.lore_cache[world_id]['rooms'].get(room_id)
        return None
    
    def get_monster_lore(self, world_id: str, monster_id: str) -> Optional[Dict]:
        """Retorna lore de um monstro"""
        if world_id in self.lore_cache:
            return self.lore_cache[world_id]['monsters'].get(monster_id)
        return None
    
    def get_npc_lore(self, world_id: str, npc_id: str) -> Optional[Dict]:
        """Retorna lore de um NPC"""
        if world_id in self.lore_cache:
            return self.lore_cache[world_id]['npcs'].get(npc_id)
        return None

